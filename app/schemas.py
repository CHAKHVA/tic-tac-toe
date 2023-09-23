from pydantic import BaseModel
from app.models import Player


class MoveInput(BaseModel):
    type: Player
    position: int

    class Config:
        orm_mode = True


class GameResult(BaseModel):
    game: str
    winner: str | None = None

    class Config:
        orm_mode = True
