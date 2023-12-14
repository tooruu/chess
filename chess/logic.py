from collections.abc import Generator
from itertools import batched

from pieces import (
    Bishop,
    BoardState,
    BoardStateGetter,
    King,
    Knight,
    Pawn,
    Piece,
    Queen,
    Rook,
    Square,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def parse_fen(fen: str) -> BoardState:
    pieces: dict[str, type[Piece]] = {
        "r": Rook,
        "n": Knight,
        "b": Bishop,
        "q": Queen,
        "k": King,
        "p": Pawn,
    }
    board: BoardState = {}
    for rank, fmt in enumerate(fen.partition(" ")[0].split("/"), -7):
        pos = Square(0, -rank)
        for char in fmt:
            if piece := pieces.get(char.lower()):
                board[pos] = piece(pos, char.isupper())
                pos = pos + (1, 0)
            else:
                for _ in range(int(char)):
                    board[pos] = None
                    pos = pos + (1, 0)
    return board


class Board(BoardStateGetter):
    def __init__(self, fen: str | None):
        self._state: BoardState = (
            parse_fen(fen)
            if fen
            else {Square(row, col): None for row in range(8) for col in range(2, 6)}
        )

    def __iter__(self) -> Generator[Piece, None, None]:
        yield from filter(None, self._state.values())

    def __getitem__(self, key: tuple[int, int] | str) -> Piece | None:
        return self._state.get(Square.from_pos(key) if isinstance(key, str) else key)

    def __str__(self) -> str:
        return "\n".join(
            " ".join(str(self._state[s] or "·") for s in row) for row in batched(self._state, 8)
        )

    def place_piece(self, piece: Piece) -> None:
        self._state[piece.pos] = piece

    def move_piece(self, piece: Piece, dest: Square) -> None:
        self._state[dest] = piece
        self._state[piece.pos] = None
        piece.pos = dest

    def promote[P: Queen | Rook | Bishop | Knight](self, pawn: Pawn, piece_type: type[P]) -> P:
        promoted = piece_type(pawn.pos, pawn.is_white)
        self._state[pawn.pos] = promoted
        return promoted
