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


# 爬取球員目前的整季成績
# 到Fielder, Pitcher Table
def load():
    """
    從球員點將錄中前往各個球員的頁面
    並且爬取該球員的成績
    """

    # 球員點將錄之URL
    player_webpage_url = "https://www.cpbl.com.tw/player"

    # 使用Selenium模擬使用者的動作

    # 建立Options object
    # 並且啟用headless模式
    # 此模式的用途是讓selenium不需要模擬現實中開啟網頁的過程
    # 因為這個過程往往會耗費相當多的時間。
    options = Options()
    options.add_argument("--headless")

    # 參數設定：新增要用來模擬的driver
    # driver1: 開啟球員點將錄
    driver1 = webdriver.Edge(service=Service("./msedgedriver"), options=options)
    driver1.get(player_webpage_url)
    print("Players page loaded...")

    # 爬取player stats
    def crawl_stats(driver, href):
        """
        爬取球員數據
        """

        driver.get(href)
        print("Stats page loaded...")
        dt_elements = driver.find_elements(By.CLASS_NAME, "DistTitle")

        """
        每個球員爬取DistTitle這個class的tag時主要會分成三種：
        1. 2個DistTitle: 尚未在一軍有'對戰成績'的球員(ex:台鋼球員皆為此類)
        2. 3個DistTitle: 專職野手、投手的球員，大多數球員落在此類
        3. 4個DistTitle: 野手上丘投過球、投手上場打擊過的二刀流球員
        """
        recorded = True if len(dt_elements) > 2 else False
        twoway = True if len(dt_elements) == 4 else False
        # 尚未在一軍有成績就跳過此球員，不加到db內
        if not recorded:
            driver.close()
            return
        # -------------------------------------------------------------------------------------
        # 先新增球員編號、名字這2個無論哪種球員都有的屬性到dict內
        stats_dict = {}

        # 取出要加入到table內的column
        # player_id

        url_info = urlparse(href)
        querystring = url_info.query
        query_params = parse_qs(querystring)
        player_id = query_params["acnt"]
        player_id = int(player_id[0])
        stats_dict["player_id"] = player_id

        # name
        # 因為名字、背號同時被包在<div class="name">標籤內
        # 所以直接取此標籤的text的話，會取出"名字背號(ex:王柏融9)"這樣的字串
        # 因此需要做額外的處理

        name_element = driver.find_element(By.CLASS_NAME, "name")
        number_element = name_element.find_element(By.CLASS_NAME, "number")
        name_text = name_element.text
        number_text = number_element.text
        name = name_text.replace(number_text, "")
        stats_dict["name"] = name

        # -------------------------------------------------------------------------------------

        if not twoway:
            # Player stats
            f_dt_element = dt_elements[0]  # f_dt_element = first DistTitle element

            # 先判斷該球員2023有沒有成績
            rt_element = driver.find_element(
                By.CLASS_NAME, "RecordTable"
            )  # rt_element: RecordTable element
            year_elements = rt_element.find_elements(By.CLASS_NAME, "year")

            # 取Total的上一個，代表最近一個球季(含2023)的成績
            year = year_elements[-2].text
            if year != "2023":
                return

            tr_elements = rt_element.find_elements(
                By.TAG_NAME, "tr"
            )  # tr_element = table row element

            # 同樣取Total的上一個
            tr_2023 = tr_elements[-2]
            stats_elements = tr_2023.find_elements(By.CLASS_NAME, "num")

            # 取出該球員屬於野手 or 投手
            player_category = f_dt_element.find_element(By.TAG_NAME, "h3").text

            # 野手的dist_title[0]標籤文字為"打擊成績"
            # 投手的dist_title[0]標籤文字為"投球成績"
            if player_category == "打擊成績":
                # 取出該球員所屬的球隊
                team = rt_element.find_elements(By.CLASS_NAME, "team")[-2].text
                stats_dict["team"] = team

                # 依序取出db內的column所需要的數據
                for key, value in DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT.items():
                    if key in ["AVG", "OBP", "SLG", "OPS"]:
                        stats_dict[key] = float(stats_elements[value].text)
                    elif key == "IBB":
                        stats_dict[key] = int(stats_elements[value].text[1:-1])
                    else:
                        stats_dict[key] = int(stats_elements[value].text)

                table_name = "Fielder"

            elif player_category == "投球成績":
                team = rt_element.find_elements(By.CLASS_NAME, "team")[-2].text
                stats_dict["team"] = team

                for key, value in DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT.items():
                    if key in ["IP", "ERA", "WHIP"]:
                        stats_dict[key] = float(stats_elements[value].text)
                    elif key == "SV+H":
                        stats_dict[key] = int(stats_elements[value[0]].text) + int(
                            stats_elements[value[1]].text
                        )
                    else:
                        stats_dict[key] = int(stats_elements[value].text)

                stats_dict["K/9"] = update_K9(stats_dict["IP"], stats_dict["K"])
                stats_dict["QS"] = 0

                table_name = "Pitcher"

            table = Table(table_name, db, autoload_with=engine)

            with engine.begin() as connection:
                insert_statement = insert(table).values(stats_dict)
                connection.execute(insert_statement)

            print("{} {} 新增完成...".format(team, name))
            print("-" * 20)
        # ------------------------------------------------------------------------------------
        # 二刀流球員
        if twoway:
            extra_stats_dict = stats_dict.copy()

            rt_elements = driver.find_elements(
                By.CLASS_NAME, "RecordTable"
            )  # rt_element: RecordTable element

            for i in range(2):
                rt_element = rt_elements[i]
                year_elements = rt_element.find_elements(By.CLASS_NAME, "year")

                year = year_elements[-2].text
                if year != "2023":
                    recorded = False
                    continue
                else:
                    recorded = True

                tr_elements = rt_element.find_elements(
                    By.TAG_NAME, "tr"
                )  # tr_element = table row element

                tr_2023 = tr_elements[-2]
                stats_elements = tr_2023.find_elements(By.CLASS_NAME, "num")

                if i == 0:
                    # 取出該球員所屬的球隊
                    team = rt_element.find_elements(By.CLASS_NAME, "team")[-2].text
                    stats_dict["team"] = team

                    for key, value in DB_FIELDER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["AVG", "OBP", "SLG", "OPS"]:
                            stats_dict[key] = float(stats_elements[value].text)
                        elif key == "IBB":
                            stats_dict[key] = int(stats_elements[value].text[1:-1])
                        else:
                            stats_dict[key] = int(stats_elements[value].text)

                    table = Table("Fielder", db, autoload_with=engine)
                    with engine.begin() as connection:
                        insert_statement = insert(table).values(stats_dict)
                        connection.execute(insert_statement)
                else:
                    # 取出該球員所屬的球隊
                    team = rt_element.find_elements(By.CLASS_NAME, "team")[-2].text
                    extra_stats_dict["team"] = team

                    for key, value in DB_PITCHER_CATEGORIES_TO_WEB_STATS_DICT.items():
                        if key in ["IP", "ERA", "WHIP"]:
                            extra_stats_dict[key] = float(stats_elements[value].text)
                        elif key == "SV+H":
                            extra_stats_dict[key] = int(
                                stats_elements[value[0]].text
                            ) + int(stats_elements[value[1]].text)
                        else:
                            extra_stats_dict[key] = int(stats_elements[value].text)

                    extra_stats_dict["K/9"] = update_K9(
                        extra_stats_dict["IP"], extra_stats_dict["K"]
                    )
                    extra_stats_dict["QS"] = 0

                    table = Table("Pitcher", db, autoload_with=engine)
                    with engine.begin() as connection:
                        insert_statement = insert(table).values(extra_stats_dict)
                        connection.execute(insert_statement)

                if recorded:
                    print("{} {} 新增完成...".format(team, name))
                    print("-" * 20)
        driver.quit()

    # 爬取player image
    def crawl_image(href, driver):
        driver.get(href)
        print("Stats page loaded...")
        p_b_element = driver.find_element(
            By.CLASS_NAME, "PlayerBrief"
        )  # p_b -> PlayerBrief
        name_number = p_b_element.find_element(By.CLASS_NAME, "name").text
        img_div_element = driver.find_element(By.CLASS_NAME, "img")
        image = img_div_element.find_element(By.TAG_NAME, "span")
        image.screenshot("static/img/player/{}.png".format(name_number))
        driver.quit()
        print("{} 圖片下載完成...".format(name_number))
        print("-" * 20)

    # -------------------------------------------------------------------------------------
    # 透過selenium尋找要點擊的連結
    player_list_elements = driver1.find_elements(By.CLASS_NAME, "PlayersList")
    player_list_elements = player_list_elements[4:]

    for player_list_element in player_list_elements:
        a_elements = player_list_element.find_elements(By.TAG_NAME, "a")
        for i in range(len(a_elements)):
            print(i + 1)
            a_element = a_elements[i]
            href = a_element.get_attribute("href")
            # driver2: 開啟每個球員的成績頁面
            driver2 = webdriver.Edge(service=Service("./msedgedriver"), options=options)
            # crawl_image(href, driver2)
            crawl_stats(driver2, href)


