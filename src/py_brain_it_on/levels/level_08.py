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
    SOLUTION_DESCRIPTION = "Schwung-Umlenkung: Eine Auffang-Kurve am Ende der Schräge fängt den Ball auf und leitet ihn über den Boden in den Eimer."
    SOLUTION_STROKES = [
        [(160, 500), (170, 720), (260, 780), (550, 810), (1000, 830), (1450, 850), (1510, 860)]
    ]


    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Schräge Ebene nach links unten geneigt
        world.add_static_segment((1100, 420), (320, 650), color=COLOR_ORANGE, radius=7)
        world.add_ball((950, 440), color=COLOR_CORAL)

        # Boden unten
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Eimer rechts auf dem Boden
        world.add_bucket((1530, floor_y), width=150, height=120, color=COLOR_TEAL)
