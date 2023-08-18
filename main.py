from flask import Flask, render_template, session, request, url_for, redirect, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    MetaData,
    String,
    Float,
    inspect,
    select,
    update,
    insert,
    and_,
)
from werkzeug.security import generate_password_hash, check_password_hash
from threading import Lock
from info import *

# 先建立一個SQLAlchemy的instance
db = SQLAlchemy()

time_flag = False

background_start = False


def create_app():
    """
    初始化Flask app
    並將app與SQLAlchemy instance綁定

    Returns:
        Flask: 使用的Flask app
    """
    app = Flask(__name__, static_folder="static", static_url_path="/")
    CORS(app)  # 在開發環境下，這可以避免因為跨域問題導致的錯誤
    # 從外部的py檔案，設定app的config
    app.config.from_pyfile("config.py")
    app.debug = True
    db.init_app(app)
    return app


app = create_app()
metadata = MetaData()
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")

# 在player路由中會使用到
# 每個帳號會當作key，裡面包含了該帳號的rearrange, rearrangeQueryFielders, rearrangeQueryPitchers
rearrangeDict = {}
# 處理要使用的資料表(table)

# 定義映射類別(mapping class)
# 來描述db table和Python class的關係


# Account Table
class Account(db.Model):
    # 若無設定，預設的table name會被轉成小寫的account
    __tablename__ = "Account"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=True)
    opponent = db.Column(db.String(100), nullable=True)

    def __init__(self, account, password, team, opponent):
        self.account = account
        self.password = password
        self.team = team
        self.opponent = opponent

    def __repr__(self):
        return "您的ID為{}, 帳號為{}".format(self.id, self.account)


class Fielder(db.Model):
    __tablename__ = "Fielder"
    _db_id = db.Column("db_id", db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100))
    team = db.Column(db.String(100))
    PA = db.Column(db.Integer)
    AB = db.Column(db.Integer)
    RBI = db.Column(db.Integer)
    R = db.Column(db.Integer)
    H = db.Column(db.Integer)
    H1 = db.Column("1H", db.Integer)
    H2 = db.Column("2H", db.Integer)
    H3 = db.Column("3H", db.Integer)
    HR = db.Column(db.Integer)
    TB = db.Column(db.Integer)
    K = db.Column(db.Integer)
    SB = db.Column(db.Integer)
    OBP = db.Column(db.Float)
    SLG = db.Column(db.Float)
    AVG = db.Column(db.Float)
    DP = db.Column(db.Integer)
    BUNT = db.Column(db.Integer)
    SF = db.Column(db.Integer)
    BB = db.Column(db.Integer)
    IBB = db.Column(db.Integer)
    HBP = db.Column(db.Integer)
    CS = db.Column(db.Integer)
    OPS = db.Column(db.Float)
    Account = db.Column(db.String(100))
    position = db.Column(db.String(100))
    round = db.Column(db.Integer)

    def __init__(
        self,
        player_id,
        name,
        team,
        PA,
        AB,
        RBI,
        R,
        H,
        H1,
        H2,
        H3,
        HR,
        TB,
        K,
        SB,
        OBP,
        SLG,
        AVG,
        DP,
        BUNT,
        SF,
        BB,
        IBB,
        HBP,
        CS,
        OPS,
        Account,
        position,
        round,
    ):
        self.player_id = player_id
        self.name = name
        self.team = team
        self.PA = PA
        self.AB = AB
        self.RBI = RBI
        self.R = R
        self.H = H
        self.H1 = H1
        self.H2 = H2
        self.H3 = H3
        self.HR = HR
        self.TB = TB
        self.K = K
        self.SB = SB
        self.OBP = OBP
        self.SLG = SLG
        self.AVG = AVG
        self.DP = DP
        self.BUNT = BUNT
        self.SF = SF
        self.BB = BB
        self.IBB = IBB
        self.HBP = HBP
        self.CS = CS
        self.OPS = OPS
        self.Account = Account
        self.position = position
        self.round = round

    def to_dict(self, stats):
        return_dict = {
            "player_ID": self.player_id,
            "Player": self.name,
            "team": self.team,
            "PA": self.PA,
            "AB": self.AB,
        }
        for stat in stats:
            return_dict[stat] = getattr(self, stat)
        return_dict["Account"] = self.Account
        return_dict["position"] = self.position.split(", ")
        return_dict["round"] = self.round
        return return_dict


class Pitcher(db.Model):
    __tablename__ = "Pitcher"
    _db_id = db.Column("db_id", db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100))
    team = db.Column(db.String(100))
    APP = db.Column(db.Integer)
    W = db.Column(db.Integer)
    L = db.Column(db.Integer)
    SV = db.Column(db.Integer)
    BSV = db.Column(db.Integer)
    HLD = db.Column(db.Integer)
    SV_H = db.Column("SV+H", db.Integer)
    IP = db.Column(db.Float)
    WHIP = db.Column(db.Float)
    ERA = db.Column(db.Float)
    H = db.Column(db.Integer)
    HR = db.Column(db.Integer)
    BB = db.Column(db.Integer)
    HBP = db.Column(db.Integer)
    K = db.Column(db.Integer)
    R = db.Column(db.Integer)
    ER = db.Column(db.Integer)
    K9 = db.Column("K/9", db.Float)
    QS = db.Column(db.Integer)
    Account = db.Column(db.String(100))
    position = db.Column(db.String(100))
    round = db.Column(db.Integer)

    def __init__(
        self,
        player_id,
        name,
        team,
        APP,
        W,
        L,
        SV,
        BSV,
        HLD,
        SV_H,
        IP,
        WHIP,
        ERA,
        H,
        HR,
        BB,
        HBP,
        K,
        R,
        ER,
        K9,
        QS,
        Account,
        position,
        round,
    ):
        self.player_id = player_id
        self.name = name
        self.team = team
        self.APP = APP
        self.W = W
        self.L = L
        self.SV = SV
        self.BSV = BSV
        self.HLD = HLD
        self.SV_H = SV_H
        self.IP = IP
        self.WHIP = WHIP
        self.ERA = ERA
        self.H = H
        self.HR = HR
        self.BB = BB
        self.HBP = HBP
        self.K = K
        self.R = R
        self.ER = ER
        self.K9 = K9
        self.QS = QS
        self.Account = Account
        self.position = position
        self.round = round

    def to_dict(self, stats):
        return_dict = {
            "player_ID": self.player_id,
            "Player": self.name,
            "team": self.team,
        }
        for stat in stats:
            return_dict[stat] = getattr(self, stat)
        return_dict["Account"] = self.Account
        return_dict["position"] = self.position.split(", ")
        return_dict["round"] = self.round
        # return {
        #     "player_ID": self.player_id,
        #     "Player": self.name,
        #     "team": self.team,
        #     "IP": self.IP,
        #     "W": self.W,
        #     "SV+H": self.SV_H,
        #     "HR": self.HR_pitcher,
        #     "WHIP": self.WHIP,
        #     "ERA": self.ERA,
        #     "K/9": self.K9,
        #     "K": self.K_pitcher,
        #     "BB": self.BB_pitcher,
        #     "QS": self.QS,
        #     "K/BB": self.K_BB,
        #     "Account": self.Account,
        #     "position": self.position.split(", "),
        #     "round": self.round,
        # }
        return return_dict


