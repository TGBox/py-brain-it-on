"""
Level 17 — Der Ausbruch

Der Ball ist in einer tiefen U-förmigen Schale gefangen.
Der Eimer steht weit entfernt rechts auf dem Boden.
Ziel: Befreie den Ball aus der Schale und befördere ihn in den Eimer.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level17(BaseLevel):
    LEVEL_NUMBER = 17
    TITLE = "Der Ausbruch"
    GOAL_DESCRIPTION = "Befreie den Ball aus der Schale in den Eimer!"
    HINT = "Zeichne einen Hebel mit einem Haken oder einen schweren Schläger, der in die Schale greift und den Ball herausholt."
    BG_COLOR = (248, 242, 246)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # U-förmige Gefängnisschale
        world.add_static_segment((780, 680), (1140, 680), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((780, 680), (780, 420), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((1140, 680), (1140, 420), color=COLOR_PURPLE, radius=8)

        # Ball in der Schale
        world.add_ball((960, 630), color=COLOR_CORAL)

        # Eimer rechts
        world.add_bucket((1650, floor_y), width=160, height=120, color=COLOR_TEAL)
