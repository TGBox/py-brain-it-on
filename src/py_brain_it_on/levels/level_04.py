"""
Level 4 — Kollision

Zwei Bälle an den gegenüberliegenden Seiten des Spielfelds.
Ziel: Bringe die beiden Bälle dazu, direkt miteinander zu kollidieren!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_BLUE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level04(BaseLevel):
    LEVEL_NUMBER = 4
    TITLE = "Kollision"
    GOAL_DESCRIPTION = "Bringe die beiden Bälle zum Zusammenstoß!"
    HINT = "Zeichne Rampen, die beide Bälle zur gleichen Zeit in die Mitte aufeinander zu rasen lassen."
    BG_COLOR = (240, 244, 252)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Eine geschwungene Brücke verbindet beide Rampenenden und führt die Bälle zum frontalen Zusammenstoß."
    SOLUTION_STROKES = [
        [(530, 580), (960, 620), (1390, 580)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Rampe links
        world.add_static_segment((120, 350), (550, 580), color=(140, 120, 100), radius=6)
        world.add_ball((250, 360), color=COLOR_CORAL)

        # Rampe rechts
        world.add_static_segment((W - 120, 350), (W - 550, 580), color=(140, 120, 100), radius=6)
        world.add_ball((W - 250, 360), color=COLOR_BLUE)

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        return world.balls_collided
