from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class GameStatus(str, Enum):
    in_progress = "in_progress"
    finished = "finished"


class Player(str, Enum):
    X = "X"
    O = "O"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default=GameStatus.in_progress)
    board = Column(String(length=9), default="         ")
    current_player = Column(String, default=Player.X)

    moves = relationship("Move", back_populates="game")


class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    move_type = Column(String)
    position = Column(Integer)

    game = relationship("Game", back_populates="moves")
