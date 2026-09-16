"""
Level 23 — Ball-Duell

Zwei Bälle müssen in der Luft oder auf einer Rampe zusammenstoßen,
und mindestens einer von ihnen muss anschließend im Eimer landen!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_BLUE, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level23(BaseLevel):
    LEVEL_NUMBER = 23
    TITLE = "Ball-Duell"
    GOAL_DESCRIPTION = "Lass die Bälle kollidieren und einen in den Eimer rollen!"
    HINT = "Bringe beide Bälle über dem Eimer zum Zusammenprall, damit der Abpraller direkt in den Eimer fällt."
    BG_COLOR = (242, 246, 252)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Start-Podest links
        world.add_static_segment((150, 320), (450, 320), color=(140, 120, 100), radius=6)
        world.add_ball((300, 270), color=COLOR_CORAL)

        # Start-Podest rechts
        world.add_static_segment((W - 450, 320), (W - 150, 320), color=(140, 120, 100), radius=6)
        world.add_ball((W - 300, 270), color=COLOR_BLUE)

        # Eimer unten Mitte
        world.add_bucket((W // 2, floor_y), width=180, height=120, color=COLOR_TEAL)

        # Boden links und rechts
        world.add_static_segment((0, floor_y), (W // 2 - 110, floor_y), color=(140, 120, 100), radius=6)
        world.add_static_segment((W // 2 + 110, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if not world.balls_collided:
            return False
        return any(b.in_bucket for b in world.balls)
