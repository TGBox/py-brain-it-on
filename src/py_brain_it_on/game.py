"""
game.py — Haupt-Game-Loop und Szenenmanager für py-brain-it-on.
"""
from __future__ import annotations

import sys
import pygame

from .settings import (
    FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH,
)
from . import save_manager
from .scenes.base_scene import BaseScene


class Game:
    """
    Haupt-Spiel-Klasse.
    
    Verwaltet das Pygame-Fenster, den Game-Loop und den Szenenstack.
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Szenenstapel (LIFO)
        self.scene_stack: list[BaseScene] = []

        # Spielfortschritt
        self.save_data = save_manager.load()

    def push_scene(self, scene: BaseScene) -> None:
        """Legt eine neue Szene auf den Stapel."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
        self.scene_stack.append(scene)
        scene.on_enter()

    def pop_scene(self) -> None:
        """Entfernt die oberste Szene vom Stapel."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
            self.scene_stack.pop()
        if self.scene_stack:
            self.scene_stack[-1].on_enter()

    @property
    def current_scene(self) -> BaseScene | None:
        return self.scene_stack[-1] if self.scene_stack else None

    def run(self) -> None:
        """Startet den Haupt-Game-Loop."""
        # Anfangs-Szene: Hauptmenü
        from .scenes.menu_scene import MenuScene
        self.push_scene(MenuScene(self))

        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta-Zeit in Sekunden
            dt = min(dt, 0.05)  # Maximal 50ms, um Sprünge bei Lag zu verhindern

            # Events verarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if len(self.scene_stack) > 1:
                        self.pop_scene()
                    else:
                        running = False
                    break
                if self.current_scene:
                    self.current_scene.handle_event(event)

            # Update
            if self.current_scene:
                self.current_scene.update(dt)

            # Zeichnen
            self.screen.fill((255, 248, 240))
            if self.current_scene:
                self.current_scene.draw(self.screen)
            pygame.display.flip()

            # Beenden wenn kein Szenenstack mehr
            if not self.scene_stack:
                running = False

        pygame.quit()
        sys.exit(0)