@app.route("/sql")
def sql():
    db.create_all()
    return "OK"


# 首頁
@app.route("/home")
def home():
    query = request.args.get("test", None)
    if query:
        return "別亂輸入query!"
    else:
        if "id" in session:
            return redirect(url_for("myleague", id=session["id"]))
        return render_template("home.html")


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


# 登入頁面
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        received = request.get_json()
        account = received["account"]
        password = received["password"]

        if login_check(account, password):
            if account == "admin":
                return jsonify(
                    {"redirect": url_for("manager"), "success": True, "admin": True}
                )
            else:
                id = (
                    db.session.query(Account)
                    .filter(Account.account == account)
                    .first()
                    .id
                )
                session["id"] = id

                # 登入後，判斷該帳號是否已經存在rearrangeDict內
                global rearrangeDict
                if account not in rearrangeDict.keys():
                    rearrangeDict[account] = {"rearrange": False}
                return jsonify(
                    {
                        "redirect": "/league_home",
                        "id": id,
                        "success": True,
                        "admin": False,
                    }
                )
        else:
            return jsonify({"redirect": url_for("login"), "success": False})
    # 在URL輸入login時，導引到首頁
    else:
        return render_template("login.html")


# 註冊頁面
@app.route("/register", methods=["GET", "POST"])
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
                new_account = Account(
                    account, generate_password_hash(password, "sha256"), None
                )
            else:
                new_account = Account(
                    account,
                    generate_password_hash(password, "sha256"),
                    received["team"],
                )
            db.session.add(new_account)
            db.session.commit()
            return redirect(url_for("home"))

    return render_template("register.html")


# 忘記密碼頁面
@app.route("/forget", methods=["GET", "POST"])
def forget():
    pass


