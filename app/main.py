from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from app.models import *

from app.schemas import GameResult, MoveInput
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/start", response_model=dict)
def start_game(db: Session = Depends(get_db)):
    game = Game()
    db.add(game)
    db.commit()
    db.refresh(game)
    return {"game_id": game.id}


@app.post("/move/{game_id}", response_model=GameResult)
def make_move(
    *,
    game_id: int = Path(..., description="Game ID"),
    move: MoveInput,
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.id == game_id).first()

    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    if str(game.status) == GameStatus.finished:
        db.close()
        return {"game": "finished", "winner": game.current_player}

    if move.position < 0 or move.position > 8:
        db.close()
        raise HTTPException(status_code=400, detail="Invalid position")

    board = list(str(game.board))
    if board[move.position] != " ":
        db.close()
        raise HTTPException(status_code=400, detail="Invalid position")

    board[move.position] = move.move_type
    game.board = "".join(board)

    # Check for a winner
    if check_winner(board, move.move_type):
        game.status = GameStatus.finished
        game_result = {"game": "finished", "winner": move.move_type}
    elif " " not in board:
        game.status = GameStatus.finished
        game_result = {"game": "finished", "winner": None}
    else:
        game.current_player = Player.X if move.move_type == "O" else Player.O
        game_result = {"game": "in_progress"}

    move_db = Move(game_id=game.id, move_type=move.move_type, position=move.position)
    db.add(move_db)
    db.commit()
    db.close()

    return game_result


@app.get("/check/{game_id}", response_model=GameResult)
def check_game(
    game_id: int = Path(..., description="Game ID"), db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.id == game_id).first()

    if game is None:
        db.close()
        raise HTTPException(status_code=404, detail="Game not found")

    if str(game.status) == GameStatus.in_progress:
        db.close()
        return {"game": "in_progress"}

    db.close()
    return {"game": "finished", "winner": game.current_player}


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    game_history = {}

    for game in games:
        moves = db.query(Move).filter(Move.game_id == game.id).all()
        move_list = [
            {"type": move.move_type, "position": move.position} for move in moves
        ]
        game_history[game.id] = {
            "moves": move_list,
        }

    db.close()
    return game_history


def check_winner(board, player):
    winning_combinations = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    for combo in winning_combinations:
        if all(board[i] == player for i in combo):
            return True
    return False
