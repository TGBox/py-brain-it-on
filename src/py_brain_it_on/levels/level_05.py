"""
Level 5 — Schaukel

Ball liegt hoch oben in der Mitte.
Eimer steht auf einer Seite ganz unten.
Zwischen Ball und Eimer liegt ein breiter leerer Raum —
Spieler muss mehrere Stufen zeichnen oder eine Kurve.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import (
    COLOR_CORAL, COLOR_TEAL, COLOR_GREEN, COLOR_YELLOW,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)


class Level05(BaseLevel):
    LEVEL_NUMBER = 5
    TITLE = "Stufenweg"
    HINT = "Zeichne mehrere Stufen oder eine geschwungene Linie als Rutsche."
    BG_COLOR = (240, 248, 242)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Ball liegt ganz oben Mitte
        world.add_static_segment((W // 2 - 50, 100), (W // 2 + 50, 100), color=(140, 120, 100), radius=5)
        world.add_ball((W // 2, 65), color=COLOR_CORAL)

        # Eimer unten rechts
        world.add_bucket((W - 100, H - 80), width=80, height=65, color=COLOR_TEAL)

        # Boden
        world.add_static_segment((0, H - 80), (W - 160, H - 80), color=(140, 120, 100), radius=5)
        world.add_static_segment((W - 40, H - 80), (W, H - 80), color=(140, 120, 100), radius=5)

        # Einige Hindernisse für mehr Spannung
        world.add_static_segment((180, 280), (280, 280), color=COLOR_GREEN, radius=5)
        world.add_static_segment((450, 380), (580, 380), color=COLOR_YELLOW, radius=5)
