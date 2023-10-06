from flask_socketio import SocketIO, join_room, leave_room, emit


class GameSocket(SocketIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def raise_error(self, massage):
        self.emit('json_response', {"type": "error", "message": massage})

    @staticmethod
    def go_to_lobby():
        join_room("lobby")

    @staticmethod
    def add_to_rating_room():
        join_room("rating_room")

    def send_rating(self, rating_table):
        self.emit('json_response', {"type": "update_rating", "table": rating_table}, room="rating_room")

    @staticmethod
    def leave_lobby(player):
        leave_room("lobby", player)

    @staticmethod
    def play_again(player):
        emit('json_response', {"type": "play_again"}, room=player)

    @staticmethod
    def start_game(game_id, player_id, opponent):
        emit('json_response',
             {
                 "type": "start_game",
                 "game_id": game_id,
                 "opponent": opponent,
             },
             room=player_id)

    def send_result(self, player_id, result, opponent_move, opponent):
        self.emit('json_response',
                  {
                      "type": "game_result",
                      "result": result,
                      "opponent_move": opponent_move,
                      "opponent": opponent,
                  },
                  room=player_id)

    def count_of_people_in_lobby(self):
        if 'lobby' in self.server.manager.rooms['/'].keys():
            return len(self.server.manager.rooms['/']['lobby'])
        return 0

    def is_player_connected(self, player):
        if 'lobby' in self.server.manager.rooms['/'].keys() and \
                player in self.server.manager.rooms['/']['lobby'].keys():
            return True
        return False
