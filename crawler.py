# 爬取網站所需的package
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from urllib.parse import urlparse, parse_qs

# 從DB抓資料所需的package
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    insert,
    inspect,
    Column,
    Integer,
    String,
    Float,
    select,
    update,
    delete,
)
from modules.config.config import SQLALCHEMY_DATABASE_URI
from modules.config.info import (
    DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT,
    DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT,
    BOX_TITLE_FIELDER,
    BOX_TITLE_PITCHER,
)

# 定義db的連接
engine = create_engine(SQLALCHEMY_DATABASE_URI)
db = MetaData()


# 處理K9 column的資料
def update_K9(IP, K):
    integer = int(IP)
    decimal = IP - integer
    try:
        return (K * 9) / (integer + decimal * 10 * (3**-1))
    except ZeroDivisionError:
        return 0


class Crawler:
    def __init__(self):

        # 建立Options object
        # 並且啟用headless模式
        # 此模式的用途是讓selenium不需要模擬現實中開啟網頁的過程
        # 因為這個過程往往會耗費相當多的時間。
        self.options = Options()
        self.options.add_argument("--headless")

        # driver: 用來開啟主要頁面
        # second_driver: 用來開啟從主頁面進入的次要頁面
        self.driver = webdriver.Edge(
            service=Service("./msedgedriver"), options=self.options
        )
        self.second_driver = webdriver.Edge(
            service=Service("./msedgedriver", options=self.options)
        )

    def season(self):
        # 球員點將錄之URL
        player_webpage = "https://www.cpbl.com.tw/player"
        self.driver.get(player_webpage)

        def form_final_stats_dict(stats_dict, stats_elements, player_category):
            if player_category == "打擊成績":
                if stats_elements == "empty":
                    # 依序取出db內的column所需要的數據
                    for key, _ in DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["AVG", "OBP", "SLG", "OPS"]:
                            stats_dict[key] = float(0)
                        elif key == "IBB":
                            stats_dict[key] = 0
                        else:
                            stats_dict[key] = 0
                else:
                    # 依序取出db內的column所需要的數據
                    for key, value in DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["AVG", "OBP", "SLG", "OPS"]:
                            stats_dict[key] = float(stats_elements[value].text)
                        elif key == "IBB":
                            stats_dict[key] = int(stats_elements[value].text[1:-1])
                        else:
                            stats_dict[key] = int(stats_elements[value].text)
                return stats_dict, "Fielder"
            else:
                if stats_elements == "empty":
                    for key, _ in DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["IP", "ERA", "WHIP"]:
                            stats_dict[key] = float(0)
                        elif key == "SV+H":
                            stats_dict[key] = 0
                        else:
                            stats_dict[key] = 0
                    # 官網沒有，但此聯盟有比的項目
                    # 後面再處理
                    stats_dict["K/9"] = float(0)
                    stats_dict["QS"] = 0
                else:
                    for key, value in DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["IP", "ERA", "WHIP"]:
                            stats_dict[key] = float(stats_elements[value].text)
                        elif key == "SV+H":
                            stats_dict[key] = int(stats_elements[value[0]].text) + int(
                                stats_elements[value[1]].text
                            )
                        else:
                            stats_dict[key] = int(stats_elements[value].text)

                    # 官網沒有，但此聯盟有比的項目
                    # 後面再處理
                    stats_dict["K/9"] = update_K9(stats_dict["IP"], stats_dict["K"])
                    stats_dict["QS"] = 0
                return stats_dict, "Pitcher"

        def stats(href):
            """
            爬取球員數據
            """

            self.second_driver.get(href)
            print("Stats page loaded...")

            # 無論有無成績，都先抓取該球員的相片。
            p_b_element = self.second_driver.find_element(
                By.CLASS_NAME, "PlayerBrief"
            )  # p_b -> PlayerBrief

            # name
            # 因為名字、背號同時被包在<div class="name">標籤內
            # 所以直接取此標籤的text的話，會取出"名字背號(ex:王柏融9)"這樣的字串
            name_jersey = p_b_element.find_element(By.CLASS_NAME, "name").text
            jersey = p_b_element.find_element(By.CLASS_NAME, "number").text
            # 去除名字前面的特殊符號
            # #：註冊註銷
            # *：合約所屬球員
            # ◎：自主培訓、測試洋將
            if name_jersey[0] in "#*◎":
                name_jersey = name_jersey[1:]
            name = name_jersey.replace(jersey, "")

            # 利用網址列上的queryString取出player_id
            # 用於處理圖片的檔名、以及新增到db內的column
            url_info = urlparse(href)
            querystring = url_info.query
            query_params = parse_qs(querystring)
            player_id = query_params["acnt"]
            player_id = int(player_id[0])

            image_name = name + str(player_id)
            img_div_element = p_b_element.find_element(By.CLASS_NAME, "img")
            image = img_div_element.find_element(By.TAG_NAME, "span")
            image.screenshot("static/img/player/{}.png".format(image_name))
            print("{} 圖片下載完成...".format(image_name))
            print("-" * 20)

            # DistTitle為記錄不同種成績的區塊
            # 分別有打擊成績、投球成績、守備成績、對戰成績
            dt_elements = self.second_driver.find_elements(By.CLASS_NAME, "DistTitle")

            """
            每個球員爬取DistTitle這個class的tag時主要會分成三種：
            1. 2個DistTitle: 尚未在一軍有'對戰成績'的球員(ex:台鋼球員皆為此類)
            2. 3個DistTitle: 專職野手、投手的球員，大多數球員落在此類
            3. 4個DistTitle: 野手上丘投過球、投手上場打擊過的二刀流球員
            """
            # 用一個變數，區分該球員是否為二刀流
            twoway = True if len(dt_elements) == 4 else False

            # -------------------------------------------------------------------------------------
            # 先新增球員編號、名字、球隊這些個無論哪種球員都有的屬性到dict內
            stats_dict = {}
            stats_dict["player_id"] = player_id
            stats_dict["name"] = name

            # 處理球隊名稱的部分
            team = p_b_element.find_element(By.CLASS_NAME, "team").text
            # 把有些球員在資料卡中寫 -> "隊伍二軍"的二軍拿掉
            team = team.replace("二軍", "")
            stats_dict["team"] = team
            # -------------------------------------------------------------------------------------

            # 正常球員
            if not twoway:
                # 利用index取出第一個有紀錄成績的Table
                # 因為此處不是二刀流，所以
                # 打擊成績 -> 打者
                # 投球成績 -> 投手
                f_dt_element = dt_elements[0]  # f_dt_element = first DistTitle element

                # 取出該球員屬於野手 or 投手
                # 野手的dist_title[0]標籤文字為"打擊成績"
                # 投手的dist_title[0]標籤文字為"投球成績"
                player_category = f_dt_element.find_element(By.TAG_NAME, "h3").text

                # 和上面取DistTable類似的意思
                # 用find_element代表只會取第一個RecordTable
                # 亦即 打擊/投球 成績
                rt_element = self.second_driver.find_element(
                    By.CLASS_NAME, "RecordTable"
                )  # rt_element: RecordTable element

                # 接下來處理年份
                year_elements = rt_element.find_elements(By.CLASS_NAME, "year")
                # 取Total的上一個，代表最近一個球季的成績
                # 若沒有2023的成績，從原本直接return
                # 改成新增全部為0的數據。
                year = year_elements[-2].text
                if year != "2023":
                    stats_dict, table_name = form_final_stats_dict(
                        stats_dict, "empty", player_category
                    )
                else:
                    tr_elements = rt_element.find_elements(
                        By.TAG_NAME, "tr"
                    )  # tr_element = table row element

                    # 同樣取Total的上一個
                    tr_2023 = tr_elements[-2]
                    stats_elements = tr_2023.find_elements(By.CLASS_NAME, "num")

                    stats_dict, table_name = form_final_stats_dict(
                        stats_dict, stats_elements, player_category
                    )

                table = Table(table_name, db, autoload_with=engine)
                with engine.connect() as connection:
                    transaction = connection.begin()
                    try:
                        select_statement = select(table).where(
                            table.c.player_id == stats_dict["player_id"]
                        )
                        result = connection.execute(select_statement).fetchone()
                        if result:
                            statement = (
                                update(table)
                                .where(table.c.player_id == stats_dict["player_id"])
                                .values(stats_dict)
                            )
                        else:
                            statement = insert(table).values(stats_dict)
                        connection.execute(statement)
                        transaction.commit()
                    except:
                        transaction.rollback()
                        raise RuntimeError

                print("{} {} 新增完成...".format(team, name))
                print("-" * 20)
            # ------------------------------------------------------------------------------------
            # 二刀流球員
            else:
                # stats_dict for 打擊成績
                # extra_stats_dict for 投球成績
                extra_stats_dict = stats_dict.copy()

                rt_elements = self.second_driver.find_elements(
                    By.CLASS_NAME, "RecordTable"
                )  # rt_element: RecordTable element

                for i in range(2):
                    rt_element = rt_elements[i]
                    year_elements = rt_element.find_elements(By.CLASS_NAME, "year")
                    year = year_elements[-2].text

                    # 加入2023年沒有出賽成績的球員
                    if year != "2023":
                        if i == 0:
                            stats_dict, table_name = form_final_stats_dict(
                                stats_dict, "empty", "打擊成績"
                            )
                        else:
                            stats_dict, table_name = form_final_stats_dict(
                                extra_stats_dict, "empty", "投球成績"
                            )
                    # 2023有成績的球員
                    else:
                        tr_elements = rt_element.find_elements(
                            By.TAG_NAME, "tr"
                        )  # tr_element = table row element

                        tr_2023 = tr_elements[-2]
                        stats_elements = tr_2023.find_elements(By.CLASS_NAME, "num")
                        if i == 0:
                            stats_dict, table_name = form_final_stats_dict(
                                stats_dict, stats_elements, "打擊成績"
                            )
                        else:
                            stats_dict, table_name = form_final_stats_dict(
                                extra_stats_dict, stats_elements, "投球成績"
                            )

                    table = Table(table_name, db, autoload_with=engine)
                    with engine.connect() as connection:
                        transaction = connection.begin()
                        try:
                            select_statement = select(table).where(
                                table.c.player_id == stats_dict["player_id"]
                            )
                            result = connection.execute(select_statement).fetchone()
                            if result:
                                statement = (
                                    update(table)
                                    .where(table.c.player_id == stats_dict["player_id"])
                                    .values(stats_dict)
                                )
                            else:
                                statement = insert(table).values(stats_dict)
                            connection.execute(statement)
                            transaction.commit()
                        except:
                            transaction.rollback()
                            raise RuntimeError
                    print("{} {} 新增完成...".format(team, name))
                    print("-" * 20)

        # 尋找球員點將錄中，每個要點擊的連結
        # 先定位到"各個球團"
        player_list_elements = self.driver.find_elements(By.CLASS_NAME, "PlayersList")
        player_list_element = player_list_elements[1]
        # for player_list_element in player_list_elements:
        a_elements = player_list_element.find_elements(By.TAG_NAME, "a")
        # 接著再從各球團，定位到各個球員
        for i in range(len(a_elements)):
            print(i + 1)
            a_element = a_elements[i]
            href = a_element.get_attribute("href")
            stats(href)
        # 最後再關掉第二個driver
        self.second_driver.quit()

    def live(self):
        box_webpage = "https://www.cpbl.com.tw/box"
        self.driver.get(box_webpage)

        def stats():
            TodayFielder = Table("TodayFielder", db, autoload_with=engine)
            TodayPitcher = Table("TodayPitcher", db, autoload_with=engine)

            # 開爬前，先清除目前Table內的資料(前一次比賽日留下來的)
            with engine.begin() as connection:
                delete_stmt_fielder = delete(TodayFielder)
                delete_stmt_pitcher = delete(TodayPitcher)
                connection.execute(delete_stmt_fielder)
                connection.execute(delete_stmt_pitcher)

            # 利用標籤數量，決定當天共打了幾場比賽
            game_list = self.driver.find_element(By.CLASS_NAME, "game_list")
            number_of_games = len(game_list.find_elements(By.CLASS_NAME, "item"))

            # 以下判斷目前球賽的狀態
            # 並根據目前不同的狀態，設定不同變數(active, G1_active, G2_active, flag)
            # 的Bool值
            if number_of_games == 1:
                active = True
                try:
                    # 比賽分類總共有：
                    # 無分類：尚未開始，有game_status，但無span
                    # 有分類：
                    # 1.先發打序 有game_status，且有span
                    # 2.延賽 無game_status，是用game_note來顯示
                    # 3.比賽中 有game_status，且有span
                    # 4.保留 ??
                    # 5.比賽結束 有game_status，但比賽結束也有資料需要爬，會在後面用額外的條件設定active，所以這邊不處理
                    gameStatusElement = self.driver.find_element(
                        By.CLASS_NAME, "game_status"
                    )

                    try:
                        gameStatus = gameStatusElement.find_element(By.TAG_NAME, "span")
                        if gameStatus.get_attribute("innerHTMl") == "先發打序":
                            active = False
                    except NoSuchElementException:
                        # 有gameStatus但下面沒有span element -> 無分類，尚未開始
                        active = False

                except NoSuchElementException:
                    # 代表沒有game_status -> 延賽
                    active = False

            # 一天兩場
            else:
                # 利用兩場比賽的bar的網址屬性，檢查當前比賽的狀態
                games = self.driver.find_element(By.CLASS_NAME, "game_list")
                games = games.find_elements(By.CLASS_NAME, "item")
                G1, G2 = games[0], games[1]

                # 原始URL為 https://www.cpbl.com.tw/box
                # 取到的href會是 /box/index?gameSno=181&year=2023&kindCode=A 這種格式
                # 所以才從index 4開始取
                G1_link = G1.find_element(By.TAG_NAME, "a").get_attribute("href")
                G2_link = G2.find_element(By.TAG_NAME, "a").get_attribute("href")

                # 用來判斷兩場比賽是否正在進行中
                G1_active, G2_active = True, True

                # 用來判斷目前位於哪一場比賽
                # True: G1, False: G2
                flag = True

                # 用另一個方式判斷延賽的場次
                if "PresentStatus=0" in G1_link and "PresentStatus=0" in G2_link:
                    G1_active = False
                    G2_active = False

                elif "PresentStatus=0" in G1_link:
                    G1_active = False
                    # 判斷完G1延賽後，利用game_status判斷G2
                    # 下面同理

                    # 因為一場延賽，所以只有一個game_status，用find_element即可
                    G2gameStatusElement = self.driver.find_element(
                        By.CLASS_NAME, "game_status"
                    )
                    if (
                        G2gameStatusElement.find_element(
                            By.TAG_NAME, "span"
                        ).get_attribute("innerHTML")
                        == "先發打序"
                    ):
                        G2_active = False
                    flag = False

                elif "PresentStatus=0" in G2_link:
                    G2_active = False

                    G1gameStatusElement = self.driver.find_element(
                        By.CLASS_NAME, "game_status"
                    )
                    if (
                        G1gameStatusElement.find_element(
                            By.TAG_NAME, "span"
                        ).get_attribute("innerHTML")
                        == "先發打序"
                    ):
                        G1_active = False
                    flag = True

                # 兩場都有game_status了
                else:
                    gameStatusElements = self.driver.find_elements(
                        By.CLASS_NAME, "game_status"
                    )
                    G1gameStatusElement, G2gameStatusElement = (
                        gameStatusElements[0],
                        gameStatusElements[1],
                    )
                    G1gameStatus = G1gameStatusElement.find_element(
                        By.TAG_NAME, "span"
                    ).get_attribute("innerHTML")
                    G2gameStatus = G2gameStatusElement.find_element(
                        By.TAG_NAME, "span"
                    ).get_attribute("innerHTML")

                    if G1gameStatus == "先發打序" and G2gameStatus == "先發打序":
                        G1_active, G2_active = False, False
                    elif G1gameStatus == "先發打序":
                        G1_active = False
                    elif G2gameStatus == "先發打序":
                        G2_active = False

            while True:
                # 依據前面設定的狀態
                # 決定目前要爬取哪一個頁面的成績
                if number_of_games == 1:
                    # 比賽尚未進行中
                    if not active:
                        print("Game Postponed or hasn't Started or Finished.")
                        break
                else:
                    if G1_active or G2_active:
                        if flag:
                            print(G1_link)
                            self.driver.get(G1_link)
                            print("Start Crawling G1.")
                        else:
                            print(G2_link)
                            self.driver.get(G2_link)
                            print("Start Crawling G2.")

                    else:
                        print("Both Games not Started or Finished.")
                        break

                # 已經決定好要爬取哪一個頁面的成績了
                record_tables = self.driver.find_elements(By.CLASS_NAME, "RecordTable")

                # 要取的是打擊成績這張表，而不是最上面的戰況表
                # 寫在左邊的代表是網頁左手邊那一對的成績表、右邊則是右手邊
                fielder_tables = [record_tables[1]] + [record_tables[4]]
                pitcher_tables = [record_tables[2]] + [record_tables[5]]

                for fielder_table in fielder_tables:
                    rows = fielder_table.find_elements(By.TAG_NAME, "tr")[1:-1]

                    for row in rows:
                        fielder_stats = {
                            "player_id": int(
                                row.find_element(By.TAG_NAME, "a").get_attribute(
                                    "href"
                                )[-4:]
                            ),
                            "name": row.find_element(By.TAG_NAME, "a").get_attribute(
                                "innerHTML"
                            ),
                        }
                        nums = row.find_elements(By.CLASS_NAME, "num")[:16]
                        for i in range(len(BOX_TITLE_FIELDER)):
                            if i == 9:
                                fielder_stats[BOX_TITLE_FIELDER[i]] = int(
                                    nums[i].get_attribute("innerHTML")[1:-1]
                                )
                            else:
                                fielder_stats[BOX_TITLE_FIELDER[i]] = int(
                                    nums[i].get_attribute("innerHTML")
                                )
                        fielder_stats["TB"] = (
                            fielder_stats["H"]
                            + fielder_stats["2H"] * 1
                            + fielder_stats["3H"] * 2
                            + fielder_stats["HR"] * 3
                        )
                        try:
                            fielder_stats["AVG"] = (
                                fielder_stats["H"] / fielder_stats["AB"]
                            )
                            fielder_stats["SLG"] = (
                                fielder_stats["TB"] / fielder_stats["AB"]
                            )
                        except ZeroDivisionError:
                            fielder_stats["AVG"] = 0
                            fielder_stats["SLG"] = 0

                        try:
                            fielder_stats["OBP"] = (
                                fielder_stats["H"]
                                + fielder_stats["BB"]
                                + fielder_stats["IBB"]
                                + fielder_stats["HBP"]
                            ) / (
                                fielder_stats["AB"]
                                + fielder_stats["BB"]
                                + fielder_stats["IBB"]
                                + fielder_stats["HBP"]
                                + fielder_stats["SF"]
                            )
                        except ZeroDivisionError:
                            fielder_stats["OBP"] = 0

                        fielder_stats["OPS"] = (
                            fielder_stats["OBP"] + fielder_stats["SLG"]
                        )
                        fielder_stats["PA"] = (
                            fielder_stats["AB"]
                            + fielder_stats["BB"]
                            + fielder_stats["IBB"]
                            + fielder_stats["HBP"]
                            + fielder_stats["SF"]
                            + fielder_stats["BUNT"]
                        )

                        with engine.begin() as connection:
                            query = select(TodayFielder).where(
                                TodayFielder.c.player_id == fielder_stats["player_id"]
                            )
                            result = connection.execute(query)
                            player = result.fetchone()

                            if player:
                                update_query = (
                                    update(TodayFielder)
                                    .where(
                                        TodayFielder.c.player_id
                                        == fielder_stats["player_id"]
                                    )
                                    .values(fielder_stats)
                                )
                                connection.execute(update_query)
                            else:
                                connection.execute(
                                    TodayFielder.insert(), [fielder_stats]
                                )

                print("Fielders Data updated.")

                """這邊要切換tab，也就是模擬點選另一隻球隊的Tab的原因是
                打者不需要切換tab，就可以從當前的隊伍成績頁面，取到另一個隊伍的打擊成績(利用innerHTML)
                但投手在沒有切換的情形下，用當前的隊伍成績頁面，取另一個隊伍的投手成績時，innerHTML會是空字串
                要切換隊伍的tab之後，投手成績的innerHTML才會有資料。"""
                table_index = 0
                while table_index < 2:
                    if table_index == 1:
                        tabs = self.driver.find_element(By.CLASS_NAME, "tabs")
                        a = tabs.find_elements(By.TAG_NAME, "a")
                        a[1].click()
                    # 按下tab切換完隊伍後，後續的操作就相同了。
                    rows = pitcher_tables[table_index].find_elements(By.TAG_NAME, "tr")[
                        1:-1
                    ]

                    for row in rows:
                        # 用split的原因，投手成績的投手名稱上
                        # 可能會隨著比賽中或比賽結束時
                        # 寫上額外的訊息
                        # ex: 蘭道爾 (W,5-2) or 李其峰 (H,9)
                        # 因此這邊用split來只取名字
                        innerText_split = (
                            row.find_element(By.TAG_NAME, "a")
                            .get_attribute("innerText")
                            .split(" ")
                        )
                        pitcher_stats = {
                            "player_id": int(
                                row.find_element(By.TAG_NAME, "a").get_attribute(
                                    "href"
                                )[-4:]
                            ),
                            "name": innerText_split[0],
                        }

                        # 先初始化這些沒辦法在比賽進行時爬到的stats
                        # 後面會利用比賽完時，innerText後面的紀錄，來增加這些stats的值
                        pitcher_stats["W"] = 0
                        pitcher_stats["L"] = 0
                        pitcher_stats["HLD"] = 0
                        pitcher_stats["SV"] = 0
                        pitcher_stats["SV_H"] = 0
                        pitcher_stats["BSV"] = 0

                        # 比賽完時，官網才會加上紀錄在名字後面
                        # 讓innerText_split長度變成2
                        if len(innerText_split) > 1:
                            # 格式為 '(W,1-0)'
                            # 因此取index 1的字元
                            # 官網目前的紀錄方式好像都是一個字元(W, L, H, S)
                            # 所以應該不會發生問題
                            if innerText_split[1][1] == "W":
                                pitcher_stats["W"] = 1
                            elif innerText_split[1][1] == "L":
                                pitcher_stats["L"] = 1
                            elif innerText_split[1][1] == "H":
                                pitcher_stats["HLD"] = 1
                                pitcher_stats["SV_H"] = 1
                            elif innerText_split[1][1] == "S":
                                pitcher_stats["SV"] = 1
                                pitcher_stats["SV_H"] = 1

                            # 因為會有這些紀錄，表示比賽已經結束了
                            # 所以要更新active的值

                            # 還有另外一個狀況是H不一定在比賽後才加上去
                            # 聯盟會在比賽進行中時就把H加上去
                            # 導致跑到一個選手有H時，就把active設成False
                            # 所以這邊加上另一個條件是遇到勝投時才設定狀態
                            # 因為有勝投出現，代表比賽一定結束了

                            # 例外狀況：和局呢？
                            if innerText_split[1][1] == "W":
                                if number_of_games == 1:
                                    active = False
                                else:
                                    if flag:
                                        G1_active = False
                                    else:
                                        G2_active = False

                        # 剩餘能爬的stats
                        nums = row.find_elements(By.CLASS_NAME, "num")
                        nums = [nums[0]] + nums[4:7] + nums[8:10] + nums[12:14]
                        for i in range(len(nums)):
                            if i == 0:
                                # 投手改用innerHTML
                                # 因為官網的innerText是一個空的字串，innerHTML才會顯示對的數據
                                # 感覺是寫的人沒有寫好，因為打者是抓得到的，只有投手沒辦法。
                                integer = int(
                                    nums[i]
                                    .find_element(By.CLASS_NAME, "integer")
                                    .get_attribute("innerHTML")
                                )
                                decimal = (
                                    nums[i]
                                    .find_element(By.CLASS_NAME, "fraction")
                                    .get_attribute("innerHTML")
                                )
                                if decimal == "1/3":
                                    decimal = 0.1
                                elif decimal == "2/3":
                                    decimal = 0.2
                                else:
                                    decimal = 0
                                pitcher_stats[BOX_TITLE_PITCHER[i]] = integer + decimal
                            else:
                                pitcher_stats[BOX_TITLE_PITCHER[i]] = int(
                                    nums[i].get_attribute("innerHTML")
                                )
                        try:
                            pitcher_stats["ERA"] = (pitcher_stats["ER"] * 9) / (
                                integer + decimal * 10 * 3**-1
                            )
                            pitcher_stats["WHIP"] = (
                                pitcher_stats["H"] + pitcher_stats["BB"]
                            ) / (integer + decimal * 10 * 3**-1)
                            pitcher_stats["K9"] = (
                                pitcher_stats["K"]
                                * 9
                                / (integer + decimal * 10 * 3**-1)
                            )
                        except ZeroDivisionError:
                            if pitcher_stats["ER"] > 0:
                                pitcher_stats["ERA"] = 9999
                            else:
                                pitcher_stats["ERA"] = 0

                            if pitcher_stats["H"] + pitcher_stats["BB"] > 0:
                                pitcher_stats["WHIP"] = 9999
                            else:
                                pitcher_stats["WHIP"] = 0

                            pitcher_stats["K9"] = 0

                        if integer >= 6 and pitcher_stats["ER"] <= 3:
                            pitcher_stats["QS"] = 1
                        else:
                            pitcher_stats["QS"] = 0

                        with engine.begin() as connection:
                            query = select(TodayPitcher).where(
                                TodayPitcher.c.player_id == pitcher_stats["player_id"]
                            )
                            result = connection.execute(query)
                            player = result.fetchone()

                            if player:
                                update_query = (
                                    update(TodayPitcher)
                                    .where(
                                        TodayPitcher.c.player_id
                                        == pitcher_stats["player_id"]
                                    )
                                    .values(pitcher_stats)
                                )
                                connection.execute(update_query)
                            else:
                                connection.execute(
                                    TodayPitcher.insert(), [pitcher_stats]
                                )
                    table_index += 1
                print("Pitchers Data updated.")
                print("-")
                # 在只有一場比賽的情況下，每次爬完會在第二個隊伍的tab上
                # 所以要在最後改回第一個tab，讓重新爬取時，爬到的投手名稱不會是空的
                if number_of_games == 1:
                    a[0].click()
                else:
                    if flag:
                        if G2_active:
                            flag = False
                    else:
                        if G1_active:
                            flag = True
                time.sleep(30)

        inspector = inspect(engine)
        existed_tables = inspector.get_table_names()
        if "TodayFielder" not in existed_tables:
            columns = [
                Column("db_id", Integer, primary_key=True),
                Column("player_id", Integer),
                Column("name", String(255)),
                Column("PA", Integer),
                Column("AB", Integer),
                Column("R", Integer),
                Column("RBI", Integer),
                Column("H", Integer),
                Column("2H", Integer),
                Column("3H", Integer),
                Column("HR", Integer),
                Column("TB", Integer),
                Column("DP", Integer),
                Column("BB", Integer),
                Column("IBB", Integer),
                Column("HBP", Integer),
                Column("K", Integer),
                Column("SF", Integer),
                Column("BUNT", Integer),
                Column("SB", Integer),
                Column("CS", Integer),
                Column("AVG", Float),
                Column("OBP", Float),
                Column("SLG", Float),
                Column("OPS", Float),
            ]
            table = Table("TodayFielder", db, *columns)
            db.create_all(engine, [table])
        if "TodayPitcher" not in existed_tables:
            columns = [
                Column("db_id", Integer, primary_key=True),
                Column("player_id", Integer),
                Column("name", String(255)),
                Column("IP", Float),
                Column("W", Integer),
                Column("L", Integer),
                Column("H", Integer),
                Column("HR", Integer),
                Column("BB", Integer),
                Column("HBP", Integer),
                Column("K", Integer),
                Column("R", Integer),
                Column("ER", Integer),
                Column("ERA", Float),
                Column("WHIP", Float),
                Column("K9", Float),
                Column("QS", Integer),
                Column("HLD", Integer),
                Column("SV", Integer),
                Column("SV_H", Integer),
                Column("BSV", Integer),
            ]

            table = Table("TodayPitcher", db, *columns)
            db.create_all(engine, [table])
        stats()


if __name__ == "__main__":
    crawler = Crawler()
    crawler.season()
    # crawler.live()
