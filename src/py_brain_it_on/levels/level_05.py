"""
Level 5 — Zickzack-Kaskade

Ball liegt ganz oben in der Mitte.
Mehrere versetzte Plattformen zwingen zu einem Zickzack-Weg.
Eimer steht unten rechts auf dem Boden.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import (
    COLOR_CORAL, COLOR_TEAL, COLOR_GREEN, COLOR_PURPLE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)


class Level05(BaseLevel):
    LEVEL_NUMBER = 5
    TITLE = "Zickzack-Kaskade"
    GOAL_DESCRIPTION = "Leite den Ball über die Stufen in den Eimer!"
    HINT = "Zeichne schräge Führungen, damit der Ball im Zickzack von Ebene zu Ebene rollt."
    BG_COLOR = (240, 248, 242)
    STAR_THRESHOLDS = (2, 3)
    SOLUTION_DESCRIPTION = "Kaskaden-Führung: Eine Rutsche leitet den Ball auf die mittlere Ebene, ein Abweiser lenkt ihn in den Eimer."
    SOLUTION_STROKES = [
        [(900, 180), (950, 240), (1050, 620)],
        [(1630, 580), (1630, 700), (1580, 820)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Start-Podest ganz oben Mitte
        world.add_static_segment((W // 2 - 140, 240), (W // 2 + 140, 240), color=(140, 120, 100), radius=6)
        world.add_ball((W // 2, 190), color=COLOR_CORAL)

        # Versetzte Plattformen
        world.add_static_segment((320, 480), (820, 480), color=COLOR_GREEN, radius=6)
        world.add_static_segment((1100, 650), (1600, 650), color=COLOR_PURPLE, radius=6)
        world.add_static_segment((400, 810), (900, 810), color=COLOR_GREEN, radius=6)

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Eimer unten rechts
        world.add_bucket((1600, floor_y), width=150, height=120, color=COLOR_TEAL)
