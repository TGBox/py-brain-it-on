"""
Level 7 — Die Schlucht

Ein tiefer Abgrund trennt den linken Bereich vom Zielbereich rechts.
Der Ball muss die Schlucht überqueren und in den Eimer gelangen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level07(BaseLevel):
    LEVEL_NUMBER = 7
    TITLE = "Die Schlucht"
    GOAL_DESCRIPTION = "Überquere die Schlucht und erreiche den Eimer!"
    HINT = "Baue eine tragfähige Brücke über den Abgrund oder katapultiere den Ball hinüber."
    BG_COLOR = (244, 240, 234)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Schlucht-Brücke: Eine lange Brücke von der Klippe über den Abgrund direkt in den Eimer."
    SOLUTION_STROKES = [
        [(240, 390), (290, 455), (600, 490), (1350, 580), (1550, 595)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        left_cliff_y = 460
        right_cliff_y = 720

        # Linke Klippe (erhöht)
        world.add_static_segment((0, left_cliff_y), (550, left_cliff_y), color=(130, 115, 95), radius=8)
        world.add_static_segment((550, left_cliff_y), (550, H), color=(130, 115, 95), radius=8)

        # Ball auf linker Klippe
        world.add_ball((300, left_cliff_y - 45), color=COLOR_CORAL)

        # Rechte Klippe
        world.add_static_segment((1350, right_cliff_y), (W, right_cliff_y), color=(130, 115, 95), radius=8)
        world.add_static_segment((1350, right_cliff_y), (1350, H), color=(130, 115, 95), radius=8)

        # Eimer auf rechter Klippe
        world.add_bucket((1600, right_cliff_y), width=150, height=120, color=COLOR_TEAL)
