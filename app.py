from flask import Flask, render_template
from flask_cors import CORS

from game_socket import GameSocket
from models import GameServer

app = Flask(__name__)
CORS(app, origins="*")
server = GameServer({}, {})
gs = GameSocket(server, app, async_mode="threading", cors_allowed_origins="*")


@app.route("/")
def main_page() -> str:
    """ Сборка всех блоков в единую страницу

    :return: html page
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
