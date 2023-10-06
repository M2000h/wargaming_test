from flask import Flask, render_template, request
from flask_cors import CORS
from game_socket import GameSocket
from models import Player, Game
from typing import Dict
import queue
import uuid
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
CORS(app, origins="*")
gs = GameSocket(app, async_mode='threading',  cors_allowed_origins="*")

lobby_queue = queue.Queue()
players: Dict[str, Player] = {}
games: Dict[str, Game] = {}
rating_table = []


@app.route('/')
def main_page():
    return render_template("index.html")


@gs.on('json_message')
def socket_worker(message):
    sid = request.sid
    logger.info(f"{sid} {message}")
    if 'type' not in message.keys():
        gs.raise_error("message must contain type")
        return

    if message['type'] == 'new_user':
        gs.go_to_lobby()
        gs.add_to_rating_room()
        lobby_queue.put(sid)
        players[sid] = Player(message['nickname'], message["avatar"])
        update_rating_table()

    elif message['type'] == 'move':
        if players[sid].last_game is None:
            gs.raise_error("You are not in game")
            return

        game = games[players[sid].last_game]
        if game.status == "ended":
            gs.raise_error("Game already ended")
            return

        if message['move'] not in ['rock', 'paper', 'scissors']:
            gs.raise_error("Impossible move")
            return

        if game.p1_id == sid and game.p1_move is None:
            game.p1_move = message['move']

        elif game.p2_id == sid and game.p2_move is None:
            game.p2_move = message['move']

    elif message['type'] == 'play_again':
        last_game = games[players[sid].last_game]
        player_2 = last_game.get_opponent(sid)
        if players[sid].last_game == players[player_2].last_game:
            gs.play_again(player_2)
        else:
            gs.raise_error("user already leave this game")

    elif message['type'] == 'new_game':
        gs.go_to_lobby()
        lobby_queue.put(sid)

    elif message['type'] == 'play_again_approve':
        last_game = games[players[sid].last_game]
        player_2 = last_game.get_opponent(sid)
        start_game(sid, player_2)

    updates_check()


def updates_check():
    """
    1. Проверяем количество игроков в лобби. Если игроков больше 1:
    2. Берем из начала очереди игроков и проверяем что они есть в лобби
       (очередь нужна т.к в лобби игроки не упорядочены)
    3. Выводим их из лобби
    4. Создаем для них игру
    :return:
    """
    while gs.count_of_people_in_lobby() > 1:
        # Если есть минимум два активных игрока в лобби
        # То берем их из очереди и проверяем на наличие в лобби (т.к список лобби не упорядочен)
        player_1 = lobby_queue.get()
        while not gs.is_player_connected(player_1):
            player_1 = lobby_queue.get()

        player_2 = lobby_queue.get()
        while not gs.is_player_connected(player_1):
            player_2 = lobby_queue.get()

        gs.leave_lobby(player_1)
        gs.leave_lobby(player_2)
        start_game(player_1, player_2)


def start_game(player_1, player_2):
    game_id = str(uuid.uuid4())
    gs.start_game(game_id, player_1, players[player_2].__dict__)
    gs.start_game(game_id, player_2, players[player_1].__dict__)
    update_rating_table()

    games[game_id] = Game(player_1, player_2)

    players[player_1].last_game = game_id
    players[player_2].last_game = game_id

    gs.start_background_task(game_progress, game_id)


def game_progress(game_id):
    for _ in range(20):
        if not games[game_id].p1_move is None and not games[game_id].p2_move is None:
            break
        time.sleep(.5)

    player_1 = games[game_id].p1_id
    player_2 = games[game_id].p2_id
    player_1_move = games[game_id].p1_move
    player_2_move = games[game_id].p2_move

    if player_1_move == player_2_move:
        players[player_1].draws += 1
        players[player_2].draws += 1
        gs.send_result(player_1, "draw", player_2_move, players[player_2].__dict__)
        gs.send_result(player_2, "draw", player_1_move, players[player_1].__dict__)

    elif (player_1_move, player_2_move) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")] or \
            player_2_move is None:
        players[player_1].wins += 1
        players[player_2].loses += 1
        gs.send_result(player_1, "win", player_2_move, players[player_2].__dict__)
        gs.send_result(player_2, "lose", player_1_move, players[player_1].__dict__)

    else:
        players[player_1].loses += 1
        players[player_2].wins += 1
        gs.send_result(player_1, "lose", player_2_move, players[player_2].__dict__)
        gs.send_result(player_2, "win", player_1_move, players[player_1].__dict__)
    games[game_id].status = "ended"
    update_rating_table()


def update_rating_table():
    sorted_players = sorted(players.values(), key=lambda x: x.wins, reverse=True)
    result = [(player.nickname, player.wins) for player in sorted_players]
    gs.send_rating(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
