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

    # 因為是在server一啟動就要處理，還沒有收到任何user端送來的請求
    # 也就是一啟動時，並不在任何的上下文(路由)中
    # 因此需要透過這個方法，手動建立一個上下文
    # 否則會報RunTime Error
    with app.app_context():
        init_db()
        db.init_app(app)
        socketio.init_app(app, cors_allowed_origins="http://127.0.0.1:5000")
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
