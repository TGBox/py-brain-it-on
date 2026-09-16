"""
levels/base_level.py — Abstrakte Basisklasse für Brain it on! Level.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..physics.world import PhysicsWorld


class BaseLevel(ABC):
    """
    Jedes Level erbt von dieser Klasse.
    
    Verantwortlich für:
    - Initialisierung der Physik-Welt (Ball, Eimer, Plattformen)
    - Metadaten (Titel, Hinweis, Hintergrundfarbe)
    - Optionale Hintergrund-Zeichnung
    """

    # In Unterklassen überschreiben
    LEVEL_NUMBER: int = 0
    TITLE: str = "Level"
    HINT: str = "Zeichne eine Form, die den Ball in den Eimer leitet."
    BG_COLOR: tuple = (245, 240, 230)

    @abstractmethod
    def setup(self, world: "PhysicsWorld") -> None:
        """
        Initialisiert die Physik-Welt für dieses Level.
        Fügt Ball(e), Eimer und statische Plattformen hinzu.
        """
        ...

    def draw_background(self, surface, area) -> None:
        """
        Optionale Hintergrund-Zeichnung (Dekorationen, Labels).
        Wird VOR den Physik-Objekten gezeichnet.
        """
        pass
