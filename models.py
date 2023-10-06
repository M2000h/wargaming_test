from dataclasses import dataclass


@dataclass
class Player:
    nickname: str
    avatar: str
    wins: int = 0
    draws: int = 0
    loses: int = 0
    last_game: str = None


@dataclass
class Game:
    p1_id: str
    p2_id: str
    p1_move: str = None
    p2_move: str = None
    status: str = "coming"

    def get_opponent(self, player_id):
        return self.p1_id if self.p1_id != player_id else self.p2_id
