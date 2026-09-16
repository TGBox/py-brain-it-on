"""
Level 8 — Gegen den Wind

Der Ball rollt auf einer Schräge nach links weg.
Der Eimer befindet sich jedoch oben rechts!
Ziel: Den Schwung des Balls umlenken oder ihn nach rechts oben katapultieren.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level08(BaseLevel):
    LEVEL_NUMBER = 8
    TITLE = "Gegen den Wind"
    GOAL_DESCRIPTION = "Lenke den nach links rollenden Ball nach rechts oben in den Eimer!"
    HINT = "Fange den Ball am Ende der Schräge mit einer steilen Kurve auf, die ihn nach rechts schleudert."
    BG_COLOR = (248, 245, 238)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Schräge Ebene nach links unten geneigt
        world.add_static_segment((1100, 420), (320, 650), color=COLOR_ORANGE, radius=7)
        world.add_ball((950, 440), color=COLOR_CORAL)

        # Boden unten
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Eimer-Plattform oben rechts
        world.add_static_segment((1320, 440), (1750, 440), color=(140, 120, 100), radius=6)
        world.add_bucket((1530, 440), width=150, height=120, color=COLOR_TEAL)
