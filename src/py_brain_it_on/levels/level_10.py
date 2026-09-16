"""
Level 10 — Zwei Bälle

Zwei Bälle an gegenüberliegenden Seiten.
Beide müssen in denselben zentralen Eimer gelangen.
Ziel: Eine Y-Form oder zwei koordinierte Rampen zeichnen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_BLUE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level10(BaseLevel):
    LEVEL_NUMBER = 10
    TITLE = "Zwei Bälle"
    GOAL_DESCRIPTION = "Bringe beide Bälle in den zentralen Eimer!"
    HINT = "Beide Bälle müssen in den Eimer. Zeichne zwei koordinierte Rampen oder eine große Y-Schale."
    BG_COLOR = (238, 244, 252)
    STAR_THRESHOLDS = (2, 4)
    SOLUTION_DESCRIPTION = "Duale Rampen: Zwei koordinierte Rutschen leiten beide Bälle zeitversetzt in den zentralen Eimer."
    SOLUTION_STROKES = [
        [(220, 260), (280, 370), (880, 800)],
        [(1700, 310), (1640, 370), (1200, 700), (1030, 800)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Ball 1 oben links
        world.add_static_segment((120, 380), (450, 380), color=(140, 120, 100), radius=6)
        world.add_ball((280, 330), color=COLOR_CORAL)

        # Ball 2 oben rechts
        world.add_static_segment((W - 450, 380), (W - 120, 380), color=(140, 120, 100), radius=6)
        world.add_ball((W - 280, 330), color=COLOR_BLUE)

        # Großer Eimer unten Mitte für beide Bälle
        world.add_bucket((W // 2, floor_y), width=180, height=120, color=COLOR_TEAL)

        # Boden
        world.add_static_segment((0, floor_y), (W // 2 - 110, floor_y), color=(140, 120, 100), radius=6)
        world.add_static_segment((W // 2 + 110, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)
