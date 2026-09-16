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
    - Initialisierung der Physik-Welt (Ball, Eimer, Plattformen, dynamische Sonderobjekte)
    - Metadaten (Titel, Zielbeschreibung, Hinweis, Hintergrundfarbe, Sterne-Grenzwerte)
    - Siegbedingungs-Prüfung (z. B. Ball im Eimer, Objekt umwerfen, Objekt anheben)
    - Optionale Hintergrund-Zeichnung
    """

    LEVEL_NUMBER: int = 0
    TITLE: str = "Level"
    GOAL_DESCRIPTION: str = "Bringe den Ball in den Eimer!"
    HINT: str = "Zeichne eine Form, um die Aufgabe zu lösen."
    BG_COLOR: tuple = (245, 240, 230)
    STAR_THRESHOLDS: tuple[int, int] = (1, 3)
    SOLUTION_DESCRIPTION: str = "Physikalische Musterlösung"
    SOLUTION_STROKES: list[list[tuple[float, float]]] = []

    def get_solution_strokes(self) -> list[list[tuple[float, float]]]:
        """Gibt die vordefinierten Striche der Musterlösung zurück."""
        return [list(s) for s in self.SOLUTION_STROKES]

    @abstractmethod
    def setup(self, world: "PhysicsWorld") -> None:
        """Initialisiert die Physik-Welt für dieses Level."""
        ...

    def check_victory(self, world: "PhysicsWorld", dt: float = 0.0) -> bool:
        """
        Prüft, ob die Zielbedingung für dieses Level erfüllt ist.
        Standardmäßig: Alle Bälle sind im Eimer zur Ruhe gekommen.
        Kann in speziellen Levels überschrieben werden (z. B. Umwerfen, Anheben, Kollision).
        """
        return world.all_balls_in_bucket

    def draw_background(self, surface, area) -> None:
        """
        Optionale Hintergrund-Zeichnung (Dekorationen, Markierungen).
        Wird vor den Physik-Objekten gezeichnet.
        """
        pass
