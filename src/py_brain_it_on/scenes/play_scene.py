"""
scenes/play_scene.py — Haupt-Spielszene für Brain it on!

Zustandsmaschine:
  DRAWING    → Spieler zeichnet Formen (Physik pausiert)
  SIMULATING → Physik läuft, Formen eingefroren
  SUCCESS    → Ball(e) im Eimer, Erfolgs-Overlay
  FAILED     → Ball außerhalb des Spielfelds (optional, derzeit kein Timeout)
"""
from __future__ import annotations

import importlib
import math
import pygame

from .base_scene import BaseScene
from ..physics.world import PhysicsWorld
from ..physics.drawing import DrawingManager
from ..settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOTAL_LEVELS, STAR_STROKES,
    COLOR_BG, COLOR_WHITE, COLOR_CORAL, COLOR_TEAL, COLOR_GREEN,
    COLOR_YELLOW, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_PANEL,
    FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM, FONT_SIZE_XS,
)
from ..ui.components import (
    RoundedButton, get_font, draw_rounded_rect, draw_star,
)
from ..ui.animations import Tween, ease_out_bounce, ease_out_back
from .. import save_manager

# States
STATE_DRAWING    = "drawing"
STATE_SIMULATING = "simulating"
STATE_SUCCESS    = "success"

# Level-Klassen-Registry
_LEVEL_CLASSES: dict[int, type] = {}
for _i in range(1, TOTAL_LEVELS + 1):
    _mod = importlib.import_module(f".level_{_i:02d}", package="py_brain_it_on.levels")
    _cls = getattr(_mod, f"Level{_i:02d}")
    _LEVEL_CLASSES[_i] = _cls


# ---------------------------------------------------------------------------
# Haupt-Spielszene
# ---------------------------------------------------------------------------

