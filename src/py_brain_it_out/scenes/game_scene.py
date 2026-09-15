"""
game_scene.py — Universelle Puzzle-Spielszene mit Header (Frage, Hinweis, Sterne).
"""
from __future__ import annotations

import importlib
import pygame

from .base_scene import BaseScene
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW, COLOR_GREEN,
    COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_WHITE, COLOR_BLACK,
    FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM, FONT_SIZE_XS,
    MAX_HINTS, TOTAL_LEVELS, WINDOW_WIDTH, WINDOW_HEIGHT,
    STAR_THRESHOLDS,
)
from ..ui.components import (
    RoundedButton, HintButton, HintOverlay, StarDisplay,
    FeedbackText, get_font, draw_rounded_rect, draw_text_centered,
)
from ..ui.animations import Tween, ease_out_bounce, ShakeEffect
from .. import save_manager


# Puzzle-Klassen registrieren
_PUZZLE_CLASSES = {}
for _i in range(1, TOTAL_LEVELS + 1):
    mod = importlib.import_module(f".puzzle_{_i:02d}", package="py_brain_it_out.puzzles")
    cls = getattr(mod, f"Puzzle{_i:02d}")
    _PUZZLE_CLASSES[_i] = cls


class GameScene(BaseScene):
    """Szene, die ein einzelnes Puzzle anzeigt."""

    # Höhe des Headers (Fragetext + Hinweis-Button)
    HEADER_H = 95
    # Höhe des Footers (Hinweis-Zähler + Zurück)
    FOOTER_H = 60

    def __init__(self, game, level: int) -> None:
        super().__init__(game)
        self.level = level
        self._hints_left = MAX_HINTS   # Pro Level immer 3 Hinweise
        self._wrong_count = 0
        self._hints_used = 0

        # Puzzle instanziieren
        puzzle_cls = _PUZZLE_CLASSES[level]
        self._puzzle = puzzle_cls(
            game,
            on_solved=self._on_solved,
            on_wrong=self._on_wrong,
        )

        # Spielbereich
        self._play_area = pygame.Rect(
            0, self.HEADER_H,
            WINDOW_WIDTH, WINDOW_HEIGHT - self.HEADER_H - self.FOOTER_H
        )

        # UI-Elemente
        self._hint_btn = HintButton(
            pos=(WINDOW_WIDTH - 48, 48),
            hints_left=self._hints_left,
            on_click=self._show_hint,
        )
        self._back_btn = RoundedButton(
            "← Menü",
            pygame.Rect(12, WINDOW_HEIGHT - self.FOOTER_H + 8, 110, 42),
            color=(140, 130, 125),
            font_size=FONT_SIZE_XS,
            on_click=self._on_back,
        )

        # Zustände
        self._hint_overlay: HintOverlay | None = None
        self._solved = False
        self._success_overlay = False
        self._star_display = StarDisplay(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20),
            star_count=0,
        )
        self._success_tween = Tween(0, 1, 0.5, ease_out_bounce)
        self._success_timer = 0.0
        self._continue_btn: RoundedButton | None = None
        self._feedback_texts: list[FeedbackText] = []
        self._header_shake = ShakeEffect(intensity=4, duration=0.3)

    def on_enter(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        # Erfolgs-Overlay
        if self._success_overlay:
            if self._continue_btn:
                self._continue_btn.handle_event(event)
            return

        # Hinweis-Overlay
        if self._hint_overlay:
            self._hint_overlay.handle_event(event)
            return

        self._back_btn.handle_event(event)
        self._hint_btn.handle_event(event)

        # Event ans Puzzle weiterreichen
        if not self._solved:
            self._puzzle.handle_event(event)

    def update(self, dt: float) -> None:
        if self._success_overlay:
            self._success_tween.update(dt)
            self._star_display.update(dt)
            self._success_timer += dt
            if self._continue_btn:
                self._continue_btn.update(dt)
            return

        if self._hint_overlay:
            self._hint_overlay.update(dt)
            if not self._hint_overlay._active:
                self._hint_overlay = None
            return

        self._back_btn.update(dt)
        self._hint_btn.update(dt)
        self._header_shake.update(dt)
        self._puzzle.update(dt)

        # Feedback-Texte
        self._feedback_texts = [ft for ft in self._feedback_texts if not ft.done]
        for ft in self._feedback_texts:
            ft.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        # Header
        self._draw_header(surface)

        # Puzzle-Spielbereich
        self._puzzle.draw(surface, self._play_area)

        # Footer
        self._draw_footer(surface)

        # Feedback-Texte
        for ft in self._feedback_texts:
            ft.draw(surface)

        # Hinweis-Overlay (obendrüber)
        if self._hint_overlay:
            self._hint_overlay.draw(surface)

        # Erfolgs-Overlay
        if self._success_overlay:
            self._draw_success_overlay(surface)

    def _draw_header(self, surface: pygame.Surface) -> None:
        # Header-Hintergrund
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, self.HEADER_H)
        pygame.draw.rect(surface, COLOR_WHITE, header_rect)
        pygame.draw.line(surface, (220, 210, 200), (0, self.HEADER_H - 1), (WINDOW_WIDTH, self.HEADER_H - 1), 2)

        shake_x = int(self._header_shake.offset_x)

        # Level-Badge
        badge_rect = pygame.Rect(16, 14, 90, 32)
        draw_rounded_rect(surface, COLOR_TEAL, badge_rect, radius=10, shadow_offset=2)
        font_badge = get_font(FONT_SIZE_XS, bold=True)
        badge_surf = font_badge.render(f"Level {self.level}", True, COLOR_WHITE)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # Frage
        font_q = get_font(FONT_SIZE_SM + 2, bold=True)
        q_surf = font_q.render(self._puzzle.QUESTION, True, COLOR_TEXT)
        surface.blit(q_surf, q_surf.get_rect(
            center=(WINDOW_WIDTH // 2 + shake_x, self.HEADER_H // 2)
        ))

        # Hinweis-Button
        self._hint_btn.draw(surface)

        # Fehlversuche-Indikator
        for i in range(3):
            x = 16 + i * 22
            y = self.HEADER_H - 20
            color = COLOR_CORAL if i < self._wrong_count else (220, 210, 200)
            pygame.draw.circle(surface, color, (x, y), 7)

    def _draw_footer(self, surface: pygame.Surface) -> None:
        footer_rect = pygame.Rect(0, WINDOW_HEIGHT - self.FOOTER_H, WINDOW_WIDTH, self.FOOTER_H)
        pygame.draw.rect(surface, COLOR_WHITE, footer_rect)
        pygame.draw.line(surface, (220, 210, 200),
                         (0, WINDOW_HEIGHT - self.FOOTER_H),
                         (WINDOW_WIDTH, WINDOW_HEIGHT - self.FOOTER_H), 2)

        self._back_btn.draw(surface)

        # Fortschritts-Info
        font_info = get_font(FONT_SIZE_XS)
        info = f"Fehlversuche: {self._wrong_count}  |  Hinweise: {self._hints_used}/{MAX_HINTS}"
        info_surf = font_info.render(info, True, COLOR_TEXT_LIGHT)
        surface.blit(info_surf, info_surf.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - self.FOOTER_H // 2)
        ))

    def _draw_success_overlay(self, surface: pygame.Surface) -> None:
        # Dunkles Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(180 * self._success_tween.value))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        # Erfolgs-Karte
        scale = self._success_tween.value
        card_w, card_h = 460, 300
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        cw = int(card_w * scale)
        ch = int(card_h * scale)
        card_rect = pygame.Rect(cx - cw // 2, cy - ch // 2, cw, ch)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=24, shadow_offset=8)

        if scale > 0.5:
            # Titel
            font_title = get_font(FONT_SIZE_LG, bold=True)
            title_surf = font_title.render("🎉 Richtig!", True, COLOR_GREEN)
            surface.blit(title_surf, title_surf.get_rect(center=(cx, cy - 80)))

            # Sterne-Anzeige
            self._star_display.draw(surface)

            # Sterne-Zahl-Text
            stars = self._calc_stars()
            font_sm = get_font(FONT_SIZE_SM)
            star_text = ["⭐ Noch Luft nach oben!", "⭐⭐ Gut gemacht!", "⭐⭐⭐ Perfekt!"][stars - 1]
            st_surf = font_sm.render(star_text, True, COLOR_TEXT)
            surface.blit(st_surf, st_surf.get_rect(center=(cx, cy + 30)))

            # Weiter-Button (erscheint nach kurzer Verzögerung)
            if self._success_timer > 0.8 and self._continue_btn:
                self._continue_btn.draw(surface)

    def _on_solved(self) -> None:
        """Wird vom Puzzle aufgerufen, wenn es gelöst wurde."""
        self._solved = True
        self._success_overlay = True
        stars = self._calc_stars()
        self._star_display.star_count = stars
        self._star_display.start_animation(stars)
        self._success_tween = Tween(0, 1, 0.5, ease_out_bounce)
        self._success_timer = 0.0

        # Fortschritt speichern
        self.game.save_data = save_manager.save_level_result(
            self.game.save_data, self.level, stars
        )
        save_manager.save(self.game.save_data)

        # Weiter-Button
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        if self.level < TOTAL_LEVELS:
            next_label = "Nächstes Level →"
            next_action = self._on_next_level
        else:
            next_label = "🏆 Fertig!"
            next_action = self._on_back_to_menu
        self._continue_btn = RoundedButton(
            next_label,
            pygame.Rect(cx - 120, cy + 65, 240, 55),
            color=COLOR_CORAL,
            font_size=FONT_SIZE_SM,
            on_click=next_action,
        )

    def _on_wrong(self) -> None:
        """Wird vom Puzzle bei falscher Aktion aufgerufen."""
        self._wrong_count += 1
        self._header_shake.start()
        # Feedback-Text
        messages = ["Falsch! 🙅", "Nochmal!", "Denk nach!", "Fast... nicht ganz!"]
        msg = messages[min(self._wrong_count - 1, len(messages) - 1)]
        ft = FeedbackText(
            text=msg,
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
            color=COLOR_CORAL,
            duration=1.2,
        )
        self._feedback_texts.append(ft)

    def _show_hint(self) -> None:
        """Zeigt das Hinweis-Overlay."""
        if self._hints_left <= 0:
            return
        self._hints_left -= 1
        self._hints_used += 1
        self._hint_btn.hints_left = self._hints_left
        self._hint_overlay = HintOverlay(
            hint_text=self._puzzle.HINT,
            on_close=lambda: None,
        )

    def _calc_stars(self) -> int:
        """Berechnet die Sternbewertung."""
        wrong = self._wrong_count
        hints = self._hints_used
        if wrong <= STAR_THRESHOLDS[3][0] and hints <= STAR_THRESHOLDS[3][1]:
            return 3
        elif wrong <= STAR_THRESHOLDS[2][0] and hints <= STAR_THRESHOLDS[2][1]:
            return 2
        return 1

    def _on_next_level(self) -> None:
        self.game.pop_scene()
        from .game_scene import GameScene
        self.game.push_scene(GameScene(self.game, self.level + 1))

    def _on_back(self) -> None:
        self.game.pop_scene()

    def _on_back_to_menu(self) -> None:
        # Alle Szenen bis aufs Hauptmenü entfernen
        while len(self.game.scene_stack) > 1:
            self.game.pop_scene()
