from gui import ChessGUI


class Game:
    def __init__(self) -> None:
        self.gui = ChessGUI(colors=("#C4AD7C", "#674B2F"))
        self.gui.whites_turn = True

    def __enter__(self) -> None:
        self.play()

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self.cleanup()

    def play(self) -> None:
        self.gui.start_game()

    def cleanup(self) -> None:
        self.gui.cleanup()
