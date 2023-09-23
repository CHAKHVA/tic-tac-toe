from pydantic import BaseModel
from app.models import Player


class MoveInput(BaseModel):
    move_type: str
    position: int

    class Config:
        orm_mode = True


class GameResult(BaseModel):
    game: str
    winner: str | None = None

    class Config:
        orm_mode = True