# 爬取成績看板中，今日比賽中的球員成績
def crawl_live():
    def crawl():
        TodayFielder = Table("TodayFielder", db, autoload_with=engine)
        TodayPitcher = Table("TodayPitcher", db, autoload_with=engine)

        # 開爬前，先清除目前Table內的資料(前一次比賽日留下來的)
        with engine.begin() as connection:
            delete_stmt_fielder = delete(TodayFielder)
            delete_stmt_pitcher = delete(TodayPitcher)
            connection.execute(delete_stmt_fielder)
            connection.execute(delete_stmt_pitcher)

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Edge(service=Service("./msedgedriver"), options=options)

        # 先前往成績看板頁面，該頁面會直接列出今天的比賽。
        driver.get("https://www.cpbl.com.tw/box")
        game_list = driver.find_element(By.CLASS_NAME, "game_list")
        number_of_games = len(game_list.find_elements(By.CLASS_NAME, "item"))

        # 根據進入成績看板後的不同情形
        # 一天一場
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
                gameStatusElement = driver.find_element(By.CLASS_NAME, "game_status")

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
            games = driver.find_element(By.CLASS_NAME, "game_list")
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
                G2gameStatusElement = driver.find_element(By.CLASS_NAME, "game_status")
                if (
                    G2gameStatusElement.find_element(By.TAG_NAME, "span").get_attribute(
                        "innerHTML"
                    )
                    == "先發打序"
                ):
                    G2_active = False
                flag = False

            elif "PresentStatus=0" in G2_link:
                G2_active = False

                G1gameStatusElement = driver.find_element(By.CLASS_NAME, "game_status")
                if (
                    G1gameStatusElement.find_element(By.TAG_NAME, "span").get_attribute(
                        "innerHTML"
                    )
                    == "先發打序"
                ):
                    G1_active = False
                flag = True

            # 兩場都有game_status了
            else:
                gameStatusElements = driver.find_elements(By.CLASS_NAME, "game_status")
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
            if number_of_games == 1:
                # 比賽尚未進行中
                if not active:
                    print("Game Postponed or hasn't Started or Finished.")
                    break
            else:
                if G1_active or G2_active:
                    if flag:
                        print(G1_link)
                        driver.get(G1_link)
                        print("Start Crawling G1.")
                    else:
                        print(G2_link)
                        driver.get(G2_link)
                        print("Start Crawling G2.")

                else:
                    print("Both Games not Started or Finished.")
                    break

            # 抓取資料
            record_tables = driver.find_elements(By.CLASS_NAME, "RecordTable")
            fielder_tables = [record_tables[1]] + [record_tables[4]]
            pitcher_tables = [record_tables[2]] + [record_tables[5]]

            for fielder_table in fielder_tables:
                rows = fielder_table.find_elements(By.TAG_NAME, "tr")[1:-1]

                for row in rows:
                    fielder_stats = {
                        "player_id": int(
                            row.find_element(By.TAG_NAME, "a").get_attribute("href")[
                                -4:
                            ]
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
                        fielder_stats["AVG"] = fielder_stats["H"] / fielder_stats["AB"]
                        fielder_stats["SLG"] = fielder_stats["TB"] / fielder_stats["AB"]
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

                    fielder_stats["OPS"] = fielder_stats["OBP"] + fielder_stats["SLG"]
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
                            connection.execute(TodayFielder.insert(), [fielder_stats])

            print("Fielders Data updated.")

            """這邊要切換tab，也就是模擬點選另一隻球隊的Tab的原因是
            打者不需要切換tab，就可以從當前的隊伍成績頁面，取到另一個隊伍的打擊成績(利用innerHTML)
            但投手在沒有切換的情形下，用當前的隊伍成績頁面，取另一個隊伍的投手成績時，innerHTML會是空字串
            要切換隊伍的tab之後，投手成績的innerHTML才會有資料。"""
            table_index = 0
            while table_index < 2:
                if table_index == 1:
                    tabs = driver.find_element(By.CLASS_NAME, "tabs")
                    a = tabs.find_elements(By.TAG_NAME, "a")
                    a[1].click()
                # 按下tab切換完隊伍後，後續的操作就相同了。
                rows = pitcher_tables[table_index].find_elements(By.TAG_NAME, "tr")[
                    1:-1
                ]

                for row in rows:
                    innerText_split = (
                        row.find_element(By.TAG_NAME, "a")
                        .get_attribute("innerText")
                        .split(" ")
                    )
                    pitcher_stats = {
                        "player_id": int(
                            row.find_element(By.TAG_NAME, "a").get_attribute("href")[
                                -4:
                            ]
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
                            pitcher_stats["K"] * 9 / (integer + decimal * 10 * 3**-1)
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
                            connection.execute(TodayPitcher.insert(), [pitcher_stats])
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

    crawl()


if __name__ == "__main__":
    # load()
    crawl_live()
