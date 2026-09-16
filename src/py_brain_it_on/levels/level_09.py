"""
Level 9 — Kettenreaktion

Ein schwerer Kasten liegt oben auf einem Mauervorsprung.
Der Ball ruht sicher in einer Mulde auf einer Plattform.
Ziel: Bringe den Kasten ins Rollen oder Fallen, um den Ball ins Ziel zu befördern.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level09(BaseLevel):
    LEVEL_NUMBER = 9
    TITLE = "Kettenreaktion"
    GOAL_DESCRIPTION = "Nutze das schwere Gewicht, um den Ball in den Eimer zu stoßen!"
    HINT = "Bringe den Kasten oben links mit einer gezeichneten Form zu Fall, damit er auf eine Rampe oder den Ball prallt."
    BG_COLOR = (245, 242, 236)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Mauervorsprung oben links mit schwerem Kasten
        world.add_static_segment((150, 320), (450, 320), color=(140, 120, 100), radius=6)
        world.add_dynamic_box((300, 260), width=100, height=100, mass=10.0, color=(170, 105, 60))

        # Plattform in der Mitte mit Ball
        world.add_static_segment((750, 620), (1150, 620), color=(140, 120, 100), radius=6)
        world.add_static_segment((750, 620), (750, 580), color=(140, 120, 100), radius=5)  # Stopper links
        world.add_ball((950, 570), color=COLOR_CORAL)

        # Eimer unten rechts
        world.add_bucket((1600, floor_y), width=160, height=120, color=COLOR_TEAL)
