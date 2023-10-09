from typing import List, Tuple, Dict
import uuid
import time

from flask import request
from flask_socketio import SocketIO, join_room, leave_room, emit

from models import Player, Game, GameServer
from const import GAME_DURATION, logger


class GameSocket(SocketIO):
    """ Сервер для общения с игроками через сокеты
    Т.к вся логика игры завязана на сокеты данный сервер реализует
    в себе все методы для проведения игры.
    """

    def __init__(self, game_server: GameServer, *args, **kwargs) -> None:
        self.game_server = game_server
        super().__init__(*args, **kwargs)
        self.on_event("json_message", self.socket_worker)

    def raise_error(self, massage: str) -> None:
        """ Возвращает ошибку
        :param massage: human-readable ошибка
        """
        self.emit("json_response", {"type": "error", "message": massage})

    @staticmethod
    def go_to_lobby() -> None:
        """ Добавляет игрока в лобби
        Работает в контексте текущего запроса.
        """
        join_room("lobby")

    @staticmethod
    def add_to_rating_room() -> None:
        """ Добавляет игрока в комнату рассылки результатов
        Комната статична, покинуть ее игроки могут только отключившись от игры
        """
        join_room("rating_room")

    def send_rating(self, rating_table: List[Tuple[str, int]]) -> None:
        """ Рассылка рейтингов

        :param rating_table: таблица в формате [(никнейм, рейтинг), ]
        """
        self.emit(
            "json_response",
            {"type": "update_rating", "table": rating_table},
            room="rating_room",
        )

    @staticmethod
    def leave_lobby(player: str) -> None:
        """ Выход из лобби
        Пока вызывается только в случае начала игры.
        :param player: id игрока
        :return:
        """
        leave_room("lobby", player)

    @staticmethod
    def play_again(player: str) -> None:
        """ Отправка игроку запрос реванше

        :param player: id игрока
        """
        emit("json_response", {"type": "play_again"}, room=player)

    @staticmethod
    def send_new_game(player_id: str, opponent: Dict[str, object]) -> None:
        """ Начало игры
        Отправляем игроку информацию о начале игры и его оппоненте
        :param player_id:
        :param opponent:
        :return:
        """
        emit(
            "json_response",
            {
                "type": "start_game",
                "opponent": opponent,
            },
            room=player_id,
        )

    def send_result(self, player_id: str, result: str, opponent_move: str or None) -> None:
        """ Отправка результата игры

        :param player_id:
        :param result:
        :param opponent_move:
        """
        self.emit(
            "json_response",
            {
                "type": "game_result",
                "result": result,
                "opponent_move": opponent_move,
            },
            room=player_id,
        )

    def count_of_people_in_lobby(self) -> int:
        """ Проверка подключенных к лобби людей

        :return: Количество людей в лобби
        """
        if "lobby" in self.server.manager.rooms["/"].keys():
            return len(self.server.manager.rooms["/"]["lobby"])
        return 0

    def is_player_connected(self, player: str) -> bool:
        """ Проверка наличия человека в лобби

        :param player:
        :return: True/False
        """
        if (
                "lobby" in self.server.manager.rooms["/"].keys()
                and player in self.server.manager.rooms["/"]["lobby"].keys()
        ):
            return True
        return False

    def socket_worker(self, message: Dict[str, str], sid = None) -> None:
        """Обработчик входящих сообщений
        Типы сообщений::
           new_user - пользователь регистрируется и попадает в лобби
           move - пользователь делает ход в игре
           play_again - пользователь предлагает реванш
           new_game - пользователь возвращается в лобби для новой игры
           play_again_approve - пользователь соглашается на реванш

        :param message: json сообщение
        :param sid: debug переменна вместо request.sid для тестов
        """
        sid = sid or request.sid
        logger.info(f"{sid} {message}")
        if "type" not in message.keys():
            self.raise_error("message must contain type")
            return

        if message["type"] == "new_user":
            self.go_to_lobby()
            self.add_to_rating_room()
            self.game_server.lobby_queue.put(sid)
            self.game_server.players[sid] = Player(message["nickname"], message["avatar"])
            self.update_rating_table()

        elif message["type"] == "move":
            if self.game_server.players[sid].last_game is None:
                self.raise_error("You are not in game")
                return

            game = self.game_server.games[self.game_server.players[sid].last_game]
            if game.status == "ended":
                self.raise_error("Game already ended")
                return

            if message["move"] not in ["rock", "paper", "scissors"]:
                self.raise_error("Impossible move")
                return

            if game.p1_id == sid and game.p1_move is None:
                game.p1_move = message["move"]

            elif game.p2_id == sid and game.p2_move is None:
                game.p2_move = message["move"]

        elif message["type"] == "play_again":
            last_game = self.game_server.games[self.game_server.players[sid].last_game]
            player_2 = last_game.get_opponent(sid)
            if self.game_server.players[sid].last_game == self.game_server.players[player_2].last_game:
                self.play_again(player_2)
            else:
                self.raise_error("user already leave this game")

        elif message["type"] == "new_game":
            self.go_to_lobby()
            self.game_server.lobby_queue.put(sid)

        elif message["type"] == "play_again_approve":
            last_game = self.game_server.games[self.game_server.players[sid].last_game]
            player_2 = last_game.get_opponent(sid)
            self.start_game(sid, player_2)

        self.updates_check()

    def update_rating_table(self) -> None:
        """Обновление глобального рейтинга

        Это функция обновляет список рейтинга и рассылает его игрокам
        """
        sorted_players = sorted(self.game_server.players.values(), key=lambda x: x.wins, reverse=True)
        result = [(player.nickname, player.wins) for player in sorted_players]
        self.send_rating(result)

    def updates_check(self) -> None:
        """Метчинг игроков из лобби

        Функция вызывается при регистрации появлении новых игроков в лобби

        1. Проверяем количество игроков в лобби. Если игроков больше 1:
        2. Берем из начала очереди игроков и проверяем что они есть в лобби
           (очередь нужна т.к в лобби игроки не упорядочены)
        3. Выводим их из лобби
        4. Создаем для них игру
        """
        while self.count_of_people_in_lobby() > 1:
            # Если есть минимум два активных игрока в лобби
            # То берем их из очереди и проверяем на наличие в лобби (т.к список лобби не упорядочен)
            player_1 = self.game_server.lobby_queue.get()
            while not self.is_player_connected(player_1):
                player_1 = self.game_server.lobby_queue.get()

            player_2 = self.game_server.lobby_queue.get()
            while not self.is_player_connected(player_2):
                player_2 = self.game_server.lobby_queue.get()

            self.leave_lobby(player_1)
            self.leave_lobby(player_2)
            self.start_game(player_1, player_2)

    def start_game(self, player_1: str, player_2: str) -> None:
        """Начало игры

        Функция рассылает уведомления игрокам и создает игру
        :param player_1:
        :param player_2:
        :return:
        """
        game_id = str(uuid.uuid4())
        self.send_new_game(player_1, self.game_server.players[player_2].__dict__)
        self.send_new_game(player_2, self.game_server.players[player_1].__dict__)
        self.update_rating_table()

        self.game_server.games[game_id] = Game(player_1, player_2)

        self.game_server.players[player_1].last_game = game_id
        self.game_server.players[player_2].last_game = game_id

        self.start_background_task(self.game_progress, game_id)

    def game_progress(self, game_id: str) -> None:
        """Проведение игры

        Функция каждые .5 секунды проверяет сделали ли оба игрока ход.
        Если оба игрока сделали ход или время закончилось, игра завершается,
        определяется победитель, игрокам рассылаются результаты, обновляются рейтинги.
        :param game_id:
        """
        for _ in range(GAME_DURATION * 2):
            if not self.game_server.games[game_id].p1_move is None and not self.game_server.games[game_id].p2_move is None:
                break
            time.sleep(0.5)

        player_1 = self.game_server.games[game_id].p1_id
        player_2 = self.game_server.games[game_id].p2_id
        player_1_move = self.game_server.games[game_id].p1_move
        player_2_move = self.game_server.games[game_id].p2_move

        if player_1_move == player_2_move:
            self.game_server.players[player_1].draws += 1
            self.game_server.players[player_2].draws += 1
            self.send_result(player_1, "draw", player_2_move)
            self.send_result(player_2, "draw", player_1_move)

        elif (player_1_move, player_2_move) in [
            ("rock", "scissors"),
            ("paper", "rock"),
            ("scissors", "paper"),
        ] or player_2_move is None:
            self.game_server.players[player_1].wins += 1
            self.game_server.players[player_2].loses += 1
            self.send_result(player_1, "win", player_2_move)
            self.send_result(player_2, "lose", player_1_move)

        else:
            self.game_server.players[player_1].loses += 1
            self.game_server.players[player_2].wins += 1
            self.send_result(player_1, "lose", player_2_move)
            self.send_result(player_2, "win", player_1_move)
        self.game_server.games[game_id].status = "ended"
        self.update_rating_table()