class PlayScene(BaseScene):
    """Spielszene: Zeichnen + Physik + UI."""

    # Bereiche
    HEADER_H = 70
    TOOLBAR_H = 60   # untere Leiste mit Buttons

    def __init__(self, game, level: int) -> None:
        super().__init__(game)
        self.level_num = level
        self._level = _LEVEL_CLASSES[level]()
        self._state = STATE_DRAWING

        self._play_area = pygame.Rect(
            0, self.HEADER_H,
            WINDOW_WIDTH, WINDOW_HEIGHT - self.HEADER_H - self.TOOLBAR_H,
        )

        # Physik & Zeichnen
        self._world: PhysicsWorld | None = None
        self._drawing = DrawingManager()
        self._stroke_count = 0
        self._sim_time = 0.0
        self._success_timer = 0.0

        # Animationen
        self._success_tween = Tween(0, 1, 0.5, ease_out_bounce)
        self._star_display_stars = 0
        self._star_reveal_timer = 0.0

        # Hinweis
        self._hints_left = 3
        self._show_hint = False
        self._hint_timer = 0.0

        # Buttons (Toolbar)
        self._btn_start  = RoundedButton(
            "Starten", pygame.Rect(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT - self.TOOLBAR_H + 8, 150, 44),
            color=COLOR_GREEN, font_size=FONT_SIZE_SM, on_click=self._on_start,
        )
        self._btn_reset  = RoundedButton(
            "Neu zeichnen", pygame.Rect(WINDOW_WIDTH // 2 - 10, WINDOW_HEIGHT - self.TOOLBAR_H + 8, 170, 44),
            color=COLOR_CORAL, font_size=FONT_SIZE_SM, on_click=self._on_reset,
        )
        self._btn_hint   = RoundedButton(
            f"Tipp ({self._hints_left})", pygame.Rect(WINDOW_WIDTH - 140, WINDOW_HEIGHT - self.TOOLBAR_H + 8, 128, 44),
            color=COLOR_YELLOW, font_size=FONT_SIZE_SM, on_click=self._on_hint,
        )
        self._btn_back   = RoundedButton(
            "< Zurueck", pygame.Rect(12, WINDOW_HEIGHT - self.TOOLBAR_H + 8, 120, 44),
            color=(140, 130, 125), font_size=FONT_SIZE_XS, on_click=self._on_back,
        )
        self._btn_next: RoundedButton | None = None

        self._reset_world()

    # ------------------------------------------------------------------
    # Scene-Lifecycle
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._reset_world()

    def on_exit(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Event-Handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        # Erfolgs-Overlay: nur Weiter-Button
        if self._state == STATE_SUCCESS:
            if self._btn_next:
                self._btn_next.handle_event(event)
            self._btn_back.handle_event(event)
            return

        # Toolbar-Buttons
        self._btn_back.handle_event(event)
        self._btn_hint.handle_event(event)

        if self._state in (STATE_DRAWING, STATE_SIMULATING):
            if self._state == STATE_DRAWING:
                self._btn_start.handle_event(event)
            self._btn_reset.handle_event(event)

            # Hinweis schließen
            if self._show_hint and event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self._show_hint = False
                return

            # Zeichnen (nur im Spielbereich)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._play_area.collidepoint(event.pos):
                    self._drawing.start(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self._drawing.is_drawing:
                    self._drawing.add_point(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self._drawing.is_drawing:
                    pts = self._drawing.finish()
                    if pts:
                        self._world.add_drawn_stroke(pts, color=(65, 58, 50))
                        self._stroke_count += 1

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        # Buttons
        self._btn_back.update(dt)
        self._btn_hint.update(dt)

        if self._show_hint:
            self._hint_timer -= dt
            if self._hint_timer <= 0:
                self._show_hint = False

        if self._state == STATE_DRAWING:
            self._btn_start.update(dt)
            self._btn_reset.update(dt)

        elif self._state == STATE_SIMULATING:
            self._btn_reset.update(dt)
            self._sim_time += dt
            self._world.step(dt)

            # Sieg prüfen
            if self._world.all_balls_in_bucket:
                self._success_timer += dt
                if self._success_timer >= 0.6:   # kurz warten, bis zur Ruhe
                    self._on_success()
            else:
                self._success_timer = 0.0

            # Ball außerhalb (unter dem Boden) — Kein Fail, nur Reset-Hint
            self._check_ball_oob()

        elif self._state == STATE_SUCCESS:
            self._success_tween.update(dt)
            self._star_reveal_timer += dt
            if self._btn_next:
                self._btn_next.update(dt)
            self._btn_back.update(dt)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        # Hintergrund
        surface.fill(self._level.BG_COLOR)

        # Level-spezifischer Hintergrund
        self._level.draw_background(surface, self._play_area)

        # Trennlinie Spielbereich
        pygame.draw.line(surface, (200, 192, 180), (0, self.HEADER_H), (WINDOW_WIDTH, self.HEADER_H), 2)
        pygame.draw.line(
            surface, (200, 192, 180),
            (0, WINDOW_HEIGHT - self.TOOLBAR_H),
            (WINDOW_WIDTH, WINDOW_HEIGHT - self.TOOLBAR_H), 2,
        )

        # Physik-Welt zeichnen
        if self._world:
            self._world.draw(surface)

        # Aktueller Strich (Vorschau)
        self._drawing.draw_preview(surface)

        # Toolbar-Hintergrund
        toolbar_rect = pygame.Rect(0, WINDOW_HEIGHT - self.TOOLBAR_H, WINDOW_WIDTH, self.TOOLBAR_H)
        pygame.draw.rect(surface, COLOR_WHITE, toolbar_rect)

        # Header
        self._draw_header(surface)

        # Toolbar-Buttons
        if self._state == STATE_DRAWING:
            self._btn_start.draw(surface)
            self._btn_reset.draw(surface)
        elif self._state == STATE_SIMULATING:
            self._btn_reset.draw(surface)
            # "Physik läuft..." Anzeige
            font_sim = get_font(FONT_SIZE_XS)
            sim_surf = font_sim.render("Physik laeuft...", True, COLOR_TEXT_LIGHT)
            surface.blit(sim_surf, sim_surf.get_rect(
                center=(WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT - self.TOOLBAR_H // 2)
            ))
        self._btn_back.draw(surface)
        self._btn_hint.draw(surface)

        # Strichanzahl
        font_strokes = get_font(FONT_SIZE_XS)
        sc_surf = font_strokes.render(f"Striche: {self._stroke_count}", True, COLOR_TEXT_LIGHT)
        surface.blit(sc_surf, (WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT - self.TOOLBAR_H + 20))

        # Hinweis-Overlay
        if self._show_hint:
            self._draw_hint_overlay(surface)

        # Erfolgs-Overlay
        if self._state == STATE_SUCCESS:
            self._draw_success_overlay(surface)

    # ------------------------------------------------------------------
    # Interne Zeichenmethoden
    # ------------------------------------------------------------------

    def _draw_header(self, surface: pygame.Surface) -> None:
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, self.HEADER_H)
        pygame.draw.rect(surface, COLOR_WHITE, header_rect)

        # Level-Badge
        badge_rect = pygame.Rect(16, 12, 100, 32)
        draw_rounded_rect(surface, COLOR_TEAL, badge_rect, radius=10, shadow_offset=2)
        font_badge = get_font(FONT_SIZE_XS, bold=True)
        badge_surf = font_badge.render(f"Level {self.level_num}", True, COLOR_WHITE)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # Titel
        font_title = get_font(FONT_SIZE_SM, bold=True)
        title_surf = font_title.render(self._level.TITLE, True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, self.HEADER_H // 2)))

        # Ziel-Text
        font_goal = get_font(FONT_SIZE_XS)
        goal_surf = font_goal.render("Bringe den Ball in den Eimer!", True, COLOR_TEXT_LIGHT)
        surface.blit(goal_surf, goal_surf.get_rect(
            center=(WINDOW_WIDTH // 2, self.HEADER_H // 2 + 18)
        ))

        # Zustand-Indikator (Punkt oben rechts)
        state_color = {
            STATE_DRAWING: COLOR_YELLOW,
            STATE_SIMULATING: COLOR_GREEN,
            STATE_SUCCESS: COLOR_TEAL,
        }.get(self._state, COLOR_TEXT_LIGHT)
        state_label = {
            STATE_DRAWING: "Zeichnen",
            STATE_SIMULATING: "Simulation",
            STATE_SUCCESS: "Geschafft!",
        }.get(self._state, "")
        pygame.draw.circle(surface, state_color, (WINDOW_WIDTH - 100, self.HEADER_H // 2), 7)
        font_state = get_font(FONT_SIZE_XS)
        state_surf = font_state.render(state_label, True, state_color)
        surface.blit(state_surf, state_surf.get_rect(midleft=(WINDOW_WIDTH - 88, self.HEADER_H // 2)))

    def _draw_hint_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 500, 200
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=20, shadow_offset=6)

        font_title = get_font(FONT_SIZE_SM, bold=True)
        t_surf = font_title.render("Tipp", True, COLOR_YELLOW)
        # Tipp-Kreis als Icon
        pygame.draw.circle(surface, COLOR_YELLOW, (cx - 60, cy - 30), 12)
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 60, cy - 30), 12, 2)
        surface.blit(t_surf, t_surf.get_rect(center=(cx + 10, cy - 30)))

        font_hint = get_font(FONT_SIZE_SM)
        # Zeilenumbruch
        words = self._level.HINT.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font_hint.size(test)[0] < card_w - 60:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        y = cy - 5
        for line in lines:
            ls = font_hint.render(line, True, COLOR_TEXT)
            surface.blit(ls, ls.get_rect(center=(cx, y)))
            y += font_hint.get_height() + 4

        font_xs = get_font(FONT_SIZE_XS)
        close_s = font_xs.render("Klick zum Schliessen", True, COLOR_TEXT_LIGHT)
        surface.blit(close_s, close_s.get_rect(center=(cx, card_rect.bottom - 20)))

    def _draw_success_overlay(self, surface: pygame.Surface) -> None:
        scale = self._success_tween.value

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        alpha = min(170, int(170 * scale))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 480, 310
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        cw = int(card_w * min(1.0, scale * 1.5))
        ch = int(card_h * min(1.0, scale * 1.5))
        card_rect = pygame.Rect(cx - cw // 2, cy - ch // 2, cw, ch)
        draw_rounded_rect(surface, COLOR_WHITE, card_rect, radius=24, shadow_offset=10)

        if scale > 0.4:
            font_big = get_font(FONT_SIZE_LG, bold=True)
            ok_surf = font_big.render("Geschafft!", True, COLOR_GREEN)
            surface.blit(ok_surf, ok_surf.get_rect(center=(cx, cy - 90)))

            # Sterne zeichnen
            star_r = 28
            spacing = int(star_r * 2.8)
            star_y = cy - 20
            for i in range(3):
                sx = cx - spacing + i * spacing
                filled = i < self._star_display_stars and self._star_reveal_timer > i * 0.3 + 0.2
                draw_star(surface, (sx, star_y), star_r, filled=filled)

            font_sm = get_font(FONT_SIZE_SM)
            labels = ["Gut gemacht!", "Super!", "Perfekt!"]
            lbl = labels[self._star_display_stars - 1] if self._star_display_stars > 0 else ""
            lbl_surf = font_sm.render(lbl, True, COLOR_TEXT_LIGHT)
            surface.blit(lbl_surf, lbl_surf.get_rect(center=(cx, cy + 40)))

            # Strich-Info
            stroke_info = get_font(FONT_SIZE_XS).render(
                f"{self._stroke_count} Strich(e) benutzt", True, COLOR_TEXT_LIGHT
            )
            surface.blit(stroke_info, stroke_info.get_rect(center=(cx, cy + 68)))

            # Weiter-Button
            if self._star_reveal_timer > 1.0 and self._btn_next:
                self._btn_next.draw(surface)
            self._btn_back.draw(surface)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        """Starte die Physik-Simulation."""
        if self._state != STATE_DRAWING:
            return
        self._state = STATE_SIMULATING
        self._sim_time = 0.0

    def _on_reset(self) -> None:
        """Setzt gezeichnete Formen zurück (Bälle werden neu platziert)."""
        self._reset_world()

    def _on_hint(self) -> None:
        if self._hints_left <= 0:
            return
        self._hints_left -= 1
        self._btn_hint.text = f"Tipp ({self._hints_left})"
        self._show_hint = True
        self._hint_timer = 8.0  # 8 Sekunden Anzeigedauer

    def _on_success(self) -> None:
        if self._state == STATE_SUCCESS:
            return
        self._state = STATE_SUCCESS
        self._success_tween = Tween(0, 1, 0.55, ease_out_bounce)
        self._star_reveal_timer = 0.0

        # Sternebewertung
        if self._stroke_count <= STAR_STROKES[3]:
            self._star_display_stars = 3
        elif self._stroke_count <= STAR_STROKES[2]:
            self._star_display_stars = 2
        else:
            self._star_display_stars = 1

        # Fortschritt speichern
        self.game.save_data = save_manager.save_level_result(
            self.game.save_data, self.level_num, self._star_display_stars
        )
        save_manager.save(self.game.save_data)

        # Weiter-Button aufbauen
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        if self.level_num < TOTAL_LEVELS:
            label = "Naechstes Level"
            action = self._on_next_level
        else:
            label = "Alle Level!"
            action = self._on_back_to_menu
        self._btn_next = RoundedButton(
            label,
            pygame.Rect(cx - 120, cy + 100, 240, 52),
            color=COLOR_CORAL,
            font_size=FONT_SIZE_SM,
            on_click=action,
        )

    def _on_back(self) -> None:
        self.game.pop_scene()

    def _on_next_level(self) -> None:
        self.game.pop_scene()
        self.game.push_scene(PlayScene(self.game, self.level_num + 1))

    def _on_back_to_menu(self) -> None:
        while len(self.game.scene_stack) > 1:
            self.game.pop_scene()

    # ------------------------------------------------------------------
    # Hilfsmethoden
    # ------------------------------------------------------------------

    def _reset_world(self) -> None:
        """Erstellt eine frische Physik-Welt mit dem Level-Setup."""
        self._world = PhysicsWorld()
        self._level.setup(self._world)
        self._drawing.cancel()
        self._stroke_count = 0
        self._sim_time = 0.0
        self._success_timer = 0.0
        self._state = STATE_DRAWING
        self._show_hint = False

    def _check_ball_oob(self) -> None:
        """Prüft, ob Bälle aus dem Spielfeld gefallen sind."""
        for ball in self._world.balls:
            pos = ball.body.position
            # Weit unterhalb des Spielfelds → Reset-Hinweis
            if pos.y > WINDOW_HEIGHT + 100:
                pass  # Ball kommt durch Border-Wall nicht raus, aber sicher ist sicher
