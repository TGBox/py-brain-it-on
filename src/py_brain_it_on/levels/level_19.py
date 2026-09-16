"""
Level 19 — Zwillings-Eimer

Zwei Bälle oben in der Mitte.
Zwei separate Eimer ganz links und ganz rechts am Boden.
Ziel: Teile die Bälle auf, sodass jeder Eimer einen Ball erhält!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_BLUE, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level19(BaseLevel):
    LEVEL_NUMBER = 19
    TITLE = "Zwillings-Eimer"
    GOAL_DESCRIPTION = "Befördere die Bälle in die beiden getrennten Eimer!"
    HINT = "Zeichne ein umgekehrtes V (Keil) zwischen die Bälle, damit einer nach links und einer nach rechts rollt."
    BG_COLOR = (242, 245, 252)
    STAR_THRESHOLDS = (2, 4)
    SOLUTION_DESCRIPTION = "Gabelungs-Rampen: Zwei getrennte Rutschen teilen die beiden Bälle nach links und rechts auf."
    SOLUTION_STROKES = [
        [(950, 150), (880, 250), (340, 850)],
        [(970, 150), (1040, 250), (1580, 850)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Start-Podest oben Mitte
        world.add_static_segment((800, 260), (1120, 260), color=(140, 120, 100), radius=6)
        world.add_ball((880, 210), color=COLOR_CORAL)
        world.add_ball((1040, 210), color=COLOR_BLUE)

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Linker Eimer
        world.add_bucket((320, floor_y), width=150, height=120, color=COLOR_TEAL)

        # Rechter Eimer
        world.add_bucket((1600, floor_y), width=150, height=120, color=COLOR_TEAL)
