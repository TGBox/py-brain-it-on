"""
Level 10 — Dreierlei

Drei Bälle auf drei verschiedenen Plattformen.
Alle drei Bälle müssen in den zentralen Eimer befördert werden.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import (
    COLOR_CORAL, COLOR_BLUE, COLOR_YELLOW, COLOR_TEAL,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)


class Level10(BaseLevel):
    LEVEL_NUMBER = 10
    TITLE = "Dreierlei"
    GOAL_DESCRIPTION = "Bringe alle drei Bälle in den großen Eimer!"
    HINT = "Zeichne eine breite Trichterschale, die von außen alle drei Bälle zur Mitte leitet."
    BG_COLOR = (244, 246, 252)
    STAR_THRESHOLDS = (2, 3)
    SOLUTION_DESCRIPTION = "Dreifach-Trichter: Zwei Außen-Rampen und ein zentraler Keil führen alle drei Bälle zusammen in den Eimer."
    SOLUTION_STROKES = [
        [(240, 220), (300, 310), (900, 780)],
        [(1680, 220), (1620, 310), (1020, 780)],
        [(940, 150), (960, 230), (980, 150)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Plattform 1 (links)
        world.add_static_segment((150, 320), (450, 320), color=(140, 120, 100), radius=6)
        world.add_ball((300, 270), color=COLOR_CORAL)

        # Plattform 2 (Mitte hoch)
        world.add_static_segment((810, 260), (1110, 260), color=(140, 120, 100), radius=6)
        world.add_ball((960, 210), color=COLOR_BLUE)

        # Plattform 3 (rechts)
        world.add_static_segment((1470, 320), (1770, 320), color=(140, 120, 100), radius=6)
        world.add_ball((1620, 270), color=COLOR_YELLOW)

        # Großer Sammel-Eimer unten in der Mitte
        world.add_bucket((W // 2, floor_y), width=240, height=130, color=COLOR_TEAL)

        # Boden links und rechts
        world.add_static_segment((0, floor_y), (W // 2 - 140, floor_y), color=(140, 120, 100), radius=6)
        world.add_static_segment((W // 2 + 140, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)
