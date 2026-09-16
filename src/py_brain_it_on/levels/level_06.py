"""
Level 6 — Bogenbrücke

Ball liegt links. Eine hohe Wand steht in der Mitte.
Eimer steht rechts auf dem Boden.
Ziel: Den Ball über die Wand hebeln, rollen oder katapultieren.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level06(BaseLevel):
    LEVEL_NUMBER = 6
    TITLE = "Bogenbrücke"
    GOAL_DESCRIPTION = "Befördere den Ball über die Wand in den Eimer!"
    HINT = "Nutze einen Hebel oder ein fallendes Gewicht, um den Ball über die Wand zu katapultieren."
    BG_COLOR = (245, 240, 232)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Bogenbrücke: Ein einzelner geschwungener Bogen von der Plattform über die Mauer in den Eimer."
    SOLUTION_STROKES = [
        [(240, 380), (280, 470), (600, 500), (960, 525), (1300, 680), (1530, 850)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Ball-Plattform links
        world.add_static_segment((120, 480), (450, 480), color=(140, 120, 100), radius=6)
        world.add_ball((280, 430), color=COLOR_CORAL)

        # Hindernis-Wand in der Mitte
        world.add_static_segment((960, floor_y), (960, 540), color=COLOR_ORANGE, radius=10)

        # Eimer rechts
        world.add_bucket((1550, floor_y), width=160, height=120, color=COLOR_TEAL)
