from flask import Blueprint, render_template, request, jsonify
from .common import db, Account, Fielder, Pitcher, score_player, socketio
from .config.info import *

draftBP = Blueprint("draft", __name__)


@draftBP.context_processor
def utility_processor():
    def get_attribute(obj, attr):
        return getattr(obj, attr)

    return dict(get_attribute=get_attribute)


@draftBP.route("/draft", methods=["GET", "POST"])
def draft():
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
            key=lambda p: score_player(
                "Fielder", p, SCORING_FIELDER, fielder_categories
            )
            if isinstance(p, Fielder)
            else score_player("Pitcher", p, SCORING_PITCHER, pitcher_categories),
            reverse=True,
        ),
        start=1,
    ):
        player.Rank = i
    players = sorted(players, key=lambda player: player.Rank, reverse=False)
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
            "Util",
            "BN",
            "BN",
            "BN",
            "BN",
        ],
        "pitchers": [
            "SP",
            "SP",
            "SP",
            "SP",
            "RP",
            "RP",
            "RP",
            "RP",
            "BN",
            "BN",
            "BN",
            "BN",
        ],
    }
    return render_template(
        "draft.html",
        myAccount=request.form["account"],
        accounts=query_account,
        players=players,
        fielder_categories=fielder_categories,
        pitcher_categories=pitcher_categories,
        positions=positions,
    )


# 選秀頁面，接收user端請求選秀的時間
@draftBP.route("/draft/time", methods=["GET"])
def time():
    from datetime import datetime, timedelta

    # draft_time = datetime.now() + timedelta(hours=1)
    draft_time = datetime(2023, 8, 25, 13, 53, 45)
    return jsonify({"Time": draft_time.isoformat("T", "seconds")})


time_flag = False


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
@draftBP.route("/draft/teams", methods=["POST"])
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
