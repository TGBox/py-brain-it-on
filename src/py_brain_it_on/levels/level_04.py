"""
Level 4 — Zwei Baelle

Zwei Baelle an verschiedenen Positionen.
Beide muessen in denselben Eimer.
Ziel: Eine Y-Form oder zwei Rampen zeichnen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_BLUE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level04(BaseLevel):
    LEVEL_NUMBER = 4
    TITLE = "Zwei Baelle"
    HINT = "Beide Baelle muessen in den Eimer. Zeichne zwei Rampen oder eine Y-Form."
    BG_COLOR = (238, 244, 252)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Ball 1 oben links
        world.add_static_segment((40, 200), (180, 200), color=(140, 120, 100), radius=5)
        world.add_ball((110, 165), color=COLOR_CORAL)

        # Ball 2 oben rechts
        world.add_static_segment((W - 180, 200), (W - 40, 200), color=(140, 120, 100), radius=5)
        world.add_ball((W - 110, 165), color=COLOR_BLUE)

        # Eimer unten Mitte
        world.add_bucket((W // 2, H - 80), width=90, height=70, color=COLOR_TEAL)

        # Boden
        world.add_static_segment((0, H - 80), (W // 2 - 80, H - 80), color=(140, 120, 100), radius=5)
        world.add_static_segment((W // 2 + 80, H - 80), (W, H - 80), color=(140, 120, 100), radius=5)
