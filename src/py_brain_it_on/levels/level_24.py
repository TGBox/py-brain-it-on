"""
Level 24 — Der Ausbruch

Der Ball ist in einer tiefen U-förmigen Schale gefangen.
Der Eimer steht weit entfernt rechts auf dem Boden.
Ziel: Befreie den Ball aus der Schale und befördere ihn in den Eimer.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level24(BaseLevel):
    LEVEL_NUMBER = 24
    TITLE = "Der Ausbruch"
    GOAL_DESCRIPTION = "Befreie den Ball aus der Schale in den Eimer!"
    HINT = "Zeichne einen Hebel mit einem Haken oder einen schweren Schläger, der in die Schale greift und den Ball herausholt."
    BG_COLOR = (248, 242, 246)
    STAR_THRESHOLDS = (2, 4)
    SOLUTION_DESCRIPTION = "Hebel-Kran: Ein Hakenarm greift in die Schale, ein fallendes Gewicht zieht den Ball heraus und schleudert ihn in den Eimer."
    SOLUTION_STROKES = [
        [(930, 640), (980, 640), (1110, 530), (1420, 560)],
        [(1350, 120), (1400, 120), (1400, 200), (1350, 200), (1350, 120)]
    ]


    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # U-förmige Gefängnisschale
        world.add_static_segment((800, 680), (1120, 680), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((800, 680), (800, 560), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((1120, 680), (1120, 560), color=COLOR_PURPLE, radius=8)

        # Ball in der Schale
        world.add_ball((960, 630), color=COLOR_CORAL)

        # Eimer rechts
        world.add_bucket((1650, floor_y), width=160, height=120, color=COLOR_TEAL)
