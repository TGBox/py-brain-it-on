"""
base_puzzle.py — Abstrakte Basisklasse für alle Puzzles.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import pygame

if TYPE_CHECKING:
    from ..game import Game


class BasePuzzle(ABC):
    """
    Jedes Puzzle erbt von dieser Klasse.
    
    Ein Puzzle ist zuständig für:
    - Zeichnen des Puzzle-Inhalts (Spielbereich)
    - Verarbeiten von Events
    - Melden, ob es gelöst wurde (via on_solved Callback)
    """

    # Metadaten — in Unterklassen überschreiben
    LEVEL_NUMBER: int = 0
    TITLE: str = "Unbekanntes Rätsel"
    QUESTION: str = "Was ist die Frage?"
    HINT: str = "Das ist ein Hinweis."

    def __init__(self, game: "Game", on_solved: callable, on_wrong: callable) -> None:
        self.game = game
        self.on_solved = on_solved   # Callback: wird bei richtiger Lösung aufgerufen
        self.on_wrong = on_wrong     # Callback: wird bei falscher Aktion aufgerufen
        self._solved = False

    @property
    def solved(self) -> bool:
        return self._solved

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Verarbeitet Pygame-Events."""
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        """Aktualisiert den Puzzle-Zustand."""
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        """
        Zeichnet das Puzzle.
        area: Der verfügbare Rechteckbereich auf dem Screen (ohne Header/Footer).
        """
        ...

    def reset(self) -> None:
        """Setzt das Puzzle in den Ausgangszustand zurück."""
        self._solved = False

    def _solve(self) -> None:
        """Intern aufrufen, wenn das Puzzle gelöst wurde."""
        if not self._solved:
            self._solved = True
            self.on_solved()

    def _wrong(self) -> None:
        """Intern aufrufen, wenn eine falsche Aktion ausgeführt wurde."""
        self.on_wrong()
