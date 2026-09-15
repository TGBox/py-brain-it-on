"""
py_brain_it_out — Python-Adaption von Brain it out!

Einstiegspunkt: main()
"""
from __future__ import annotations


def main() -> None:
    """Startet das Spiel."""
    from .game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
