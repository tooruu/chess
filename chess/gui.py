from collections.abc import Iterable, Sequence
from itertools import product

import pygame as pyg
import win32con
import win32gui
from logic import STARTING_FEN, Board
from pieces import Piece, Square

ICON = r"resources/icon.png"
WINDOW_CAPTION = "Chess"
CELL_SIZE = 80
PIECE_SET = "resources/pieces/Neo.png"

type ColorValue = pyg.Color | int | str | tuple[int, int, int] | tuple[int, int, int, int]


# https://stackoverflow.com/a/64550793
def wnd_proc(old_wnd_proc, draw_callback, wnd_handle, message, w_param, l_param):
    if message == win32con.WM_SIZE:
        # win32gui.RedrawWindow(wnd_handle, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE)
        draw_callback()
    return win32gui.CallWindowProc(old_wnd_proc, wnd_handle, message, w_param, l_param)


class ChessGUI:
    board: pyg.Surface
    _sprites: dict[str, pyg.Surface]

    def __init__(
        self,
        fen: str = STARTING_FEN,
        cell_size_px: float = CELL_SIZE,
        colors: tuple[ColorValue, ColorValue] = ("white", "black"),
        piece_set: str = PIECE_SET,
    ) -> None:
        self.state = Board(fen)
        self._wnd_size = cell_size_px * 8
        self.colors = colors
        self.piece_set = piece_set
        self.whites_turn = True
        self.selection: Piece | None = None
        self.available_moves = set[Square]()
        pyg.display.set_icon(pyg.image.load(ICON))
        pyg.display.set_caption(WINDOW_CAPTION)
        pyg.mouse.set_cursor(pyg.SYSTEM_CURSOR_HAND)
        pyg.init()

        self.load_pieces()
        self.board = pyg.display.set_mode((self._wnd_size,) * 2, pyg.RESIZABLE)
        self.draw_board()
        old_wnd_proc = win32gui.SetWindowLong(
            win32gui.GetForegroundWindow(),
            win32con.GWL_WNDPROC,
            lambda *args: wnd_proc(old_wnd_proc, self.correct_aspect_ratio, *args),
        )  # Call self.correct_aspect_ratio on each window resize event

    def __start__(self) -> None:
        self.start_game()

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        pyg.quit()

    def start_game(self) -> None:
        while event := pyg.event.wait():
            match event:
                case pyg.event.Event(type=pyg.QUIT):
                    return
                case pyg.event.Event(type=pyg.MOUSEBUTTONDOWN, button=1, pos=pos):
                    square = self.pos_to_square(pos)
                    piece = self.state[square]
                    if piece and piece.is_white is self.whites_turn:
                        pyg.mouse.set_visible(not self.toggle_moves_for(piece))
                        pyg.mouse.set_pos(self.square_to_rect(square).center)
                    elif self.selection:
                        pyg.mouse.set_visible(True)
                        self.make_move(self.selection, square)
                        self.toggle_moves_for(self.selection)
                case pyg.event.Event(type=pyg.MOUSEMOTION, pos=(x, y)) if self.selection:
                    self.draw_board()
                    offset = self._wnd_size / 16
                    pos = (x - offset, y - offset)
                    pyg.display.update(self.board.blit(self._sprites[self.selection.type], pos))

    def make_move(self, piece: Piece, dest: Square) -> bool:
        if dest not in self.available_moves:
            return False
        self.state.move_piece(piece, dest)
        self.switch_turn()
        return True

    def draw_board(self, rect: pyg.Rect | Sequence[pyg.Rect] | None = None) -> None:
        # Draw checkers
        self.board.fill(self.colors[1])
        area = self._wnd_size / 8
        i = 0
        for row in range(8):
            for col in range(8):
                if i % 2 == 0:
                    self.board.fill(self.colors[0], (area * col, area * row, area, area))
                i += 1
            i += 1

        # Place pieces
        # for piece in self.state:
        #     sprite = self._sprites[piece.type]
        #     sprite = pyg.transform.smoothscale(sprite, (self._wnd_size / 8,) * 2)
        #     self.board.blit(sprite, self.square_to_rect(piece.pos))
        self.board.blits(
            [
                (self._sprites[piece.type], self.square_to_rect(piece.pos))
                for piece in self.state
                if piece is not self.selection
            ]
        )

        if self.available_moves:
            self.highlight_squares(self.available_moves)

        if rect:
            pyg.display.update(rect)
        else:
            pyg.display.update()

    def switch_turn(self) -> None:
        self.whites_turn = not self.whites_turn

    def square_color(self, square: Square) -> pyg.Color:
        return pyg.Color(self.colors[sum(square) % 2 == 0])

    def toggle_moves_for(self, piece: Piece) -> bool:
        if piece is self.selection:
            self.selection = None
            self.available_moves.clear()
            self.draw_board()
            return False

        if self.selection:  # Erase moves for the previously selected piece
            self.draw_board([self.square_to_rect(s) for s in self.available_moves])
        self.selection = piece
        self.available_moves = piece.get_moves(self.state)
        # self.add_outline_to_image(self._sprites[piece.type], 2, (255, 0, 0))
        self.highlight_squares(self.available_moves)
        return True

    def add_outline_to_image(self, image: pyg.Surface, thickness: int, color: tuple):
        ...
        # mask = pyg.mask.from_surface(image).scale((image.get_width() + 2, image.get_height() + 2))
        # mask.fill()
        # new_img = pyg.Surface((image.get_width() + 2, image.get_height() + 2))
        # new_img.fill()

        # for i in -thickness, thickness:
        #     new_img.blit(mask, (i + thickness, thickness))
        #     new_img.blit(mask, (thickness, i + thickness))
        # new_img.blit(image, (thickness, thickness))
        # mask.to_surface(self.board, unsetcolor=None, setcolor="red")
        # pyg.display.flip()

        # return new_img

    def highlight_squares(self, squares: Iterable[Square]) -> None:
        radius = self._wnd_size / 32
        surface = pyg.Surface((self._wnd_size,) * 2, pyg.SRCALPHA)
        # rects = [
        #     pyg.draw.circle(
        #         surface,
        #         (~self.square_color(square)).lerp(pyg.Color(*() * 3), 0.5),
        #         self.square_to_rect(square).center,
        #         radius,
        #     )
        #     for square in squares
        #     if square.valid
        # ]
        rects = list[pyg.Rect]()
        for square in squares:
            square_color = ~self.square_color(square)
            # r, g, b, _ = square_color
            # luma = 0.2126 * r + 0.7152 * g + 0.0722 * b  # ITU-R BT.709
            square_color += pyg.Color(0, 0, 0, 40)
            pos = self.square_to_rect(square).center
            rects.append(pyg.draw.circle(surface, square_color, pos, radius))
        self.board.blit(surface, (0, 0))
        pyg.display.update(rects)

    def pos_to_square(self, pos: tuple[int, int]) -> Square:
        cell_size = self._wnd_size / 8
        x, y = pos
        return Square(int(x // cell_size), int(7 - y // cell_size))

    def square_to_rect(self, square: Square) -> pyg.Rect:
        cell_size = self._wnd_size / 8
        return pyg.Rect(
            cell_size * square.file,
            self._wnd_size - (cell_size * (square.rank + 1)),
            cell_size,
            cell_size,
        )

    def load_pieces(self) -> None:
        set_path, _, file_ext = self.piece_set.rpartition(".")
        self._sprites = dict[str, pyg.Surface]()
        for piece in map("".join, product("wb", "pnbrqk")):
            sprite = pyg.image.load(f"{set_path}/{piece}.{file_ext}")
            self._sprites[piece] = pyg.transform.smoothscale(sprite, (self._wnd_size / 8,) * 2)

    def correct_aspect_ratio(self) -> None:
        w, h = pyg.display.get_window_size()
        if w == self._wnd_size:
            size = h
        elif h == self._wnd_size:
            size = w
        else:
            size = (w + h) // 2
        self._wnd_size = max(size, 256)
        self.load_pieces()
        self.board = pyg.display.set_mode((self._wnd_size,) * 2, pyg.RESIZABLE)
        self.draw_board()
