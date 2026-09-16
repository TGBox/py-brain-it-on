"""
Level 24 — Katapult-Meister

Eine gigantische, 600 Pixel hohe Mauer teilt das Spielfeld.
Eine vorinstallierte Wippe steht bereit.
Ziel: Katapultiere den Ball mit maximaler Wucht über die Riesenmauer!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, COLOR_GREEN, WINDOW_WIDTH, WINDOW_HEIGHT


class Level24(BaseLevel):
    LEVEL_NUMBER = 24
    TITLE = "Katapult-Meister"
    GOAL_DESCRIPTION = "Schleudere den Ball über die Riesenmauer in den Eimer!"
    HINT = "Lass ein sehr großes, schweres Gewicht aus großer Höhe auf die linke Seite der Wippe knallen."
    BG_COLOR = (246, 242, 238)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Riesenmauer in der Mitte (x = 960)
        world.add_static_segment((960, floor_y), (960, 380), color=COLOR_ORANGE, radius=12)

        # Drehpunkt links für die Wippe
        world.add_static_segment((500, floor_y), (480, floor_y - 90), color=COLOR_GREEN, radius=8)
        world.add_static_segment((500, floor_y), (520, floor_y - 90), color=COLOR_GREEN, radius=8)
        world.add_static_segment((460, floor_y - 90), (540, floor_y - 90), color=COLOR_GREEN, radius=6)

        # Dynamischer Wippbalken
        world.add_dynamic_box((500, floor_y - 105), width=540, height=24, mass=4.0, color=(160, 110, 70))

        # Ball auf dem rechten Ende der Wippe
        world.add_ball((720, floor_y - 140), color=COLOR_CORAL)

        # Eimer rechts
        world.add_bucket((1550, floor_y), width=160, height=120, color=COLOR_TEAL)
