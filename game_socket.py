from typing import List, Tuple, Dict

from flask_socketio import SocketIO, join_room, leave_room, emit


class GameSocket(SocketIO):
    """ Сервер для общения с игроками через сокеты

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def start_game(player_id: str, opponent: Dict[str, object]) -> None:
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

    def send_result(self, player_id: str, result: str, opponent_move: str, opponent: Dict[str, object]) -> None:
        """ Отправка результата игры

        :param player_id:
        :param result:
        :param opponent_move:
        :param opponent:
        """
        self.emit(
            "json_response",
            {
                "type": "game_result",
                "result": result,
                "opponent_move": opponent_move,
                "opponent": opponent,
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
