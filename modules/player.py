# Modified date: 2024.2.16
# Author: Steven
# Description: 處理player路由中
# 所有使用到的功能
from flask import Blueprint, current_app, request, render_template
from .common import (
    db,
    engine,
    accountTable,
    Fielder,
    Pitcher,
    score_player,
    read_category,
    rearrangeDict,
)
from sqlalchemy import select
from .config.info import *

playerBP = Blueprint("player", __name__)


@playerBP.route("/player", methods=["GET", "POST"])
def player():
    myAccount = request.form["account"]

    def accountsToList(accounts):
        accountsList = []
        for account in accounts:
            accountsList.append(account.account)
        return accountsList

    def playersToList(players):
        playersList = []
        for player in players:
            playerDict = {}
            for c in player.__table__.columns:
                if c.name == "db_id":
                    continue
                elif c.name == "1H":
                    playerDict[c.name] = getattr(player, "H1")
                elif c.name == "2H":
                    playerDict[c.name] = getattr(player, "H2")
                elif c.name == "3H":
                    playerDict[c.name] = getattr(player, "H3")
                elif c.name == "SV+H":
                    playerDict[c.name] = getattr(player, "SV_H")
                elif c.name == "K/9":
                    playerDict[c.name] = getattr(player, "K9")
                else:
                    playerDict[c.name] = getattr(player, c.name)
            playerDict["Rank"] = getattr(player, "Rank")
            playerDict["show"] = getattr(player, "show")
            playersList.append(playerDict)
        return playersList

    with engine.begin() as connection:
        queryAccount = select(accountTable).where(accountTable.c.account != "admin")
        accounts = connection.execute(queryAccount)
        accounts = accountsToList(accounts)

        fielders = db.session.query(Fielder).all()
        pitchers = db.session.query(Pitcher).all()

    players = fielders + pitchers

    categories = {}
    selectedFielderCategories, selectedPitcherCategories, _, _ = read_category()
    categories["T_F"] = list(FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["T_P"] = list(PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["S_F"] = selectedFielderCategories
    categories["S_P"] = selectedPitcherCategories
    for i, player in enumerate(
        sorted(
            players,
            key=lambda p: (
                score_player("Fielder", p, SCORING_FIELDER, selectedFielderCategories)
                if isinstance(p, Fielder)
                else score_player(
                    "Pitcher", p, SCORING_PITCHER, selectedPitcherCategories
                )
            ),
            reverse=True,
        ),
        start=1,
    ):
        player.player_id = str(player.player_id).rjust(4, "0")
        player.Rank = i
        player.show = True

    fielders = sorted(fielders, key=lambda fielder: fielder.Rank, reverse=False)
    pitchers = sorted(pitchers, key=lambda pitcher: pitcher.Rank, reverse=False)

    fielders = playersToList(fielders)
    pitchers = playersToList(pitchers)

    return render_template(
        "player.html",
        myAccount=myAccount,
        accounts=accounts,
        categories=categories,
        fielders=fielders,
        pitchers=pitchers,
    )


# 在玩家於player頁面，按下某個球員的+號時
# 會經由javascript的處理
# 並利用<a>標籤，來對此路由發出帶有queryString的GET請求
@playerBP.route("/addplayer", methods=["GET"])
def addplayer():
    def playersToList(players):
        playersList = []
        for player in players:
            try:
                playerDict = {}
                for c in player.__table__.columns:
                    if c.name == "db_id":
                        continue
                    elif c.name == "1H":
                        playerDict[c.name] = getattr(player, "H1")
                    elif c.name == "2H":
                        playerDict[c.name] = getattr(player, "H2")
                    elif c.name == "3H":
                        playerDict[c.name] = getattr(player, "H3")
                    elif c.name == "SV+H":
                        playerDict[c.name] = getattr(player, "SV_H")
                    elif c.name == "K/9":
                        playerDict[c.name] = getattr(player, "K9")
                    else:
                        playerDict[c.name] = getattr(player, c.name)
                playerDict["show"] = True
            except AttributeError:
                continue
            playersList.append(playerDict)
        return playersList

    # 轉換成dict的原因是
    # JavaScript沒辦法直接使用Python傳過去之某table的物件
    # 因此要用dict的方式然後再轉成JSON來處理。
    def selectPlayerToDict(player):
        playerDict = {}
        for c in player.__table__.columns:
            if c.name == "db_id":
                continue
            elif c.name == "1H":
                playerDict[c.name] = getattr(player, "H1")
            elif c.name == "2H":
                playerDict[c.name] = getattr(player, "H2")
            elif c.name == "3H":
                playerDict[c.name] = getattr(player, "H3")
            elif c.name == "SV+H":
                playerDict[c.name] = getattr(player, "SV_H")
            elif c.name == "K/9":
                playerDict[c.name] = getattr(player, "K9")
            else:
                playerDict[c.name] = getattr(player, c.name)
        return playerDict

    account = request.args.get("account")
    player_id = request.args.get("pid")
    selectPlayerFA = (
        db.session.query(Fielder).filter(Fielder.player_id == player_id).first()
    )
    if not selectPlayerFA:
        selectPlayerFA = (
            db.session.query(Pitcher).filter(Pitcher.player_id == player_id).first()
        )

    categories = {}
    selectedFielderCategories, selectedPitcherCategories, _, _ = read_category()
    categories["T_F"] = list(FIELDER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["T_P"] = list(PITCHER_CATEGORIES_TO_TODAY_CATEGORIES.keys())
    categories["S_F"] = selectedFielderCategories
    categories["S_P"] = selectedPitcherCategories

    fielders = rearrangeDict[account]["Fielders"]
    pitchers = rearrangeDict[account]["Pitchers"]

    fielders = playersToList(fielders)
    pitchers = playersToList(pitchers)

    selectPlayerFA = selectPlayerToDict(selectPlayerFA)

    return render_template(
        "addplayer.html",
        fielders=fielders,
        pitchers=pitchers,
        selectPlayerFA=selectPlayerFA,
        myAccount=account,
        player_id=player_id,
        categories=categories,
    )


@playerBP.route("/dropplayer", methods=["GET"])
def dropplayer():
    account = request.args.get("account")
    player_id = request.args.get("pid")
    return "0"
