from pydantic import BaseModel


class MoveInput(BaseModel):
    type: str
    position: int

    class Config:
        orm_mode = True


class GameResult(BaseModel):
    game: str
    winner: str | None = None

    class Config:
        orm_mode = True
