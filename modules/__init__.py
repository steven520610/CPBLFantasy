# Modified date: 2023.2.14
# Author: Steven
# Description: 利用Python獨特的方法，來初始化modules這個package，
# 決定app在此處如何建立app物件
# 並執行一些初始完後，就要馬上執行的動作。

from flask import Flask
from flask_cors import CORS
from .config.info import *
from .common import *


def create_app():
    """
    初始化Flask app
    並將app與SQLAlchemy instance綁定

    Returns:
        Flask: 使用的Flask app
    """
    app = Flask(
        __name__,
        static_folder="../static",
        static_url_path="/",
        template_folder="../templates",
    )
    # 從外部的py檔案，設定app的config
    app.config.from_pyfile("config/config.py")
    app.debug = True

    # 因為在server一啟動就要處理，此時還沒有收到任何user端送來的請求
    # 也就是一啟動時，並不在任何的上下文(request context)中
    # 因此需要透過這個方法，手動建立一個應用上下文(application context)
    # 否則會報RunTime Error
    with app.app_context():
        # 此處分別用兩種方式建立與db的連結
        # 第一個是用Core component
        init_db()
        # 第二個是ORM component
        # 兩者會處理不同的任務，主要原因是有些操作只能透過其中一個component來完成。
        db.init_app(app)
        socketio.init_app(app, cors_allowed_origins="http://127.0.0.1:5000")
        # 每一次重啟app，都會做此步驟
        # 因為在db內，球員的排列是所有球員依據隊伍去排的，各個帳號所選的球員也是依照這個方法排列
        # 然而在登入後，我想要在user進到自己所選球員的頁面時，就顯示排列正確的roster
        # 因此在每一次啟動app時，就進行排列的動作。
        rearrangeAll()

    from .other import otherBP
    from .myteam import myteamBP, isinstance_filter
    from .matchup import matchupBP
    from .draft import draftBP
    from .player import playerBP

    # 註冊模塊Blueprint
    app.register_blueprint(otherBP)
    app.register_blueprint(myteamBP)
    # 將原本在app直接使用app.instance_filter
    # 改成從Blueprint instance中取得的方法
    app.jinja_env.filters["isinstance"] = isinstance_filter
    app.register_blueprint(matchupBP)
    app.register_blueprint(draftBP)
    app.register_blueprint(playerBP)

    CORS(app)  # 在開發環境下，這可以避免因為跨域問題導致的錯誤
    return app
