"""
Level 13 — Präzisionsschuss

In der Mitte steht eine massive Wand mit einem schmalen Durchlass.
Der Ball muss exakt durch diese Öffnung geschossen werden, um den Eimer zu treffen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level13(BaseLevel):
    LEVEL_NUMBER = 13
    TITLE = "Präzisionsschuss"
    GOAL_DESCRIPTION = "Befördere den Ball durch das Fenster in den Eimer!"
    HINT = "Gib dem Ball auf der Rampe genug Schwung oder zeichne eine Schanze, die genau auf die Öffnung zielt."
    BG_COLOR = (244, 240, 248)
    STAR_THRESHOLDS = (1, 2)
    SOLUTION_DESCRIPTION = "Präzisions-Schanze: Eine Rampe zielt genau durch das Wandfenster direkt in den Eimer."
    SOLUTION_STROKES = [
        [(520, 480), (1050, 620), (1530, 850)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Anlauf-Rampe links
        world.add_static_segment((150, 320), (550, 480), color=(140, 120, 100), radius=6)
        world.add_ball((250, 320), color=COLOR_CORAL)

        # Barriere-Wand mit Tor in der Mitte (x=1050)
        world.add_static_segment((1050, 100), (1050, 520), color=COLOR_PURPLE, radius=10)
        world.add_static_segment((1050, 720), (1050, floor_y), color=COLOR_PURPLE, radius=10)

        # Eimer rechts
        world.add_bucket((1600, floor_y), width=160, height=120, color=COLOR_TEAL)
