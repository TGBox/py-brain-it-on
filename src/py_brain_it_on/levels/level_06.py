"""
Level 6 — Die Schlucht

Ein tiefer Abgrund trennt den linken Bereich vom Zielbereich rechts.
Der Ball muss die Schlucht überqueren und in den Eimer gelangen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level06(BaseLevel):
    LEVEL_NUMBER = 6
    TITLE = "Die Schlucht"
    GOAL_DESCRIPTION = "Überquere die Schlucht und erreiche den Eimer!"
    HINT = "Baue eine tragfähige Brücke über den Abgrund oder katapultiere den Ball hinüber."
    BG_COLOR = (244, 240, 234)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        cliff_y = 720

        # Linke Klippe
        world.add_static_segment((0, cliff_y), (650, cliff_y), color=(130, 115, 95), radius=8)
        world.add_static_segment((650, cliff_y), (650, H), color=(130, 115, 95), radius=8)

        # Ball auf linker Klippe
        world.add_ball((300, cliff_y - 45), color=COLOR_CORAL)

        # Rechte Klippe
        world.add_static_segment((1250, cliff_y), (W, cliff_y), color=(130, 115, 95), radius=8)
        world.add_static_segment((1250, cliff_y), (1250, H), color=(130, 115, 95), radius=8)

        # Eimer auf rechter Klippe
        world.add_bucket((1600, cliff_y), width=150, height=120, color=COLOR_TEAL)
