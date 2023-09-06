# 2023.9.6
# 撰寫所有在header上功能頁面之外的其餘頁面的script
# 包括home, login, register, forget, manager, myleague, toadyupdate

from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    render_template,
    request,
    jsonify,
)
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Float,
    inspect,
    select,
    update,
    insert,
    delete,
)
from werkzeug.security import generate_password_hash, check_password_hash
from .config.info import *
from .common import *

otherBP = Blueprint("other", __name__)


# 首頁
@otherBP.route("/home")
def home():
    if "id" in session:
        return redirect(url_for("other.myleague", id=session["id"]))
    return render_template("home.html")


# 登入頁面
@otherBP.route("/login", methods=["GET", "POST"])
def login():
    def login_check(account, password):
        query = db.session.query(Account).filter(Account.account == account).first()
        # 帳號不存在
        if not query:
            return False

        # 確認密碼正確與否
        if check_password_hash(query.password, password):
            return True
        else:
            return False

    if request.method == "POST":
        received = request.get_json()
        account = received["account"]
        password = received["password"]

        if login_check(account, password):
            # 根據帳號不同，決定要重定向到哪個路由
            if account == "admin":
                return jsonify(
                    {
                        "redirect": url_for("other.manager"),
                        "success": True,
                        "admin": True,
                    }
                )
            else:
                id = (
                    db.session.query(Account)
                    .filter(Account.account == account)
                    .first()
                    .id
                )
                session["id"] = id

                return jsonify(
                    {
                        "redirect": "/league_home",
                        "id": id,
                        "success": True,
                        "admin": False,
                    }
                )
        else:
            return jsonify({"redirect": url_for("other.login"), "success": False})
    # 在URL輸入login時，導引到首頁
    else:
        return render_template("login.html")


# 註冊頁面
@otherBP.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        received = request.form
        account = received["account"]
        password = received["password"]

        query = db.session.query(Account).filter(Account.account == account).first()
        if query:
            return render_template("register.html", message="此帳號已存在！")
        else:
            if "team" not in received:
                # 一開始新增帳號是不會馬上新增對手
                # 之後手動更新或是另外用一個演算法
                # 更新每一週對手的更動
                new_account = Account(
                    account, generate_password_hash(password, "sha256"), None, "TBD"
                )
            else:
                new_account = Account(
                    account,
                    generate_password_hash(password, "sha256"),
                    received["team"],
                    "TBD",
                )
            db.session.add(new_account)
            db.session.commit()
            return redirect(url_for("other.home"))

    return render_template("register.html")


# 忘記密碼頁面
@otherBP.route("/forget", methods=["GET", "POST"])
def forget():
    pass


