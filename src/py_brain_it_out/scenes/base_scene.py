"""
base_scene.py — Abstrakte Basisklasse für alle Szenen.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ..game import Game


class BaseScene(ABC):
    """Jede Szene erbt von dieser Klasse."""

    def __init__(self, game: "Game") -> None:
        self.game = game

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Verarbeitet ein einzelnes Pygame-Event."""
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        """Aktualisiert den Zustand der Szene (dt = Delta-Zeit in Sekunden)."""
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet die Szene auf die gegebene Surface."""
        ...

    def on_enter(self) -> None:
        """Wird aufgerufen, wenn die Szene aktiv wird."""
        pass

    def on_exit(self) -> None:
        """Wird aufgerufen, wenn die Szene verlassen wird."""
        pass
