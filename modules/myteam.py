# Modified date: 2024.2.14
# Author: Steven
# Description: 處理myteam路由中
# 所有使用到的功能

from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from .common import (
    Fielder,
    Pitcher,
    Account,
    db,
    metadata,
    engine,
    fielderTable,
    pitcherTable,
    rearrangeDict,
    positionDict,
    rearrangePlayer,
    read_category,
)
from .config.info import *
from sqlalchemy import Table, select, update, inspect, Connection

myteamBP = Blueprint("myteam", __name__)


# 為了在jinja2內使用isinstance這個功能
# 需要加上的地方
@myteamBP.app_template_filter()
def isinstance_filter(obj, class_name):
    if class_name == "Fielder":
        return isinstance(obj, Fielder)
    elif class_name == "Pitcher":
        return isinstance(obj, Pitcher)
    else:
        import builtins

        type_fn = getattr(builtins, class_name, None)
        return isinstance(obj, type_fn)


# 球員頁面
@myteamBP.route("/myteam", methods=["GET", "POST"])
def myteam():
    account = request.form["account"]
    # player頁面中的addplayer路由
    # 表單才會傳下面這些資料給此路由
    try:
        todayFielder = Table("TodayFielder", metadata, autoload_with=engine)
        todayPitcher = Table("TodayPitcher", metadata, autoload_with=engine)

        def inToday(connection: Connection, ID, type):
            if type == "Fielder":
                query = select(todayFielder).where(todayFielder.c.player_id == ID)
            else:
                query = select(todayPitcher).where(todayPitcher.c.player_id == ID)
            result = connection.execute(query).fetchone()

            return True if result else False

        def updatePlayer(connection: Connection, type, id, account=None):
            if type == "Fielder":
                updateStmt = update(fielderTable).where(fielderTable.c.player_id == id)
            else:
                updateStmt = update(pitcherTable).where(pitcherTable.c.player_id == id)

            updateStmt = updateStmt.values(Account=account)
            connection.execute(updateStmt)

        addPlayerID = int(request.form["addPlayer"])
        addPlayerType = request.form["addPlayerType"]
        dropPlayerID = int(request.form["dropPlayer"])
        dropPlayerType = request.form["dropPlayerType"]
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                # 先判斷add/drop的球員是否已經在today的Table裡
                # 只要存在，就代表該球員已經開始比賽了
                # 因此就不能再對該球員add/drop
                if inToday(connection, addPlayerID, addPlayerType) or inToday(
                    connection, dropPlayerID, dropPlayerType
                ):
                    return redirect(url_for("other.error", account=account))
                else:
                    # 有傳account的話代表是add
                    # 沒有傳代表是drop

                    # 此處add進來的球員，round不會有值，依然會是NULL
                    # 而drop的球員，只是把Account設成NULL，但round還是原本選秀的順位。

                    updatePlayer(connection, addPlayerType, addPlayerID, account)
                    updatePlayer(connection, dropPlayerType, dropPlayerID)
                transaction.commit()
                # 球員交換過後，會再把該帳號的所有球員重新排列一次
                rearrangePlayer(account)
            except:
                transaction.rollback()
                raise RuntimeError("DB操作時發生錯誤！")

    except KeyError:
        pass
    queryAccount = db.session.query(Account).filter(Account.account == account).first()

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

    # 用來存登入此帳號的使用者所擁有且今日有出賽球員的成績
    existedFieldersStats, existedPitchersStats = [], []

    if "TodayFielder" not in existedTables:
        tableExist = False
    else:
        tableExist = True
        # Core
        TodayFielder = Table("TodayFielder", metadata, autoload_with=engine)
        TodayPitcher = Table("TodayPitcher", metadata, autoload_with=engine)

    for fielder in rearrangeDict[account]["Fielders"]:
        # rearrange中，有可能該格子沒辦法放目前所選的球員
        # 該element的值會是False
        if not fielder:
            existedFieldersStats.append(False)
            continue
        # 如果紀錄今日成績的Table不存在，可確定該球員也一定不會有今日出賽的紀錄
        # 對Fielder instance加上一個額外的屬性
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
        # 目的是要讓後面用超連結連到CPBL官網球員頁面時使用
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
        "myteam.html",
        myAccount=queryAccount.account,
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


# 接收當user交換不同格子的選手時
# 所發送出來的AJAX請求
@myteamBP.route("/myteam/update", methods=["POST"])
def myteamUpdate():
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
    rearrangeDict[receiveData["account"]]["rearrange"] = True
    return jsonify({"message": "Success"})
