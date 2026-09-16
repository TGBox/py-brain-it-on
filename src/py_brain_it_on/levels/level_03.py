"""
Level 3 — Der Trichter

Ball fällt frei aus der Luft.
Eimer steht unten in der Mitte.
Ziel: Einen Trichter zeichnen, der den frei fallenden Ball zielsicher in den Eimer lenkt.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level03(BaseLevel):
    LEVEL_NUMBER = 3
    TITLE = "Der Trichter"
    GOAL_DESCRIPTION = "Fange den fallenden Ball mit einem Trichter auf!"
    HINT = "Zeichne zwei schräge Linien wie ein V über dem Eimer, um den fallenden Ball aufzufangen."
    BG_COLOR = (244, 246, 240)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Trichter-Form: Ein V-förmiger Trichter über dem Eimer fängt den fallenden Ball auf."
    SOLUTION_STROKES = [
        [(720, 280), (940, 750), (980, 750), (1180, 280)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Ball fällt frei von oben leicht versetzt
        world.add_ball((W // 2 - 180, 200), color=COLOR_CORAL)

        # Eimer unten in der Mitte
        world.add_bucket((W // 2, floor_y), width=130, height=120, color=COLOR_TEAL)

        # Boden links und rechts
        world.add_static_segment((0, floor_y), (W // 2 - 80, floor_y), color=(140, 120, 100), radius=6)
        world.add_static_segment((W // 2 + 80, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Leitrampen links und rechts oben
        world.add_static_segment((200, 480), (500, 660), color=COLOR_PURPLE, radius=6)
        world.add_static_segment((W - 200, 480), (W - 500, 660), color=COLOR_PURPLE, radius=6)