# 聯盟管理者頁面
@otherBP.route("/manager", methods=["GET", "POST"])
def manager():
    if request.method == "POST":
        if request.form.get("confirm", False):
            # ------------------------------------------------------------------
            # 定義Fielder, Pitcher這兩個Table

            # Fielder
            fielder_columns = [
                # 這邊都是sqlalchemy的Core功能
                # 所提供的class
                # 與利用 db = SQLAlchemy()中
                # db.Column不同
                Column("db_id", Integer, primary_key=True),
                Column("player_id", Integer),
                Column("name", String(255)),
                Column("team", String(255)),
                Column("PA", Integer),
                Column("AB", Integer),
                Column("RBI", Integer),
                Column("R", Integer),
                Column("H", Integer),
                Column("1H", Integer),
                Column("2H", Integer),
                Column("3H", Integer),
                Column("HR", Integer),
                Column("TB", Integer),
                Column("K", Integer),
                Column("SB", Integer),
                Column("OBP", Float),
                Column("SLG", Float),
                Column("AVG", Float),
                Column("DP", Integer),
                Column("BUNT", Integer),
                Column("SF", Integer),
                Column("BB", Integer),
                Column("IBB", Integer),
                Column("HBP", Integer),
                Column("CS", Integer),
                Column("OPS", Float),
                Column("Account", String(255), nullable=True),
                Column("position", String(255), nullable=True),
                Column("round", Integer, nullable=True),
            ]

            fielder = Table("Fielder", metadata, *fielder_columns)
            # Pitcher
            pitcher_columns = [
                Column("db_id", Integer, primary_key=True),
                Column("player_id", Integer),
                Column("name", String(255)),
                Column("team", String(255)),
                Column("APP", Integer),
                Column("W", Integer),
                Column("L", Integer),
                Column("SV", Integer),
                Column("BSV", Integer),
                Column("HLD", Integer),
                Column("SV+H", Integer),
                Column("IP", Float),
                Column("WHIP", Float),
                Column("ERA", Float),
                Column("H", Integer),
                Column("HR", Integer),
                Column("BB", Integer),
                Column("HBP", Integer),
                Column("K", Integer),
                Column("R", Integer),
                Column("ER", Integer),
                Column("K/9", Float),
                Column("QS", Integer),
                Column("Account", String(255), nullable=True),
                Column("position", String(255), nullable=True),
                Column("round", Integer, nullable=True),
            ]

            pitcher = Table("Pitcher", metadata, *pitcher_columns)
            # ------------------------------------------------------------------
            # 與db建立連線後
            # 將定義好的Fielder, Pitcher Table加入db內
            metadata.create_all(engine, [fielder, pitcher])

            # 取出管理員選擇的Fielder, Pitcher比項
            fielder_categories = request.form.getlist("Batting")
            pitcher_categories = request.form.getlist("Pitching")

            # 把選擇的比項寫成一個檔案
            # 以便之後讀取的時候直接讀檔案就好
            path = "categories.txt"
            with open(path, "w") as file:
                file.write("Fielders\n")
                file.writelines(
                    [fielder_stat + "\n" for fielder_stat in fielder_categories]
                )
                file.write("-\n")
                file.write("Pitchers\n")
                file.write("IP\n")
                file.writelines(
                    [pitcher_stat + "\n" for pitcher_stat in pitcher_categories]
                )
            return render_template("manager.html", message="設定完成！")
    return render_template("manager.html")


# 聯盟首頁
@otherBP.route("/league_home/<int:id>", methods=["GET", "POST"])
def myleague(id):
    # 目前的方法透過在URL切換不同的id就可以切換不同帳號
    # 實務上在登入後建立session來存，檢查session內有無此網頁中保存的資料
    # 有的話代表登入過，確認是本人
    # 沒有的話就不能這樣透過URL輸入id來進入此網頁
    if "id" not in session:
        return redirect(url_for("other.login"))
    query = db.session.query(Account).filter(Account.id == id).first()
    account = query.account
    team = query.team
    return render_template("myleague.html", account=account, team=team)


