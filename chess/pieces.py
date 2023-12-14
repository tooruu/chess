from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from itertools import product
from typing import NamedTuple, Protocol, Self, override


class BoardStateGetter(Protocol):
    def __getitem__(self, key: tuple[int, int]) -> Piece | None:
        ...


type BoardState = dict[tuple[int, int], Piece | None]


SYMBOLS: dict[str, str] = {
    "r": "♜",
    "n": "♞",
    "b": "♝",
    "q": "♛",
    "k": "♚",
    "p": "♟",
    "R": "♖",
    "N": "♘",
    "B": "♗",
    "Q": "♕",
    "K": "♔",
    "P": "♙",
}


class SlidingPieceMixin:
    def get_directional_moves(
        self: Piece, board: BoardStateGetter, pos: Square, deltas: Iterable[tuple[int, int]]
    ) -> set[Square]:
        moves = set[Square]()
        for delta in deltas:
            square = pos
            while (square := square + delta).valid:
                moves.add(square)
                if board[square]:
                    break
        return moves


class Square(NamedTuple):
    file: int
    rank: int

    def __str__(self) -> str:
        return f"{'ABCDEFGH'[self.file]}{self.rank+1}"

    def __add__(self, other: tuple[int, int]) -> Self:
        return type(self)(self.file + other[0], self.rank + other[1])

    def __sub__(self, other: tuple[int, int]) -> Self:
        return type(self)(self.file - other[0], self.rank - other[1])

    @property
    def valid(self) -> bool:
        return 0 <= self.file < 8 and 0 <= self.rank < 8

    @classmethod
    def from_pos(cls, pos: str) -> Self:
        return cls("ABCDEFGH".index(pos[0].upper()), int(pos[1]) - 1)


class Piece(Protocol):
    pos: Square
    is_white: bool

    def __init__(self, pos: Square, is_white: bool) -> None:
        self.pos = pos
        self.is_white = is_white

    @abstractmethod
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        ...

    def get_moves(self, board: BoardStateGetter) -> set[Square]:
        return {
            s
            for s in self._generate_moves(board)
            if s.valid and (not (dest := board[s]) or dest.is_white is not self.is_white)
        }

    def __str__(self) -> str:
        name = type(self).__name__
        char = name[name == "Knight"]
        return SYMBOLS[char.upper() if self.is_white else char.lower()]

    @property
    def type(self) -> str:
        name = type(self).__name__
        return ("w" if self.is_white else "b") + name[name == "Knight"].lower()


class Pawn(Piece):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        moves = set[Square]()
        if not board[next_rank := self.pos + (0, self.is_white or -1)]:
            moves.add(next_rank)
            # Check two square starting move
            if self.pos.rank == 1 and self.is_white or self.pos.rank == 6 and not self.is_white:
                if not board[next_next_rank := next_rank + (0, self.is_white or -1)]:
                    moves.add(next_next_rank)
        # Check captures
        for dx in -1, 1:
            if board[diag := next_rank + (dx, 0)]:
                moves.add(diag)
        return moves


class Rook(Piece, SlidingPieceMixin):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        return self.get_directional_moves(board, self.pos, ((1, 0), (0, 1), (0, -1), (-1, 0)))


class Knight(Piece):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        deltas = (-2, -1), (-2, +1), (+2, -1), (+2, +1), (-1, -2), (-1, +2), (+1, -2), (+1, +2)
        return {self.pos + d for d in deltas}


class Bishop(Piece, SlidingPieceMixin):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        return self.get_directional_moves(board, self.pos, ((1, 1), (1, -1), (-1, 1), (-1, -1)))


class Queen(Rook, Bishop):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        return Rook._generate_moves(self, board) | Bishop._generate_moves(self, board)


class King(Piece):
    @override
    def _generate_moves(self, board: BoardStateGetter) -> set[Square]:
        return {self.pos + d for d in product((0, +1, -1), (0, +1, -1))}
