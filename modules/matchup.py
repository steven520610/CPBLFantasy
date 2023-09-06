from flask import Blueprint, current_app, request, render_template
from threading import Lock
from .common import *
from sqlalchemy import Table, inspect, select
from .config.info import *

matchupBP = Blueprint("matchup", __name__)

started = False
current_clients = []
background_task = Lock()


@matchupBP.context_processor
def utility_processor():
    def get_max(playersCount):
        max = 0
        for _, value in playersCount.items():
            if value > max:
                max = value
        return max

    return dict(get_max=get_max)


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

        finally:
            background_task.release()


@matchupBP.route("/matchup", methods=["GET", "POST"])
def matchup():
    # 根據league_home頁面的表單內的hidden input
    # 傳入account
    account = request.form["account"]

    # 根據輸入的帳號，提出該帳號名稱對應到的
    # 帳號、對手帳號
    query_account = db.session.query(Account).filter(Account.account == account).first()
    account = query_account.account
    opponent = query_account.opponent

    global rearrangeDict

    # 所選的球員
    Fielders, Pitchers = {}, {}

    Fielders["my"] = rearrangeDict[account]["Fielders"]
    Pitchers["my"] = rearrangeDict[account]["Pitchers"]

    Fielders["opp"] = rearrangeDict[opponent]["Fielders"]
    Pitchers["opp"] = rearrangeDict[opponent]["Pitchers"]

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
        "Fielder": [
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
        ],
        "Pitcher": ["SP", "SP", "SP", "SP", "RP", "RP", "RP", "RP"],
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