# 把今日成績加入本週成績、球季成績
@otherBP.route("/todayupdate", methods=["GET", "POST"])
def todayupdate():
    # ==================
    # 調整不能直接相加的比項
    # ==================
    def adjustUnadditive(type, processDict, shouldRound, isWeekly):
        if type == "Fielders":
            try:
                processDict["AVG"] = processDict["H"] / processDict["AB"]
                processDict["SLG"] = processDict["TB"] / processDict["AB"]
            except ZeroDivisionError:
                processDict["AVG"] = 0
                processDict["SLG"] = 0
            try:
                processDict["OBP"] = (
                    processDict["H"]
                    + processDict["BB"]
                    + processDict["IBB"]
                    + processDict["HBP"]
                ) / (
                    processDict["AB"]
                    + processDict["BB"]
                    + processDict["IBB"]
                    + processDict["HBP"]
                    + processDict["SF"]
                )
            except ZeroDivisionError:
                processDict["OBP"] = 0
            processDict["OPS"] = processDict["OBP"] + processDict["SLG"]

            if shouldRound:
                processDict["AVG"] = round(processDict["AVG"], 3)
                processDict["OBP"] = round(processDict["OBP"], 3)
                processDict["SLG"] = round(processDict["SLG"], 3)
                processDict["OPS"] = round(processDict["OPS"], 3)

        elif type == "Pitchers":
            try:
                # 把三進位的局數轉成十進位，才可以計算
                IP_decimal = (
                    int(processDict["IP"])
                    + (processDict["IP"] - int(processDict["IP"])) * 10 * 3**-1
                )

                # 加這個條件是因為WeeklyStats Table把Fielder, Pitcher混在一起
                # 所以會有重複名稱的欄位(ex:都有H, K, BB, ...)
                # 但是Today的話會分開，因此不會有這個問題

                if isWeekly:
                    processDict["ERA"] = processDict["ER"] * 9 / IP_decimal
                    processDict["WHIP"] = (
                        processDict["H_P"] + processDict["BB_P"]
                    ) / IP_decimal
                    processDict["K9"] = processDict["K_P"] * 9 / IP_decimal
                else:
                    processDict["ERA"] = processDict["ER"] * 9 / IP_decimal
                    processDict["WHIP"] = (
                        processDict["H"] + processDict["BB"]
                    ) / IP_decimal
                    processDict["K/9"] = processDict["K"] * 9 / IP_decimal

                if shouldRound:
                    processDict["ERA"] = round(processDict["ERA"], 2)
                    processDict["WHIP"] = round(processDict["WHIP"], 2)
                    if isWeekly:
                        processDict["K9"] = round(processDict["K9"], 2)
                    else:
                        processDict["K/9"] = round(processDict["K/9"], 2)

            except ZeroDivisionError:
                processDict["ERA"] = 0
                processDict["WHIP"] = 0
                if isWeekly:
                    processDict["K9"] = 0
                else:
                    processDict["K/9"] = 0

    if request.method == "POST":
        if request.form.get("confirmed", False):
            fielders = Table("Fielder", metadata, autoload_with=engine)
            pitchers = Table("Pitcher", metadata, autoload_with=engine)

            todayfielders = Table("TodayFielder", metadata, autoload_with=engine)
            todaypitchers = Table("TodayPitcher", metadata, autoload_with=engine)

            account = Table("Account", metadata, autoload_with=engine)
            weeklyStats = Table("WeeklyStats", metadata, autoload_with=engine)

            with engine.begin() as connection:
                queryTodayFielders = select(todayfielders)
                results = connection.execute(queryTodayFielders)
                todayFieldersResult = results.fetchall()

                queryTodayPitchers = select(todaypitchers)
                results = connection.execute(queryTodayPitchers)
                todayPitchersResult = results.fetchall()

                inspector = inspect(engine)
                tableExist = inspector.get_table_names()

                # 先抓出所有table的欄位，以便後續使用
                todayFielderColumns = inspector.get_columns("TodayFielder")
                todayPitcherColumns = inspector.get_columns("TodayPitcher")

                # ==========
                # 更新本季成績
                # ==========
                def seasonUpdate(type, todayPlayersResult, players):
                    for i in range(len(todayPlayersResult)):
                        # 取出球員對應到的球季成績
                        query_season = select(players).where(
                            players.c.player_id == todayPlayersResult[i][1]
                        )
                        result = connection.execute(query_season)
                        SelectPlayer = result.fetchone()

                        processDict = {}

                        if not SelectPlayer:
                            # 加入非stats的欄位
                            processDict["player_id"] = todayPlayersResult[i][1]
                            processDict["name"] = todayPlayersResult[i][2]

                            # 因為今日成績沒有隊伍資訊，所以先用TBD，之後再去DB內修改
                            processDict["team"] = "TBD"

                        # 本季成績 + 今日成績 -> 新的本季成績
                        if type == "Fielders":
                            for (
                                key,
                                value,
                            ) in FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                # AVG, OBP, SLB, OPS不能直接加
                                if key not in ["AVG", "OBP", "SLG", "OPS"]:
                                    try:
                                        processDict[key] = (
                                            getattr(SelectPlayer, key)
                                            + todayPlayersResult[i][value]
                                        )
                                    except AttributeError:
                                        processDict[key] = todayPlayersResult[i][value]

                            # 因為今日成績沒有一安，因此要額外計算
                            # 1H = H - 2H - 3H - HR
                            try:
                                processDict["1H"] = getattr(SelectPlayer, "1H") + (
                                    todayPlayersResult[i][7]
                                    - todayPlayersResult[i][8]
                                    - todayPlayersResult[i][9]
                                    - todayPlayersResult[i][10]
                                )
                            except AttributeError:
                                processDict["1H"] = (
                                    todayPlayersResult[i][7]
                                    - todayPlayersResult[i][8]
                                    - todayPlayersResult[i][9]
                                    - todayPlayersResult[i][10]
                                )
                        elif type == "Pitchers":
                            for (
                                key,
                                value,
                            ) in PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                try:
                                    if key == "IP":
                                        # 把局數加總的十進位轉成三進位
                                        IP_sum = (
                                            getattr(SelectPlayer, key)
                                            + todayPlayersResult[i][3]
                                        )
                                        integer = int(IP_sum)
                                        decimal = IP_sum - integer
                                        if decimal * 10 >= 3:
                                            integer += 1
                                            decimal -= 0.3
                                        processDict[key] = integer + decimal
                                    elif key == "SV_H":
                                        processDict["SV+H"] = (
                                            getattr(SelectPlayer, "SV+H")
                                            + todayPlayersResult[i][value]
                                        )
                                    elif key not in ["K9", "ERA", "WHIP"]:
                                        processDict[key] = (
                                            getattr(SelectPlayer, key)
                                            + todayPlayersResult[i][value]
                                        )
                                except AttributeError:
                                    if key == "IP":
                                        processDict[key] = todayPlayersResult[i][3]
                                    elif key == "SV_H":
                                        processDict["SV+H"] = todayPlayersResult[i][
                                            value
                                        ]
                                    else:
                                        processDict[key] = todayPlayersResult[i][value]
                            # 因為今日成績沒有APP，但是有出現在今日成績就代表有出場
                            try:
                                processDict["APP"] = getattr(SelectPlayer, "APP") + 1
                            except AttributeError:
                                processDict["APP"] = 1

                        adjustUnadditive(type, processDict, True, False)
                        print(processDict)
                        if SelectPlayer:
                            update_stmt = (
                                update(players)
                                .where(players.c.player_id == todayPlayersResult[i][1])
                                .values(processDict)
                            )
                            connection.execute(update_stmt)
                        else:
                            # Account, position, round欄位可以為null，所以不需要設定
                            insert_stmt = insert(players).values(processDict)
                            connection.execute(insert_stmt)

                # ==========
                # 更新當週成績
                # ==========
                def weeklyUpdate():
                    if "WeeklyStats" not in tableExist:
                        # 新增一個WeeklyStats Table
                        # 此Table會包括所有Fielder, Pitcher的欄位，不分開成兩個Table了

                        # 宣告此Table需要的欄位
                        columns = [
                            Column("id", Integer, primary_key=True),
                            Column("account", String(255)),
                        ]

                        # 依序加入Fielder, Pitcher的欄位

                        for todayFielderColumn in todayFielderColumns:
                            if todayFielderColumn["name"] in [
                                "db_id",
                                "player_id",
                                "name",
                            ]:
                                continue

                            if todayFielderColumn["name"] in [
                                "AVG",
                                "OBP",
                                "SLG",
                                "OPS",
                            ]:
                                columns.append(
                                    Column(todayFielderColumn["name"], Float)
                                )
                            else:
                                columns.append(
                                    Column(todayFielderColumn["name"], Integer)
                                )

                        for todayPitcherColumn in todayPitcherColumns:
                            if todayPitcherColumn["name"] in [
                                "db_id",
                                "player_id",
                                "name",
                            ]:
                                continue

                            if todayPitcherColumn["name"] in [
                                "IP",
                                "ERA",
                                "WHIP",
                                "K9",
                            ]:
                                columns.append(
                                    Column(todayPitcherColumn["name"], Float)
                                )
                            # 因為前面Fielder已經使用過這些名稱
                            elif todayPitcherColumn["name"] in [
                                "H",
                                "HR",
                                "BB",
                                "HBP",
                                "K",
                                "R",
                            ]:
                                columns.append(
                                    Column(todayPitcherColumn["name"] + "_P", Integer)
                                )
                            else:
                                columns.append(
                                    Column(todayPitcherColumn["name"], Integer)
                                )

                        table = Table("WeeklyStats", metadata, *columns)
                        metadata.create_all(engine, [table])

                    # =============================
                    # 確認WeeklyStats Table內
                    # 目前有無記載要查詢的account的成績
                    # =============================
                    def checkAccount(account):
                        queryWeeklyStats = select(weeklyStats).where(
                            weeklyStats.c.account == account
                        )
                        result = connection.execute(queryWeeklyStats)
                        SelectAccount = result.fetchone()
                        return SelectAccount

                    # =========================
                    # 依照傳入的Table、球員種類
                    # 更新WeeklyStats Table的資料
                    # =========================
                    def updatePlayer(
                        type,
                        todayPlayersResult,
                        todayplayers,
                        todayPlayerColumns,
                        players,
                        todayTotal,
                    ):
                        for i in range(len(todayPlayersResult)):
                            # 因為有今日成績的球員，並沒有紀錄該球員所屬的Account
                            # 所以要利用join把有球員所屬的Account，也就是整季成績的Table給載進來
                            # 利用兩者都有的player_id去join
                            query = (
                                select(todayplayers)
                                .join(
                                    players,
                                    players.c.player_id == todayplayers.c.player_id,
                                )
                                .where(
                                    todayplayers.c.player_id
                                    == todayPlayersResult[i][1],
                                    players.c.Account == Account.account,
                                )
                            )
                            result = connection.execute(query)
                            # 今日成績的所有球員都會被遍歷，但有些球員可能沒人選
                            # 於是會跳過這些沒人選的球員
                            SelectPlayer = result.fetchone()
                            if not SelectPlayer:
                                continue
                            # 接下來要判斷選到的球員，是否被放在BN
                            # 不是的話就會跳過
                            index = 0
                            # 確認選到的球員被放在rearrange的位置
                            for player in rearrangeDict[Account.account][type]:
                                if not player or SelectPlayer[1] != int(
                                    player.player_id
                                ):
                                    index += 1
                                else:
                                    break

                            # 野手和投手BN格子的索引不同
                            if type == "Fielders":
                                if index >= 11:
                                    continue
                            elif type == "Pitchers":
                                if index >= 8:
                                    continue

                            # 有被選入到某個Account的球員
                            # 因為回圈內有些地方會跳出，因此宣告一個取index的變數
                            j = 0

                            if type == "Fielders":
                                for todayPlayerColumn in todayPlayerColumns:
                                    # AVG, OBP, SLG, OPS這四個stats沒法直接加
                                    # 後面再處理
                                    if todayPlayerColumn["name"] in [
                                        "db_id",
                                        "player_id",
                                        "name",
                                        "AVG",
                                        "OBP",
                                        "SLG",
                                        "OPS",
                                    ]:
                                        continue

                                    # 可直接加的stats

                                    # +3是因為todayPlayer的每一列中
                                    # 前三個column分別為db_id, player_id, name
                                    todayTotal[todayPlayerColumn["name"]] = (
                                        todayTotal[todayPlayerColumn["name"]]
                                        + SelectPlayer[j + 3]
                                    )
                                    j += 1

                                # 處理AVG, OBP, SLG, OPS
                                adjustUnadditive(type, todayTotal, True, True)

                            elif type == "Pitchers":
                                for todayPlayerColumn in todayPlayerColumns:
                                    # ERA, WHIP, K9這三個比項不直接加
                                    if todayPlayerColumn["name"] in [
                                        "db_id",
                                        "player_id",
                                        "name",
                                    ]:
                                        continue

                                    elif todayPlayerColumn["name"] in [
                                        "ERA",
                                        "WHIP",
                                        "K9",
                                    ]:
                                        j += 1
                                        continue

                                    # **
                                    # 這些欄位會和todayTotal，屬於打者的欄位名稱撞到
                                    # 所以要加上_P
                                    if todayPlayerColumn["name"] in [
                                        "H",
                                        "HR",
                                        "BB",
                                        "HBP",
                                        "K",
                                        "R",
                                    ]:
                                        todayTotal[todayPlayerColumn["name"] + "_P"] = (
                                            todayTotal[todayPlayerColumn["name"] + "_P"]
                                            + SelectPlayer[j + 3]
                                        )
                                    else:
                                        todayTotal[todayPlayerColumn["name"]] = (
                                            todayTotal[todayPlayerColumn["name"]]
                                            + SelectPlayer[j + 3]
                                        )
                                    j += 1

                                # IP因為進制的問題
                                # 每個Pitcher跑完之後都要處理
                                IP_sum = todayTotal["IP"]
                                integer = int(IP_sum)
                                decimal = IP_sum - integer
                                if decimal * 10 >= 3:
                                    integer += 1
                                    decimal -= 0.3
                                todayTotal["IP"] = integer + decimal

                                # ERA, WHIP, K9另外計算
                                # 防止有投手本季成績為0.0
                                adjustUnadditive(type, todayTotal, True, True)

                    # 查詢db中的Account Table的所有帳號，
                    # 接下來會尋找每個帳號中，今天有成績的選手
                    query_account = select(account)
                    results = connection.execute(query_account)
                    AccountsResult = results.fetchall()

                    # 遍歷查詢的所有帳號
                    for Account in AccountsResult:
                        # admin帳號不會出現在每週成績內，略過
                        if Account.account == "admin":
                            continue

                        SelectAccount = checkAccount(Account.account)

                        # 若目前還沒有此帳號的每週成績，則新增一個全部stats都為0的列
                        if not SelectAccount:
                            insertDict = {
                                "id": Account.id,
                                "account": Account.account,
                            }
                            WeeklyColumns = inspector.get_columns("WeeklyStats")
                            for WeeklyColumn in WeeklyColumns:
                                if WeeklyColumn["name"] in ["id", "account"]:
                                    continue

                                insertDict[WeeklyColumn["name"]] = 0

                            insertStmt = insert(weeklyStats).values(insertDict)
                            connection.execute(insertStmt)

                        else:
                            # 每天該帳號的加總stats都從0開始
                            # 接著會遍歷每個該帳號所屬的球員
                            # 把stats累加起來
                            todayTotal = {}

                            WeeklyColumns = inspector.get_columns("WeeklyStats")
                            for WeeklyColumn in WeeklyColumns:
                                if WeeklyColumn["name"] in ["id", "account"]:
                                    continue
                                todayTotal[WeeklyColumn["name"]] = 0

                            updatePlayer(
                                "Fielders",
                                todayFieldersResult,
                                todayfielders,
                                todayFielderColumns,
                                fielders,
                                todayTotal,
                            )

                            updatePlayer(
                                "Pitchers",
                                todayPitchersResult,
                                todaypitchers,
                                todayPitcherColumns,
                                pitchers,
                                todayTotal,
                            )

                            # 以上Account所有選擇的球員之stats都加總完成
                            # 再來還要把原本就在此Table內的數據 + 上今日的成績
                            # 當作最新的本週成績
                            for WeeklyColumn in WeeklyColumns:
                                if WeeklyColumn["name"] in ["id", "account"]:
                                    continue

                                todayTotal[WeeklyColumn["name"]] = todayTotal[
                                    WeeklyColumn["name"]
                                ] + getattr(SelectAccount, WeeklyColumn["name"])

                                # 最後該帳號的
                                # 當日總成績和當週成績的IP做相加時
                                # 要再處理一次
                                if WeeklyColumn["name"] == "IP":
                                    integer = int(todayTotal["IP"])
                                    decimal = todayTotal["IP"] - integer
                                    if decimal * 10 >= 3:
                                        integer += 1
                                        decimal -= 0.3
                                    todayTotal["IP"] = integer + decimal

                            # 因為這邊又把本日成績和本週原始成績做相加的動作
                            # 所以那些不能加的欄位要再重新計算一次
                            adjustUnadditive("Fielders", todayTotal, True, True)
                            adjustUnadditive("Pitchers", todayTotal, True, True)

                            # 最後把處理完的stats加上WeeklyStats所需要的id, account column
                            todayTotal["id"] = Account.id
                            todayTotal["account"] = Account.account

                            # 更新WeeklyStats Table
                            updateStmt = (
                                update(weeklyStats)
                                .where(weeklyStats.c.account == Account.account)
                                .values(todayTotal)
                            )
                            connection.execute(updateStmt)

                # Fielders, Pitchers在今日成績會分成兩個Table處理
                # WeeklyStats則會把Fielders, Pitchers混在一起處理
                seasonUpdate("Fielders", todayFieldersResult, fielders)
                seasonUpdate("Pitchers", todayPitchersResult, pitchers)
                weeklyUpdate()

                # 更新完後，就可以清除Today的資料了
                deleteStmt = delete(todayfielders)
                connection.execute(deleteStmt)
                deleteStmt = delete(todaypitchers)
                connection.execute(deleteStmt)

            return "更新完成！"
        else:
            return "更新失敗。"
    else:
        return render_template("todayupdate.html")
