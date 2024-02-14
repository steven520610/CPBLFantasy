# Modified date: 2024.2.14
# Author: Steven
# Description: 實作此app初始化完之後，就要立刻執行的內容，包括
#   1. SQLAlchemy: 處理此app與db的互動
#   2. SocketIO: 處理Client Server間的雙向互動
#   3. 排序db內每個帳號所選的球員如何呈現在roster中
# 以及定義一些在多個網頁中，需要重複使用到的function
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy import create_engine, MetaData, Table, select
from .config.info import *

# 先建立一個SQLAlchemy的instance
db = SQLAlchemy()
# 建立SocketIO object
socketio = SocketIO()
metadata = MetaData()

engine = None
accountTable = None
fielderTable = None
pitcherTable = None


# SQLAlchemy Core 定義的 Model
# 把從db抓取Table的步驟在一開始就執行
# 這樣不用每個路由都重抓一次
def init_db():
    global engine, accountTable, fielderTable, pitcherTable
    engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    accountTable = Table("Account", metadata, autoload_with=engine)
    fielderTable = Table("Fielder", metadata, autoload_with=engine)
    pitcherTable = Table("Pitcher", metadata, autoload_with=engine)


# SQLAlchemy ORM 定義的 Model
class Account(db.Model):
    # 若無設定，預設的table name會被轉成小寫的account
    __tablename__ = "Account"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=True)
    opponent = db.Column(db.String(100), nullable=True)


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
        return return_dict


# 在myteam, player路由中會使用到
# 每個帳號會當作key，裡面包含了該帳號的rearrange, rearrangeQueryFielders, rearrangeQueryPitchers
rearrangeDict = {}
rearrange = False
# 根據球員的position，決定該球員會在網頁的哪一列上，讓該球員會對應到正確的守位格
# 總共有23個格子 (19個正常守位 + 4個BN)
positionDict = {
    # 11
    "Fielder": ["C", "1B", "2B", "3B", "SS", "OF", "OF", "OF", "OF", "Util", "Util"],
    # 8
    "Pitcher": ["SP", "SP", "SP", "SP", "RP", "RP", "RP", "RP"],
}