# 聯盟管理者頁面
@app.route("/manager", methods=["GET", "POST"])
def manager():
    if request.method == "POST":
        if request.form.get("confirm", False):
            # ------------------------------------------------------------------
            # 定義Fielder, Pitcher這兩個Table

            # Fielder
            fielder_columns = [
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

            fielder_categories = request.form.getlist("Batting")
            pitcher_categories = request.form.getlist("Pitching")

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
@app.route("/league_home/<int:id>", methods=["GET", "POST"])
def myleague(id):
    if "id" not in session:
        return redirect(url_for("login"))
    query = db.session.query(Account).filter(Account.id == id).first()
    account = query.account
    team = query.team
    return render_template("myleague.html", account=account, team=team)


# 為了在jinja2內使用isinstance這個功能
# 需要加上的地方
@app.template_filter("isinstance")
def isinstance_filter(obj, class_name):
    if class_name == "Fielder":
        return isinstance(obj, Fielder)
    elif class_name == "Pitcher":
        return isinstance(obj, Pitcher)
    else:
        import builtins

        type_fn = getattr(builtins, class_name, None)
        return isinstance(obj, type_fn)


@app.context_processor
def utility_processor():
    def get_attribute(obj, attr):
        return getattr(obj, attr)

    def get_min(playersCount):
        min = 99
        for key, value in playersCount.items():
            if value < min:
                min = value
        return min

    def get_max(playersCount):
        max = 0
        for key, value in playersCount.items():
            if value > max:
                max = value
        return max

    return dict(get_attribute=get_attribute, get_min=get_min, get_max=get_max)


# 選秀頁面
@app.route("/draft", methods=["GET", "POST"])
def draft():
    def score_fielder(fielder, stats):
        OPS_plus = ((fielder.OBP / AVG_OBP) + (fielder.SLG / AVG_SLG) - 1) * 100
        score = 0
        for key, value in SCORING_FIELDER.items():
            score += getattr(fielder, key) * value if key in stats else 0
        score += (OPS_plus - 100) * (fielder.PA / AVG_PA)
        return score

    def score_pitcher(pitcher, stats):
        IP_decimal = int(pitcher.IP) + (pitcher.IP - int(pitcher.IP)) * 3**-1
        score = 0
        for key, value in SCORING_PITCHER.items():
            score += getattr(pitcher, key) * value if key in stats else 0
        return score

    # Query for sidebar
    query_account = db.session.query(Account).filter(Account.account != "admin").all()
    query_account = sorted(query_account, key=lambda k: k.id)
    # Query for player
    fielder_categories, pitcher_categories, _, _ = read_category()

    # print(pitcher_categories)
    fielders = db.session.query(Fielder).all()
    pitchers = db.session.query(Pitcher).all()

    players = fielders + pitchers

    for i, player in enumerate(
        sorted(
            players,
            key=lambda p: score_fielder(p, fielder_categories)
            if isinstance(p, Fielder)
            else score_pitcher(p, pitcher_categories),
            reverse=True,
        ),
        start=1,
    ):
        player.Rank = i
    players = sorted(players, key=lambda player: player.Rank, reverse=False)
    print(players)
    print(players[0].position)
    positions = {
        "fielders": [
            "C",
            "1B",
            "2B",
            "3B",
            "SS",
            "OF",
            "OF",
            "OF",
            "OF",
            "Util",
            "BN",
            "BN",
            "BN",
            "BN",
        ],
        "pitchers": ["SP", "SP", "SP", "SP", "RP", "RP", "BN", "BN", "BN", "BN"],
    }
    return render_template(
        "draft.html",
        login_account=request.form["account"],
        accounts=query_account,
        players=players,
        fielder_categories=fielder_categories,
        pitcher_categories=pitcher_categories,
        positions=positions,
    )


# 選秀頁面，接收user端請求選秀的時間
@app.route("/draft/time", methods=["GET"])
def time():
    from datetime import datetime, timedelta

    # draft_time = datetime.now() + timedelta(hours=1)
    draft_time = datetime(2023, 8, 13, 13, 19, 20)
    return jsonify({"Time": draft_time.isoformat("T", "seconds")})


# 選秀頁面，接收user端發出的firstTimer事件
@socketio.on("firstTimer", namespace="/draft")
def firstTimer(_):
    global time_flag
    # 第一個分頁發送emit後
    # 會更改time_flag並等待一秒
    # 弭平不同分頁進入選秀頁面，不到一秒的時間差
    # 讓所有分頁可以同步開始
    if not time_flag:
        time_flag = True
        socketio.sleep(1)
        socketio.emit("firstTimer", {"message": "Success!"}, namespace="/draft")


# 選秀頁面，接收user端發出的draftTimer事件
@socketio.on("draftTimer", namespace="/draft")
def draftTimer(auto):
    if auto:
        socketio.sleep(1)
    socketio.emit("draftTimer", {"message": "Success!"}, namespace="/draft")


# 選秀頁面，接收user端選擇球員並按下選秀按鈕後
# 更新資料庫
@socketio.on("update", namespace="/draft")
def draftupdate(data):
    if data["auto"]:
        socketio.sleep(1)
    print(data)
    try:
        if data["HR_fielder"]:
            query = (
                db.session.query(Fielder)
                .filter(Fielder.player_id == int(data["player_ID"]))
                .first()
            )
            query.Account = data["Account"]
            query.round = data["round"]
        else:
            query = (
                db.session.query(Pitcher)
                .filter(Pitcher.player_id == int(data["player_ID"]))
                .first()
            )
            query.Account = data["Account"]
            query.round = data["round"]
        db.session.commit()
        data["message"] = "Success!"
        socketio.emit("update", data, namespace="/draft")
    except ValueError as e:
        data["message"] = "Failed!"
        socketio.emit("update", data, namespace="/draft")


# 選秀頁面，處理user端按下Teams選項後，傳送AJAX請求
# 列出該user各位置所選球員
@app.route("/draft/teams", methods=["POST"])
def teams():
    login = request.get_json()
    login = login["login"]
    # print(type(login), login)
    try:
        query_fielders = (
            db.session.query(Fielder).filter(Fielder.Account == login).all()
        )
        query_pitchers = (
            db.session.query(Pitcher).filter(Pitcher.Account == login).all()
        )

        query_fielders = sorted(query_fielders, key=lambda k: k.round, reverse=False)
        query_pitchers = sorted(query_pitchers, key=lambda k: k.round, reverse=False)

        fielder_categories, pitcher_categories, _, _ = read_category()

        fielders_list_of_dicts = [
            fielder.to_dict(fielder_categories) for fielder in query_fielders
        ]
        pitchers_list_of_dicts = [
            pitcher.to_dict(pitcher_categories) for pitcher in query_pitchers
        ]
        return_data = {
            "fielders": fielders_list_of_dicts,
            "pitchers": pitchers_list_of_dicts,
        }
        # print(return_data["pitchers"])
        return jsonify(
            {
                "data": return_data,
                "message": "Success!",
                "stats": [fielder_categories, pitcher_categories],
            }
        )
    except ValueError as e:
        return jsonify({"message": "failed"})


started = False
current_clients = []
background_task = Lock()


def background_update():
    """背景任務，用來定期的爬取TodayFielder, TodayPitcher內的資料

    Returns:
        None
    """
    if background_task.acquire(False):
        try:
            global started
            while started:
                socketio.sleep(10)
                # 因為disconnect後
                # 雖然started已經設為False了
                # 但可能本來就已經進入while loop
                # 但還在這個等待的時間
                # 因此額外加上一個判斷式
                # 如果是在等待時間disconnect
                # 就不會再執行
                if started:
                    emit_json = {}
                    query_fielder = Table(
                        "TodayFielder", metadata, autoload_with=engine
                    )
                    query_pitcher = Table(
                        "TodayPitcher", metadata, autoload_with=engine
                    )
                    with engine.begin() as connection:
                        # Fielder
                        stmt = query_fielder.select()
                        result = connection.execute(stmt)
                        rows = result.fetchall()
                        fielders = []
                        for row in rows:
                            fielder_data = []
                            for data in row:
                                fielder_data.append(data)
                            fielders.append(fielder_data)

                        # Pitcher
                        stmt = query_pitcher.select()
                        result = connection.execute(stmt)
                        rows = result.fetchall()
                        pitchers = []
                        for row in rows:
                            pitcher_data = []
                            for data in row:
                                pitcher_data.append(data)
                            pitchers.append(pitcher_data)

                        emit_json["Fielder"] = fielders
                        emit_json["Pitcher"] = pitchers

                        socketio.emit("update", emit_json, namespace="/matchup")

                    # print("Update Success!")
        finally:
            background_task.release()


# 球員頁面
@app.route("/player", methods=["GET", "POST"])
def player():
    account = request.form["account"]
    global rearrangeDict
    queryAccount = db.session.query(Account).filter(Account.account == account).first()
    # 根據球員的position，決定該球員會在網頁的哪一列上，讓該球員會對應到守位格
    # 總共有20個格子 (16個正常守位 + 4個BN)
    positionDict = {
        # 10
        "Fielder": ["C", "1B", "2B", "3B", "SS", "OF", "OF", "OF", "OF", "Util"],
        # 6
        "Pitcher": ["SP", "SP", "SP", "SP", "RP", "RP"],
    }

    if not rearrangeDict[account]["rearrange"]:
        # 從db的Fielder, Pitcher Table抓出此帳號所選的球員

        queryFielders = (
            db.session.query(Fielder).filter(Fielder.Account == account).all()
        )
        queryPitchers = (
            db.session.query(Pitcher).filter(Pitcher.Account == account).all()
        )

        # 宣告有多個該守位的格子已被使用幾個、最多使用幾個
        Used = {
            "OF": {"Count": 0, "Limit": 4},
            "SP": {"Count": 0, "Limit": 4},
            "RP": {"Count": 0, "Limit": 2},
        }

        # Fielder
        # 宣告一個用來存調整順序後的球員陣列
        rearrangeQueryFielders = [False] * 10

        # 先賦予每個球員 "是否已經被分配守位" 這個屬性
        for queryFielder in queryFielders:
            queryFielder.assignPosition = False

        # 宣告當前取的fielder、守位、BN起始對應的索引值
        fielderIndex = 0
        positionIndex = 0
        # BNIndex = 10

        # 宣告決定程式流程的一些Bool變數，分別是：
        # 決定所選球員內，是否擁有多守位的球員
        # 決定排序時是否在第一輪(略過多守位球員的情況)
        # 決定Util格子是否被任一球員使用
        hasMultiPosition = False
        firstRound = True
        UtilUsed = False

        while fielderIndex < len(queryFielders) or hasMultiPosition:
            # 第一輪，先略過多守位球員
            if firstRound:
                # 多守位球員會以 ", " 被隔開多個守位
                if len(queryFielders[fielderIndex].position.split(", ")) > 1:
                    fielderIndex += 1
                    hasMultiPosition = True
                    # 最後一個球員被選到後就會重新開始while loop
                    if fielderIndex == len(queryFielders):
                        firstRound = False
                        fielderIndex = 0
                    continue
                # 指定守位到對應格子

                # 從第一個守位開始選起，遇到符合的守位，且該守位目前尚無人使用的話
                # 就會跳出此回圈
                for position in positionDict["Fielder"]:
                    if queryFielders[fielderIndex].position == position:
                        positionIndex = positionDict["Fielder"].index(position)

                        # 遇到該守位有多個格子的情況
                        if position in Used.keys():
                            positionIndex += Used[position]["Count"]
                            # 如果該多格子的守位尚未使用完的情況
                            # 如果使用完的話就會往後，將此球員放到Util或BN
                            if (
                                positionIndex
                                < positionDict["Fielder"].index(position)
                                + Used[position]["Limit"]
                            ):
                                if not rearrangeQueryFielders[positionIndex]:
                                    rearrangeQueryFielders[
                                        positionIndex
                                    ] = queryFielders[fielderIndex]
                                    queryFielders[fielderIndex].assignPosition = True
                                    Used[position]["Count"] += 1
                                    break

                        # 只有單一格子
                        else:
                            if not rearrangeQueryFielders[positionIndex]:
                                rearrangeQueryFielders[positionIndex] = queryFielders[
                                    fielderIndex
                                ]
                                queryFielders[fielderIndex].assignPosition = True
                                break

                # 在所有守位都檢查完或是該球員已經被分配到格子的情況

                # Util所有球員都能放
                if not queryFielders[fielderIndex].assignPosition and not UtilUsed:
                    rearrangeQueryFielders[9] = queryFielders[fielderIndex]
                    queryFielders[fielderIndex].assignPosition = True
                    UtilUsed = True

                # 所有守位(含Util)都判斷完，但該球員依舊沒有被分配到格子
                # -> BN
                if not queryFielders[fielderIndex].assignPosition:
                    rearrangeQueryFielders.append(False)
                    rearrangeQueryFielders[-1] = queryFielders[fielderIndex]
                    queryFielders[fielderIndex].assignPosition = True
                    # BNIndex += 1

                fielderIndex += 1
                if fielderIndex == len(queryFielders):
                    firstRound = False
                    fielderIndex = 0

            # 第二輪，開始分配多守位的球員
            else:
                hasMultiPosition = False
                if not queryFielders[fielderIndex].assignPosition:
                    # 用來跳出第一層for loop，也就是該球員的不同守位
                    shouldBreak = False

                    # 迭代該該球員的每個守位
                    for playerPosition in queryFielders[fielderIndex].position.split(
                        ", "
                    ):
                        # 這邊和上述大致相同了
                        for position in positionDict["Fielder"]:
                            if playerPosition == position:
                                positionIndex = positionDict["Fielder"].index(position)
                                if position in Used.keys():
                                    positionIndex += Used[position]["Count"]

                                if position in Used.keys():
                                    if (
                                        positionIndex
                                        < positionDict["Fielder"].index(position)
                                        + Used[position]["Limit"]
                                    ):
                                        if not rearrangeQueryFielders[positionIndex]:
                                            rearrangeQueryFielders[
                                                positionIndex
                                            ] = queryFielders[fielderIndex]
                                            queryFielders[
                                                fielderIndex
                                            ].assignPosition = True
                                            Used[position]["Count"] += 1
                                            shouldBreak = True
                                            break
                                if not rearrangeQueryFielders[positionIndex]:
                                    rearrangeQueryFielders[
                                        positionIndex
                                    ] = queryFielders[fielderIndex]
                                    queryFielders[fielderIndex].assignPosition = True
                                    shouldBreak = True
                                    break

                        # 如果多守位的其中一個守位被成功分配
                        # 就不用再看其他守位了
                        if shouldBreak:
                            break

                    if not queryFielders[fielderIndex].assignPosition and not UtilUsed:
                        rearrangeQueryFielders[9] = queryFielders[fielderIndex]
                        queryFielders[fielderIndex].assignPosition = True
                        UtilUsed = True

                    if not queryFielders[fielderIndex].assignPosition:
                        rearrangeQueryFielders.append(False)
                        rearrangeQueryFielders[-1] = queryFielders[fielderIndex]
                        queryFielders[fielderIndex].assignPosition = True
                        # BNIndex += 1

                fielderIndex += 1

        rearrangeDict[account]["Fielders"] = rearrangeQueryFielders

        # Pitcher
        rearrangeQueryPitchers = [False] * len(queryPitchers)
        # 先賦予每個球員 "是否被分配守位" 這個屬性
        for queryPitcher in queryPitchers:
            queryPitcher.assignPosition = False
        pitcherIndex = 0
        positionIndex = 0
        hasMultiPosition = False
        firstRound = True
        BNIndex = 6
        while pitcherIndex < len(queryPitchers) or hasMultiPosition:
            # 第一輪，先略過多守位球員
            if firstRound:
                if len(queryPitchers[pitcherIndex].position.split(", ")) > 1:
                    pitcherIndex += 1
                    hasMultiPosition = True
                    if pitcherIndex == len(queryPitchers):
                        firstRound = False
                        pitcherIndex = 0
                    continue
                # 指定守位到對應格子
                for position in positionDict["Pitcher"]:
                    if queryPitchers[pitcherIndex].position == position:
                        positionIndex = positionDict["Pitcher"].index(position)
                        positionIndex += Used[position]["Count"]

                        if (
                            positionIndex
                            < positionDict["Pitcher"].index(position)
                            + Used[position]["Limit"]
                            and not rearrangeQueryPitchers[positionIndex]
                        ):
                            rearrangeQueryPitchers[positionIndex] = queryPitchers[
                                pitcherIndex
                            ]
                            queryPitchers[pitcherIndex].assignPosition = True
                            Used[position]["Count"] += 1
                            break

                if not queryPitchers[pitcherIndex].assignPosition:
                    rearrangeQueryPitchers[BNIndex] = queryPitchers[pitcherIndex]
                    queryPitchers[pitcherIndex].assignPosition = True
                    BNIndex += 1

                pitcherIndex += 1
                if pitcherIndex == len(queryPitchers):
                    firstRound = False
                    pitcherIndex = 0

            else:
                hasMultiPosition = False
                if not queryPitchers[pitcherIndex].assignPosition:
                    shouldBreak = False
                    for playerPosition in queryPitchers[pitcherIndex].position.split(
                        ", "
                    ):
                        for position in positionDict["Pitcher"]:
                            if playerPosition == position:
                                positionIndex = positionDict["Pitcher"].index(position)
                                positionIndex += Used[position]

                                if (
                                    positionIndex
                                    < positionDict["Pitcher"].index(position)
                                    + Used[position]["Limit"]
                                    and not rearrangeQueryPitchers[positionIndex]
                                ):
                                    rearrangeQueryPitchers[
                                        positionIndex
                                    ] = queryPitchers[pitcherIndex]
                                    queryPitchers[pitcherIndex].assignPosition = True
                                    Used[position]["Count"] += 1
                                    shouldBreak = True
                                    break

                        if shouldBreak:
                            break

                    if not queryPitchers[pitcherIndex].assignPosition:
                        rearrangeQueryPitchers[BNIndex] = queryPitchers[pitcherIndex]
                        queryPitchers[pitcherIndex].assignPosition = True
                        BNIndex += 1

                pitcherIndex += 1

        rearrangeDict[account]["Pitchers"] = rearrangeQueryPitchers

    # 取出TodayFielder, TodayPitcher Table內所有的比項
    totalFielderCategories = list(FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    totalPitcherCategories = list(PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.keys())

    # 取出manager所選擇的比項
    (
        selectFielderCategories,
        selectPitcherCategories,
        _,
        _,
    ) = read_category()

    # 檢查db內是否已經存在上述兩個紀錄今日成績的Tables
    inspector = inspect(engine)
    existedTables = inspector.get_table_names()

    # 用來存登入此帳號的使用者中，所擁有且今日有出賽球員的成績
    existedFieldersStats, existedPitchersStats = [], []

    if "TodayFielder" not in existedTables:
        tableExist = False
    else:
        tableExist = True
        TodayFielder = Table("TodayFielder", metadata, autoload_with=engine)
        TodayPitcher = Table("TodayPitcher", metadata, autoload_with=engine)

    for fielder in rearrangeDict[account]["Fielders"]:
        if not fielder:
            existedFieldersStats.append(False)
            continue
        # 如果紀錄今日成績的Table不存在，可確定該球員也一定不會有今日出賽的紀錄
        if not tableExist:
            fielder.inlineup = False
        else:
            with engine.begin() as connection:
                # 接下來檢查今日成績的table內有沒有紀錄該球員的成績
                # 如果沒有會回傳一個空的值
                query = select(TodayFielder).where(
                    TodayFielder.c.player_id == fielder.player_id
                )
                result = connection.execute(query)
                fielderStats = result.fetchone()
                # 找不到代表就不在目前尚未在出賽名單
                if not fielderStats:
                    fielder.inlineup = False
                # 如果有就建立一個存該球員今日成績的陣列
                else:
                    fielder.inlineup = True
                    existedFielderStats = []
                    # 所有比項都會紀錄，不只存所選的比項
                    for i in range(len(totalFielderCategories)):
                        existedFielderStats.append(fielderStats[i + 3])
                    # 該球員成績紀錄完後，加入前面所宣告的
                    # 該帳號所擁有球員的所有成績
                    existedFieldersStats.append(existedFielderStats)
        # 調整有些球員id為二位數or三位數的情況，因為db內是以integer的方式儲存
        fielder.player_id = str(fielder.player_id).rjust(4, "0")

    for pitcher in rearrangeDict[account]["Pitchers"]:
        if not pitcher:
            existedPitchersStats.append(False)
            continue
        if not tableExist:
            pitcher.inlineup = False
        else:
            with engine.begin() as connection:
                query = select(TodayPitcher).where(
                    TodayPitcher.c.player_id == pitcher.player_id
                )
                result = connection.execute(query)
                pitcherStats = result.fetchone()
                if not pitcherStats:
                    pitcher.inlineup = False
                else:
                    pitcher.inlineup = True
                    existedPitcherStats = []
                    for i in range(len(totalPitcherCategories)):
                        existedPitcherStats.append(pitcherStats[i + 3])
                    existedPitchersStats.append(existedPitcherStats)

        pitcher.player_id = str(pitcher.player_id).rjust(4, "0")

    return render_template(
        "player.html",
        account=queryAccount.account,
        fielders=rearrangeDict[account]["Fielders"],
        pitchers=rearrangeDict[account]["Pitchers"],
        totalFielderCategories=totalFielderCategories,
        totalPitcherCategories=totalPitcherCategories,
        selectFielderCategories=selectFielderCategories,
        selectPitcherCategories=selectPitcherCategories,
        existedFieldersStats=existedFieldersStats,
        existedPitchersStats=existedPitchersStats,
        FIELDER_CATEGORIES_TO_TODAY_CATEGORIES=FIELDER_CATEGORIES_TO_TODAY_CATEGORIES,
        PITCHER_CATEGORIES_TO_TODAY_CATEGORIES=PITCHER_CATEGORIES_TO_TODAY_CATEGORIES,
        positionDict=positionDict,
    )


@app.route("/player/update", methods=["POST"])
def playerUpdate():
    global rearrangeDict
    receiveData = request.get_json()
    if receiveData["type"] == "Fielder":
        (
            rearrangeDict[receiveData["account"]]["Fielders"][
                receiveData["active"]["index"]
            ],
            rearrangeDict[receiveData["account"]]["Fielders"][
                receiveData["target"]["index"]
            ],
        ) = (
            rearrangeDict[receiveData["account"]]["Fielders"][
                receiveData["target"]["index"]
            ],
            rearrangeDict[receiveData["account"]]["Fielders"][
                receiveData["active"]["index"]
            ],
        )
        # print(rearrangeQueryFielders)
    else:
        (
            rearrangeDict[receiveData["account"]]["Pitchers"][
                receiveData["active"]["index"]
            ],
            rearrangeDict[receiveData["account"]]["Pitchers"][
                receiveData["target"]["index"]
            ],
        ) = (
            rearrangeDict[receiveData["account"]]["Pitchers"][
                receiveData["target"]["index"]
            ],
            rearrangeDict[receiveData["account"]]["Pitchers"][
                receiveData["active"]["index"]
            ],
        )
        # print(rearrangeQueryPitchers)
    rearrangeDict[receiveData["account"]]["rearrange"] = True
    return jsonify({"message": "Success"})


@app.route("/matchup", methods=["GET", "POST"])
def matchup():
    # 根據league_home頁面的表單內的hidden input
    # 傳入account
    account = request.form["account"]

    # 根據輸入的帳號，提出該帳號名稱對應到的
    # 帳號、對手帳號
    query_account = db.session.query(Account).filter(Account.account == account).first()
    account = query_account.account
    opponent = query_account.opponent

    # 所選的球員
    Fielders, Pitchers = {}, {}
    Fielders["my"] = db.session.query(Fielder).filter(Fielder.Account == account).all()
    Pitchers["my"] = db.session.query(Pitcher).filter(Pitcher.Account == account).all()

    # 取出對手的球員
    Fielders["opp"] = (
        db.session.query(Fielder).filter(Fielder.Account == opponent).all()
    )
    Pitchers["opp"] = (
        db.session.query(Pitcher).filter(Pitcher.Account == opponent).all()
    )

    # 取出所有比項以及盟主選的比項
    categories = {}
    (
        S_fielder_categories,
        S_pitcher_categories,
        _,
        _,
    ) = read_category()

    # T_F:TotalFielders
    # T_P:TotalPitchers
    # S_F:SelectFielders
    # S_P:SelectPitchers
    categories["T_F"] = list(FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["T_P"] = list(PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["S_F"] = S_fielder_categories
    categories["S_P"] = S_pitcher_categories

    # 檢查Table是否已存在db中
    inspector = inspect(engine)
    existedTables = inspector.get_table_names()
    FieldersStats = {}
    PitchersStats = {}

    # 取出紀錄今日成績的Table
    if "TodayFielder" not in existedTables:
        table_exist = False
    else:
        table_exist = True
        TodayFielder = Table("TodayFielder", metadata, autoload_with=engine)
        TodayPitcher = Table("TodayPitcher", metadata, autoload_with=engine)

    # 取出紀錄本週成績的Table
    weeklyStats = Table("WeeklyStats", metadata, autoload_with=engine)
    WeeklyStats = {}
    with engine.begin() as connection:
        # 取出屬於載入matchup路由的帳戶的當週成績
        queryMy = select(weeklyStats).where(weeklyStats.c.account == account)
        result = connection.execute(queryMy)
        WeeklyStats["my"] = result.fetchone()

        # 取出屬於載入matchup路由的帳戶的當週成績
        queryOpp = select(weeklyStats).where(weeklyStats.c.account == opponent)
        result = connection.execute(queryOpp)
        WeeklyStats["opp"] = result.fetchone()

    # 計算自己與對手的Players數量，選擇多的當作在網頁要呈現幾列
    # 如果不足的那邊就會是Empty
    FieldersCount, PitchersCount = {}, {}
    # 手動宣告此聯盟內的Roster Positions
    RosterPositions = {
        "Fielder": ["C", "1B", "2B", "3B", "SS", "OF", "OF", "OF", "OF", "Util"],
        "Pitcher": ["SP", "SP", "SP", "SP", "RP", "RP"],
    }

    # Fielders
    for key, _ in Fielders.items():
        count = 0

        # 存放此帳號所選球員的今日成績
        existed_fielders_stats = []

        # 遍歷所有選的球員
        for fielder in Fielders[key]:
            # inlineup是用來判斷網頁中，有沒有需要顯示資料
            # 注意這邊db內並沒有這個欄位
            # 也就是說可以利用這個方法，建立一個隱藏的欄位，傳給後續的程式使用
            if not table_exist:
                fielder.inlineup = False
            else:
                # 檢查每個自己選到的球員，是否存在TodayFielder這個Table
                # 也就是檢查今天有沒有成績
                with engine.begin() as connection:
                    query = select(TodayFielder).where(
                        TodayFielder.c.player_id == fielder.player_id
                    )
                    result = connection.execute(query)
                    fielder_stats = result.fetchone()

                    if not fielder_stats:
                        fielder.inlineup = False
                    else:
                        fielder.inlineup = True
                        existed_fielder_stats = []

                        # 有成績就遍歷抓取出來的成績，然後加到陣列裡
                        for i in range(len(categories["T_F"])):
                            existed_fielder_stats.append(fielder_stats[i + 3])

                        # 最後把此球員的成績加到此帳號所選的球員內
                        existed_fielders_stats.append(existed_fielder_stats)
            fielder.player_id = str(fielder.player_id).rjust(4, "0")
            count += 1
        FieldersStats[key] = existed_fielders_stats
        FieldersCount[key] = count

    # Pitchers
    for key, _ in Pitchers.items():
        count = 0
        existed_pitchers_stats = []
        for pitcher in Pitchers[key]:
            if not table_exist:
                pitcher.inlineup = False
            else:
                with engine.begin() as connection:
                    query = select(TodayPitcher).where(
                        TodayPitcher.c.player_id == pitcher.player_id
                    )
                    result = connection.execute(query)
                    pitcher_stats = result.fetchone()
                    if not pitcher_stats:
                        pitcher.inlineup = False
                    else:
                        pitcher.inlineup = True
                        existed_pitcher_stats = []
                        for i in range(len(categories["T_P"])):
                            existed_pitcher_stats.append(pitcher_stats[i + 3])
                        existed_pitchers_stats.append(existed_pitcher_stats)

            pitcher.player_id = str(pitcher.player_id).rjust(4, "0")
            count += 1
        PitchersStats[key] = existed_pitchers_stats
        PitchersCount[key] = count
    print(PitchersStats["opp"])

    return render_template(
        "matchup.html",
        account=account,
        opponent=opponent,
        WeeklyStats=WeeklyStats,
        Fielders=Fielders,
        Pitchers=Pitchers,
        categories=categories,
        FieldersStats=FieldersStats,
        PitchersStats=PitchersStats,
        FieldersCount=FieldersCount,
        PitchersCount=PitchersCount,
        FIELDER_CATEGORIES_TO_TODAY_CATEGORIES=FIELDER_CATEGORIES_TO_TODAY_CATEGORIES,
        PITCHER_CATEGORIES_TO_TODAY_CATEGORIES=PITCHER_CATEGORIES_TO_TODAY_CATEGORIES,
        RosterPositions=RosterPositions,
    )


@socketio.on("connect", namespace="/matchup")
def matchup_connect():
    global current_clients
    global started
    current_clients.append(1)
    print(current_clients)
    if not started:
        print("Background start.")
        started = True
        socketio.start_background_task(background_update)


@socketio.on("disconnect", namespace="/matchup")
def matchup_disconnect():
    global started
    global current_clients
    if len(current_clients) == 1:
        started = False
        print("All pages disconnected.")
    current_clients.pop()
    print(current_clients)


# 把今日成績加入本週成績、球季成績
@app.route("/todayupdate", methods=["GET", "POST"])
def todayupdate():
    if request.method == "POST":
        if request.form.get("confirmed", False):
            fielders = Table("Fielder", metadata, autoload_with=engine)
            pitchers = Table("Pitcher", metadata, autoload_with=engine)

            todayfielders = Table("TodayFielder", metadata, autoload_with=engine)
            todaypitchers = Table("TodayPitcher", metadata, autoload_with=engine)

            account = Table("Account", metadata, autoload_with=engine)
            weeklyStats = Table("WeeklyStats", metadata, autoload_with=engine)

            with engine.begin() as connection:
                Fielders = select(todayfielders)
                results = connection.execute(Fielders)
                FieldersResult = results.fetchall()

                query_todayPitchers = select(todaypitchers)
                results = connection.execute(query_todayPitchers)
                PitchersResult = results.fetchall()

                inspector = inspect(engine)
                tableExist = inspector.get_table_names()

                # 更新本季成績
                def seasonUpdate():
                    # Fielder
                    # 取出今日成績的Table
                    for i in range(len(FieldersResult)):
                        # 取出球員對應到的球季成績
                        # FielderResult[i][1] : 今日成績內的某一個球員的player_id
                        query_season = select(fielders).where(
                            fielders.c.player_id == FieldersResult[i][1]
                        )
                        result = connection.execute(query_season)
                        SelectFielder = result.fetchone()

                        # 有可能是本季初登場
                        # 所以球季成績可能還沒有此球員的資料
                        # 如果有的話就用update
                        # 沒有就把今日成績新增到球季成績

                        # 更新
                        if SelectFielder:
                            # 存放要更新球季成績的字典
                            update_dict = {}

                            # 本季成績 + 今日成績 -> 新的本季成績
                            for (
                                key,
                                value,
                            ) in FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                # AVG, OBP, SLB, OPS不能直接加
                                if key not in ["AVG", "OBP", "SLG", "OPS"]:
                                    update_dict[key] = (
                                        getattr(SelectFielder, key)
                                        + FieldersResult[i][value]
                                    )

                            # 因為今日成績沒有一安，因此要額外計算
                            # 1H = H - 2H - 3H - HR
                            update_dict["1H"] = getattr(SelectFielder, "1H") + (
                                FieldersResult[i][7]
                                - FieldersResult[i][8]
                                - FieldersResult[i][9]
                                - FieldersResult[i][10]
                            )
                            # 計算球季AVG, OBP, SLG, OPS
                            # 因為計算這四項整季的成績所需要的數據已經加到update_dict裡面了(加完今日)，所以可以直接用
                            update_dict["AVG"] = round(
                                update_dict["H"] / update_dict["AB"], 3
                            )
                            update_dict["OBP"] = round(
                                (
                                    update_dict["H"]
                                    + update_dict["BB"]
                                    + update_dict["IBB"]
                                    + update_dict["HBP"]
                                )
                                / (
                                    update_dict["AB"]
                                    + update_dict["BB"]
                                    + update_dict["IBB"]
                                    + update_dict["HBP"]
                                    + update_dict["SF"]
                                ),
                                3,
                            )
                            update_dict["SLG"] = round(
                                update_dict["TB"] / update_dict["AB"], 3
                            )
                            update_dict["OPS"] = update_dict["OBP"] + update_dict["SLG"]

                            # 更新
                            update_stmt = (
                                update(fielders)
                                .where(fielders.c.player_id == FieldersResult[i][1])
                                .values(update_dict)
                            )
                            connection.execute(update_stmt)

                        # 新增
                        else:
                            # 存放新增球季成績的字典
                            insert_dict = {}

                            # 加入非stats的欄位
                            insert_dict["player_id"] = FieldersResult[i][1]
                            insert_dict["name"] = FieldersResult[i][2]

                            # 因為今日成績沒有隊伍資訊，所以先用TBD，之後再去DB內修改
                            insert_dict["team"] = "TBD"

                            for (
                                key,
                                value,
                            ) in FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                # AVG, OBP, SLB, OPS不能直接加
                                if key not in ["AVG", "OBP", "SLG", "OPS"]:
                                    insert_dict[key] = FieldersResult[i][value]

                            # 因為今日成績沒有一安，因此要額外計算
                            # 1H = H - 2H - 3H - HR
                            insert_dict["1H"] = (
                                FieldersResult[i][7]
                                - FieldersResult[i][8]
                                - FieldersResult[i][9]
                                - FieldersResult[i][10]
                            )

                            # 計算球季AVG, OBP, SLG, OPS
                            # 因為計算這四項整季的成績所需要的數據已經加到update_dict裡面了(加完今日)，所以可以直接用
                            insert_dict["AVG"] = round(
                                insert_dict["H"] / insert_dict["AB"], 3
                            )
                            insert_dict["OBP"] = round(
                                (
                                    insert_dict["H"]
                                    + insert_dict["BB"]
                                    + insert_dict["IBB"]
                                    + insert_dict["HBP"]
                                )
                                / (
                                    insert_dict["AB"]
                                    + insert_dict["BB"]
                                    + insert_dict["IBB"]
                                    + insert_dict["HBP"]
                                    + insert_dict["SF"]
                                ),
                                3,
                            )
                            insert_dict["SLG"] = round(
                                insert_dict["TB"] / insert_dict["AB"], 3
                            )
                            insert_dict["OPS"] = insert_dict["OBP"] + insert_dict["SLG"]

                            # Account, position, round欄位可以為null，所以不需要設定
                            insert_stmt = insert(fielders).values(insert_dict)
                            connection.execute(insert_stmt)

                    # Pitcher
                    # 取出今日成績的Table

                    for i in range(len(PitchersResult)):
                        query_season = select(pitchers).where(
                            pitchers.c.player_id == PitchersResult[i][1]
                        )
                        result = connection.execute(query_season)
                        SelectPitcher = result.fetchone()

                        if SelectPitcher:
                            update_dict = {}

                            for (
                                key,
                                value,
                            ) in PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                if key == "IP":
                                    # 把局數加總的十進位轉成三進位
                                    IP_sum = (
                                        getattr(SelectPitcher, key)
                                        + PitchersResult[i][3]
                                    )
                                    integer = int(IP_sum)
                                    decimal = IP_sum - integer
                                    if decimal * 10 >= 3:
                                        integer += 1
                                        decimal -= 0.3
                                    update_dict[key] = integer + decimal
                                #
                                elif key == "SV_H":
                                    update_dict["SV+H"] = (
                                        getattr(SelectPitcher, "SV+H")
                                        + PitchersResult[i][value]
                                    )
                                elif key not in ["K9", "ERA", "WHIP"]:
                                    update_dict[key] = (
                                        getattr(SelectPitcher, key)
                                        + PitchersResult[i][value]
                                    )

                            # 因為今日成績沒有APP，但是有出現在今日成績就代表有出場
                            update_dict["APP"] = getattr(SelectPitcher, "APP") + 1

                            # ERA, WHIP, K9另外計算
                            # 防止有投手本季成績為0.0
                            try:
                                # 把三進位的局數轉成十進位，才可以計算
                                IP_decimal = (
                                    int(update_dict["IP"])
                                    + (update_dict["IP"] - int(update_dict["IP"]))
                                    * 10
                                    * 3**-1
                                )
                                update_dict["ERA"] = round(
                                    update_dict["ER"] * 9 / IP_decimal, 2
                                )
                                update_dict["WHIP"] = round(
                                    (update_dict["H"] + update_dict["BB"]) / IP_decimal,
                                    2,
                                )
                                update_dict["K/9"] = round(
                                    update_dict["K"] * 9 / IP_decimal, 2
                                )
                            except ZeroDivisionError:
                                update_dict["ERA"] = 0
                                update_dict["WHIP"] = 0
                                update_dict["K/9"] = 0

                            update_stmt = (
                                update(pitchers)
                                .where(pitchers.c.player_id == PitchersResult[i][1])
                                .values(update_dict)
                            )

                            connection.execute(update_stmt)

                        else:
                            insert_dict = {}

                            # 加入非stats的欄位
                            insert_dict["player_id"] = PitchersResult[i][1]
                            insert_dict["name"] = PitchersResult[i][2]

                            # 因為今日成績沒有隊伍資訊，所以先用TBD，之後再去DB內修改
                            insert_dict["team"] = "TBD"

                            for (
                                key,
                                value,
                            ) in PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.items():
                                # 因為是新增的，IP不會有進位的問題，因此可以直接用Table的資料
                                if key == "SV_H":
                                    insert_dict["SV+H"] = PitchersResult[i][value]
                                elif key not in ["K9", "ERA", "WHIP"]:
                                    insert_dict[key] = PitchersResult[i][value]

                            # 初登場，直接設定
                            insert_dict["APP"] = 1

                            # ERA, WHIP, K9另外計算
                            # 防止有投手本季成績為0.0
                            try:
                                # 把三進位的局數轉成十進位，才可以計算
                                IP_decimal = (
                                    int(insert_dict["IP"])
                                    + (insert_dict["IP"] - int(insert_dict["IP"]))
                                    * 10
                                    * 3**-1
                                )
                                insert_dict["ERA"] = round(
                                    insert_dict["ER"] * 9 / IP_decimal, 2
                                )
                                insert_dict["WHIP"] = round(
                                    (insert_dict["H"] + insert_dict["BB"]) / IP_decimal,
                                    2,
                                )
                                insert_dict["K/9"] = round(
                                    insert_dict["K"] * 9 / IP_decimal, 2
                                )
                            except ZeroDivisionError:
                                insert_dict["ERA"] = 0
                                insert_dict["WHIP"] = 0
                                insert_dict["K/9"] = 0

                            # Account, position, round欄位可以為null，所以不需要設定
                            insert_stmt = insert(pitchers).values(insert_dict)
                            connection.execute(insert_stmt)

                # 更新當週成績
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

                    # 先抓出所有table的欄位，以便後續使用
                    todayFielderColumns = inspector.get_columns("TodayFielder")
                    todayPitcherColumns = inspector.get_columns("TodayPitcher")

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

                        # 查詢此回圈中的帳號
                        query_weekly = select(weeklyStats).where(
                            weeklyStats.c.account == Account.account
                        )
                        result = connection.execute(query_weekly)
                        SelectAccount = result.fetchone()

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

                        # 若有，就要取TodayFielder內，屬於此Account的選手了
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

                            # 先加入Fielder比項
                            for i in range(len(FieldersResult)):
                                # 因為有今日成績的球員，並沒有紀錄該球員所屬的Account
                                # 所以要利用join把有球員所屬的Account，也就是整季成績的Table給載進來
                                # 利用兩者都有的player_id去join
                                query = (
                                    select(todayfielders)
                                    .join(
                                        fielders,
                                        fielders.c.player_id
                                        == todayfielders.c.player_id,
                                    )
                                    .where(
                                        and_(
                                            todayfielders.c.player_id
                                            == FieldersResult[i][1],
                                            fielders.c.Account == Account.account,
                                        )
                                    )
                                )
                                result = connection.execute(query)
                                # 今日成績的所有球員都會被遍歷，但有些球員可能沒人選
                                # 於是會跳過這些沒人選的球員
                                SelectFielder = result.fetchone()
                                if not SelectFielder:
                                    continue

                                # 有被選入到某個Account的球員
                                # 因為回圈內有些地方會跳出，因此宣告一個取index的變數
                                j = 0
                                for todayFielderColumn in todayFielderColumns:
                                    # AVG, OBP, SLG, OPS這四個stats沒法直接加
                                    # 後面再處理
                                    if todayFielderColumn["name"] in [
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

                                    # +3是因為todayFielder的每一列中
                                    # 前三個column分別為db_id, player_id, name
                                    todayTotal[todayFielderColumn["name"]] = (
                                        todayTotal[todayFielderColumn["name"]]
                                        + SelectFielder[j + 3]
                                    )
                                    j += 1

                            # 處理AVG, OBP, SLG, OPS
                            todayTotal["AVG"] = todayTotal["H"] / todayTotal["AB"]
                            todayTotal["OBP"] = (
                                todayTotal["H"]
                                + todayTotal["BB"]
                                + todayTotal["IBB"]
                                + todayTotal["HBP"]
                            ) / (
                                todayTotal["AB"]
                                + todayTotal["BB"]
                                + todayTotal["IBB"]
                                + todayTotal["HBP"]
                                + todayTotal["SF"]
                            )
                            todayTotal["SLG"] = todayTotal["TB"] / todayTotal["AB"]
                            todayTotal["OPS"] = todayTotal["OBP"] + todayTotal["SLG"]

                            # 再加入Pitcher比項
                            for i in range(len(PitchersResult)):
                                query = (
                                    select(todaypitchers)
                                    .join(
                                        pitchers,
                                        pitchers.c.player_id
                                        == todaypitchers.c.player_id,
                                    )
                                    .where(
                                        and_(
                                            todaypitchers.c.player_id
                                            == PitchersResult[i][1],
                                            pitchers.c.Account == Account.account,
                                        )
                                    )
                                )
                                result = connection.execute(query)
                                SelectPitcher = result.fetchone()

                                if not SelectPitcher:
                                    continue

                                # 這邊用-1開始是因為
                                j = 0
                                for todayPitcherColumn in todayPitcherColumns:
                                    # ERA, WHIP, K9這三個比項不直接加
                                    if todayPitcherColumn["name"] in [
                                        "db_id",
                                        "player_id",
                                        "name",
                                    ]:
                                        continue

                                    elif todayPitcherColumn["name"] in [
                                        "ERA",
                                        "WHIP",
                                        "K9",
                                    ]:
                                        j += 1
                                        continue

                                    # **
                                    # 這些欄位會和todayTotal，屬於打者的欄位名稱撞到
                                    # 所以要加上_P
                                    if todayPitcherColumn["name"] in [
                                        "H",
                                        "HR",
                                        "BB",
                                        "HBP",
                                        "K",
                                        "R",
                                    ]:
                                        todayTotal[
                                            todayPitcherColumn["name"] + "_P"
                                        ] = (
                                            todayTotal[
                                                todayPitcherColumn["name"] + "_P"
                                            ]
                                            + SelectPitcher[j + 3]
                                        )
                                    else:
                                        todayTotal[todayPitcherColumn["name"]] = (
                                            todayTotal[todayPitcherColumn["name"]]
                                            + SelectPitcher[j + 3]
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
                            try:
                                # 把三進位的局數轉成十進位，才可以計算
                                IP_decimal = (
                                    int(todayTotal["IP"])
                                    + (todayTotal["IP"] - int(todayTotal["IP"]))
                                    * 10
                                    * 3**-1
                                )
                                todayTotal["ERA"] = round(
                                    todayTotal["ER"] * 9 / IP_decimal, 2
                                )
                                todayTotal["WHIP"] = round(
                                    (todayTotal["H_P"] + todayTotal["BB_P"])
                                    / IP_decimal,
                                    2,
                                )
                                todayTotal["K9"] = round(
                                    todayTotal["K_P"] * 9 / IP_decimal, 2
                                )
                            except ZeroDivisionError:
                                todayTotal["ERA"] = 0
                                todayTotal["WHIP"] = 0
                                todayTotal["K9"] = 0

                            # 以上Account所有選擇的球員之stats都加總完成

                            # 再來還要把原本就在此Table內的數據 + 上今日的成績
                            # 當作最新的本週成績
                            for WeeklyColumn in WeeklyColumns:
                                if WeeklyColumn["name"] in ["id", "account"]:
                                    continue

                                todayTotal[WeeklyColumn["name"]] = todayTotal[
                                    WeeklyColumn["name"]
                                ] + getattr(SelectAccount, WeeklyColumn["name"])

                            # 因為這邊又把本日成績和本週原始成績做相加的動作
                            # 所以那些不能加的欄位要再重新計算一次
                            # AVG, OBP, SLG, OPS
                            todayTotal["AVG"] = todayTotal["H"] / todayTotal["AB"]
                            todayTotal["OBP"] = (
                                todayTotal["H"]
                                + todayTotal["BB"]
                                + todayTotal["IBB"]
                                + todayTotal["HBP"]
                            ) / (
                                todayTotal["AB"]
                                + todayTotal["BB"]
                                + todayTotal["IBB"]
                                + todayTotal["HBP"]
                                + todayTotal["SF"]
                            )
                            todayTotal["SLG"] = todayTotal["TB"] / todayTotal["AB"]
                            todayTotal["OPS"] = todayTotal["OBP"] + todayTotal["SLG"]

                            # ERA, WHIP, K9另外計算
                            # 防止有投手本季成績為0.0
                            try:
                                # 把三進位的局數轉成十進位，才可以計算
                                IP_decimal = (
                                    int(todayTotal["IP"])
                                    + (todayTotal["IP"] - int(todayTotal["IP"]))
                                    * 10
                                    * 3**-1
                                )
                                todayTotal["ERA"] = round(
                                    todayTotal["ER"] * 9 / IP_decimal, 2
                                )
                                todayTotal["WHIP"] = round(
                                    (todayTotal["H_P"] + todayTotal["BB_P"])
                                    / IP_decimal,
                                    2,
                                )
                                todayTotal["K9"] = round(
                                    todayTotal["K_P"] * 9 / IP_decimal, 2
                                )
                            except ZeroDivisionError:
                                todayTotal["ERA"] = 0
                                todayTotal["WHIP"] = 0
                                todayTotal["K9"] = 0

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

                seasonUpdate()
                weeklyUpdate()
            return "更新完成！"
        else:
            return "更新失敗。"
    else:
        return render_template("todayupdate.html")


@app.route("/bootstrap", methods=["GET"])
def bootstrap():
    return render_template("bootstrap.html")


# 主程式
if __name__ == "__main__":
    socketio.run(app)