"""
Level 2 — Bogenbrücke

Ball liegt links. Eine hohe Wand steht in der Mitte.
Eimer steht rechts auf dem Boden.
Ziel: Den Ball über die Wand hebeln, rollen oder katapultieren.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level02(BaseLevel):
    LEVEL_NUMBER = 2
    TITLE = "Bogenbrücke"
    GOAL_DESCRIPTION = "Befördere den Ball über die Wand in den Eimer!"
    HINT = "Nutze einen Hebel oder ein fallendes Gewicht, um den Ball über die Wand zu katapultieren."
    BG_COLOR = (245, 240, 232)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Ball-Plattform links
        world.add_static_segment((120, 600), (450, 600), color=(140, 120, 100), radius=6)
        world.add_ball((280, 550), color=COLOR_CORAL)

        # Hindernis-Wand in der Mitte (nicht bis ganz oben, damit man gut darüber hebeln kann)
        world.add_static_segment((960, floor_y), (960, 480), color=COLOR_ORANGE, radius=10)
        # Abgeschrägter Kopf
        world.add_static_segment((960, 480), (920, 450), color=COLOR_ORANGE, radius=8)

        # Eimer rechts
        world.add_bucket((1550, floor_y), width=160, height=120, color=COLOR_TEAL)