# 因為當初爬蟲爬取球員資料時
# 是依據隊伍的順序從上爬下來
# 所以db內球員的順序預設就會以隊伍來做排序
# 讓select時也會以隊伍順序從上排下來
# 造成該守位不一定會對應到符合的球員
# 因此需要對該帳號所選的球員
# 根據守位重新排列
def rearrangePlayer(account):
    queryFielders = db.session.query(Fielder).filter(Fielder.Account == account).all()
    queryPitchers = db.session.query(Pitcher).filter(Pitcher.Account == account).all()

    # 宣告該帳號中，有多個該守位的格子已被使用幾個、最多使用幾個
    # 會需要根據不同聯盟、不同管理員設定Roster以及守位的數量去做更動
    Used = {
        "OF": {"Count": 0, "Limit": 4},
        "SP": {"Count": 0, "Limit": 4},
        "RP": {"Count": 0, "Limit": 4},
        "Util": {"Count": 0, "Limit": 2},
    }

    # Fielder
    # 宣告一個用來存調整順序後的球員陣列
    # 長度會等於positionDict對應到球員種類的陣列長度

    # 陣列的每個element若非False，就會是一個ORM Model的instance

    # 因為Fielder和Pitcher在db裡面分開存
    # 所以這邊也分開處理
    rearrangeQueryFielders = [False] * len(positionDict["Fielder"])

    # 額外賦予每個instance "是否已經被分配守位" 這個屬性
    for queryFielder in queryFielders:
        queryFielder.assignPosition = False

    # 宣告當前的fielder、守位之索引值
    fielderIndex = 0
    positionIndex = 0

    # 宣告決定程式流程的一些Bool變數，分別是：
    # 決定所選球員內，是否擁有多守位
    # 決定當前排序時是否在第一輪(因為第一輪會略過多守位球員)
    hasMultiPosition = False
    firstRound = True

    while fielderIndex < len(queryFielders) or hasMultiPosition:
        # 第一輪
        if firstRound:
            # 多守位球員會以 ", " 被隔開多個守位
            # 會先略過多守位球員
            if len(queryFielders[fielderIndex].position.split(", ")) > 1:
                fielderIndex += 1

                # 只要有任一球員是多守位就會設定
                hasMultiPosition = True
                # 最後一個球員被選到後就會重新開始while loop
                if fielderIndex == len(queryFielders):
                    firstRound = False
                    fielderIndex = 0
                continue

            # 第一輪中的非多守位球員

            # 從第一個守位開始選起，遇到符合的守位且該守位目前尚無人使用的話
            # 就會跳出此for回圈
            for position in positionDict["Fielder"]:
                if queryFielders[fielderIndex].position == position:
                    positionIndex = positionDict["Fielder"].index(position)

                    # 若該守位有多個格子的情況
                    if position in Used.keys():
                        # 會先確定有多個格子的守位已經被使用幾個
                        positionIndex += Used[position]["Count"]
                        # 如果使用完的話就會往後，將此球員放到Util或BN
                        if (
                            positionIndex
                            < positionDict["Fielder"].index(position)
                            + Used[position]["Limit"]
                        ):
                            if not rearrangeQueryFielders[positionIndex]:
                                rearrangeQueryFielders[positionIndex] = queryFielders[
                                    fielderIndex
                                ]
                                queryFielders[fielderIndex].assignPosition = True
                                Used[position]["Count"] += 1

                                # 該球員只要某個守位被設定完後
                                # 就可以跳出for loop
                                # 不用再檢查剩餘的守位了
                                # (這邊的剩餘守位是指positionDict中的守位)
                                break

                    # 只有單一格子
                    else:
                        if not rearrangeQueryFielders[positionIndex]:
                            rearrangeQueryFielders[positionIndex] = queryFielders[
                                fielderIndex
                            ]
                            queryFielders[fielderIndex].assignPosition = True
                            break

            # 在所有守位都檢查完而且該球員還沒被分配到格子的情況
            # 就會查看Util格有沒有位置
            if (
                not queryFielders[fielderIndex].assignPosition
                and Used["Util"]["Count"] < 2
            ):
                rearrangeQueryFielders[
                    positionDict["Fielder"].index("Util") + Used["Util"]["Count"]
                ] = queryFielders[fielderIndex]
                Used["Util"]["Count"] += 1
                queryFielders[fielderIndex].assignPosition = True

            # 所有守位以及Util都判斷完，但該球員依舊沒有被分配到格子
            # 就會被分到BN格子
            if not queryFielders[fielderIndex].assignPosition:
                # 每個BN格子都會讓list新增一個element
                rearrangeQueryFielders.append(False)
                rearrangeQueryFielders[-1] = queryFielders[fielderIndex]
                queryFielders[fielderIndex].assignPosition = True

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
                for playerPosition in queryFielders[fielderIndex].position.split(", "):
                    # 這邊和上述大致相同
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
                                        rearrangeQueryFielders[positionIndex] = (
                                            queryFielders[fielderIndex]
                                        )
                                        queryFielders[fielderIndex].assignPosition = (
                                            True
                                        )
                                        Used[position]["Count"] += 1
                                        shouldBreak = True
                                        break
                            if not rearrangeQueryFielders[positionIndex]:
                                rearrangeQueryFielders[positionIndex] = queryFielders[
                                    fielderIndex
                                ]
                                queryFielders[fielderIndex].assignPosition = True
                                shouldBreak = True
                                break

                    # 如果多守位的其中一個守位被成功分配
                    # 就不用再看其他守位了
                    if shouldBreak:
                        break

                if (
                    not queryFielders[fielderIndex].assignPosition
                    and Used["Util"]["Count"] < 2
                ):
                    rearrangeQueryFielders[
                        positionDict["Fielder"].index("Util") + Used["Util"]["Count"]
                    ] = queryFielders[fielderIndex]
                    Used["Util"]["Count"] += 1
                    queryFielders[fielderIndex].assignPosition = True

                if not queryFielders[fielderIndex].assignPosition:
                    rearrangeQueryFielders.append(False)
                    rearrangeQueryFielders[-1] = queryFielders[fielderIndex]
                    queryFielders[fielderIndex].assignPosition = True

            fielderIndex += 1

    # 將該帳號排序完的球員，存到最初宣告的空dict
    rearrangeDict[account]["Fielders"] = rearrangeQueryFielders

    # Pitcher
    rearrangeQueryPitchers = [False] * len(positionDict["Pitcher"])
    # 先賦予每個球員 "是否被分配守位" 這個屬性
    for queryPitcher in queryPitchers:
        queryPitcher.assignPosition = False
    pitcherIndex = 0
    positionIndex = 0
    hasMultiPosition = False
    firstRound = True

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
                rearrangeQueryPitchers.append(False)
                rearrangeQueryPitchers[-1] = queryPitchers[pitcherIndex]
                queryPitchers[pitcherIndex].assignPosition = True

            pitcherIndex += 1
            if pitcherIndex == len(queryPitchers):
                firstRound = False
                pitcherIndex = 0

        else:
            hasMultiPosition = False
            if not queryPitchers[pitcherIndex].assignPosition:
                shouldBreak = False
                for playerPosition in queryPitchers[pitcherIndex].position.split(", "):
                    for position in positionDict["Pitcher"]:
                        if playerPosition == position:
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
                                shouldBreak = True
                                break

                    if shouldBreak:
                        break

                if not queryPitchers[pitcherIndex].assignPosition:
                    rearrangeQueryPitchers.append(False)
                    rearrangeQueryPitchers[-1] = queryPitchers[pitcherIndex]
                    queryPitchers[pitcherIndex].assignPosition = True

            pitcherIndex += 1

    rearrangeDict[account]["Pitchers"] = rearrangeQueryPitchers


