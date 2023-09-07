from modules import create_app, socketio
from flask import render_template

app = create_app()


# 建立一個全域的404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("page_not_found.html"), 404


if __name__ == "__main__":
    socketio.run(app)