def rearrangeAll():
    global accountTable
    with engine.begin() as connection:
        query = select(accountTable).where(accountTable.c.account != "admin")
        results = connection.execute(query)
        accounts = results.fetchall()
    for account in accounts:
        rearrangeDict[account.account] = {}
        rearrangePlayer(account.account)
    global rearrange
    rearrange = True


def score_player(type, player, SCORING_PLAYER, categories):
    score = 0
    for key, value in SCORING_PLAYER.items():
        score += getattr(player, key) * value if key in categories else 0
    if type == "Fielder":
        OPS_plus = ((player.OBP / AVG_OBP) + (player.SLG / AVG_SLG) - 1) * 100
        score += (OPS_plus - 100) * (player.PA / AVG_PA)
    elif type == "Pitcher":
        IPDecimal = int(player.IP) + (player.IP - int(player.IP)) * 3**-1
        score += IPDecimal * 3.6
    return score


def read_category():
    """讀取categories.txt內的比項

    Returns:
        list: fielder_categories,
        list: pitcher_categories,
        int: number of fielder_categories,
        int: number of pitcher_categories
    """
    fielder_categories, pitcher_categories = [], []
    path = "categories.txt"
    # 找出分隔Fielders, Pitchers的位置
    with open(path, "r") as file:
        index = 0
        for line in file.readlines():
            if line.strip() != "-":
                index += 1
            else:
                split_index = index
                break
    # 再重讀一次檔案
    with open(path, "r") as file:
        lines = file.readlines()
        for i in range(1, split_index):
            fielder_categories.append(lines[i].strip())
        for i in range(split_index + 2, len(lines)):
            pitcher_categories.append(lines[i].strip())
    return (
        fielder_categories,
        pitcher_categories,
        len(fielder_categories),
        len(pitcher_categories),
    )
