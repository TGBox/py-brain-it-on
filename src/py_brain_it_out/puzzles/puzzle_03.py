"""
puzzle_03.py — Level 3: "Mach das Licht an!"

TRICK: Der Lichtschalter funktioniert erst, wenn der Stecker eingesteckt ist.
Erst Stecker klicken → dann Schalter klicken.
"""
from __future__ import annotations

import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import COLOR_BG, COLOR_TEXT, COLOR_YELLOW, COLOR_WHITE
from ..ui.components import get_font, draw_rounded_rect
from ..ui.animations import ShakeEffect, Tween, ease_out_bounce


class Puzzle03(BasePuzzle):
    LEVEL_NUMBER = 3
    TITLE = "Level 3"
    QUESTION = "Mach das Licht an!"
    HINT = "Funktioniert ein Lichtschalter ohne Strom? Vielleicht musst du erst den Stecker einstecken!"

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._plugged_in = False      # Stecker eingesteckt?
        self._light_on = False        # Licht an?
        self._switch_on = False       # Schalter umgelegt?
        self._shake = ShakeEffect()
        self._plug_dragging = False
        self._plug_pos = [200, 430]   # Stecker-Position (ziehbar)
        self._socket_pos = [200, 300] # Steckdose (Ziel)
        self._drag_offset = [0, 0]
        self._light_alpha = 0
        self._light_tween: Tween | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Stecker ziehen
            px, py = self._plug_pos
            plug_rect = pygame.Rect(px - 20, py - 30, 40, 60)
            if not self._plugged_in and plug_rect.collidepoint(event.pos):
                self._plug_dragging = True
                self._drag_offset = [event.pos[0] - px, event.pos[1] - py]
                return

            # Schalter klicken
            sw_rect = self._get_switch_rect()
            if sw_rect.collidepoint(event.pos):
                if not self._plugged_in:
                    # Falsch: Stecker nicht drin
                    self._wrong()
                    self._shake.start()
                else:
                    self._switch_on = not self._switch_on
                    self._light_on = self._switch_on
                    if self._light_on:
                        self._light_tween = Tween(0, 255, 0.5, ease_out_bounce)
                        self._solve()
                return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._plug_dragging:
                self._plug_dragging = False
                # Prüfen ob Stecker nahe an Steckdose
                px, py = self._plug_pos
                sx, sy = self._socket_pos
                import math
                if math.hypot(px - sx, py - sy) < 50:
                    self._plugged_in = True
                    self._plug_pos = list(self._socket_pos)

        if event.type == pygame.MOUSEMOTION:
            if self._plug_dragging:
                self._plug_pos[0] = event.pos[0] - self._drag_offset[0]
                self._plug_pos[1] = event.pos[1] - self._drag_offset[1]

    def update(self, dt: float) -> None:
        self._shake.update(dt)
        if self._light_tween:
            self._light_alpha = int(self._light_tween.update(dt))
            if self._light_tween.done:
                self._light_tween = None

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y

        # Raum — dunkel wenn Licht aus, hell wenn Licht an
        if self._light_on:
            room_color = (255, 245, 200)
        else:
            room_color = (60, 55, 70)
        surface.fill(room_color, area)

        # Licht-Aura
        if self._light_on:
            light_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Helle Mitte beim Licht
            for radius in range(200, 0, -20):
                alpha = int((200 - radius) * 0.8)
                pygame.draw.circle(light_surf, (255, 240, 150, alpha),
                                   (ox + w // 2, oy + 80), radius)
            surface.blit(light_surf, (0, 0))

        # Glühbirne (oben mitte)
        bulb_cx = ox + w // 2
        bulb_cy = oy + 85
        # Kabel
        pygame.draw.line(surface, (80, 80, 80) if not self._light_on else (60, 60, 60),
                         (bulb_cx, oy + 5), (bulb_cx, bulb_cy - 20), 3)
        # Fassung
        pygame.draw.rect(surface, (100, 90, 80),
                         pygame.Rect(bulb_cx - 12, bulb_cy - 20, 24, 12), border_radius=4)
        # Birne
        bulb_color = COLOR_YELLOW if self._light_on else (140, 130, 100)
        pygame.draw.circle(surface, bulb_color, (bulb_cx, bulb_cy + 5), 28)
        if self._light_on:
            pygame.draw.circle(surface, (255, 255, 220), (bulb_cx - 5, bulb_cy), 10)

        # Steckdose (Ziel)
        sx, sy = self._socket_pos
        self._draw_socket(surface, sx, sy, self._plugged_in)

        # Schalter
        sw_rect = self._get_switch_rect()
        sw_offset = int(self._shake.offset_x)
        sw_draw_rect = sw_rect.move(sw_offset, 0)
        self._draw_switch(surface, sw_draw_rect, self._switch_on, self._plugged_in)

        # Stecker (wenn nicht eingesteckt)
        if not self._plugged_in:
            px, py = self._plug_pos
            self._draw_plug(surface, px, py)
            # Hinweis-Pfeil
            font = get_font(15)
            if not self._plugged_in:
                hint_text = "← Stecker einstecken" if px > sx else "Stecker → Steckdose"
                c = (200, 200, 200) if not self._light_on else (80, 80, 80)
                hint_surf = font.render("Stecker zur Steckdose ziehen!", True, c)
                surface.blit(hint_surf, hint_surf.get_rect(center=(ox + w // 2, oy + h - 25)))
        else:
            font = get_font(16)
            c = (80, 80, 80) if self._light_on else (200, 200, 200)
            tip = font.render("Jetzt den Schalter drücken!", True, c)
            surface.blit(tip, tip.get_rect(center=(ox + w // 2, oy + h - 25)))

    def _draw_socket(self, surface, cx, cy, active):
        color = (220, 210, 200) if not active else (180, 230, 180)
        pygame.draw.rect(surface, color, (cx - 25, cy - 30, 50, 60), border_radius=8)
        pygame.draw.rect(surface, (160, 150, 140), (cx - 25, cy - 30, 50, 60), 2, border_radius=8)
        # Löcher
        if not active:
            pygame.draw.ellipse(surface, (100, 90, 80), (cx - 15, cy - 15, 10, 18))
            pygame.draw.ellipse(surface, (100, 90, 80), (cx + 5, cy - 15, 10, 18))
        else:
            # Stecker drin
            pygame.draw.rect(surface, (80, 150, 80), (cx - 15, cy - 18, 30, 36), border_radius=4)

    def _draw_switch(self, surface, rect, on, enabled):
        bg = (220, 215, 210) if not enabled else (200, 230, 200)
        pygame.draw.rect(surface, bg, rect, border_radius=10)
        pygame.draw.rect(surface, (150, 140, 130), rect, 2, border_radius=10)
        # Toggle-Knopf
        knob_y = rect.y + 8 if on else rect.y + rect.height - 8 - 20
        knob_color = (255, 220, 80) if on else (180, 175, 165)
        pygame.draw.rect(surface, knob_color,
                         (rect.x + 8, knob_y, rect.width - 16, 20), border_radius=6)
        # Label
        font = get_font(13)
        label = "EIN" if on else "AUS"
        label_color = (50, 50, 50) if not enabled else (30, 30, 30)
        lbl = font.render(label, True, label_color)
        surface.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_plug(self, surface, cx, cy):
        """Zeichnet den Stecker."""
        # Körper
        pygame.draw.rect(surface, (200, 190, 180), (cx - 18, cy - 28, 36, 50), border_radius=6)
        pygame.draw.rect(surface, (150, 140, 130), (cx - 18, cy - 28, 36, 50), 2, border_radius=6)
        # Stifte
        pygame.draw.rect(surface, (80, 80, 80), (cx - 10, cy + 22, 6, 16), border_radius=3)
        pygame.draw.rect(surface, (80, 80, 80), (cx + 4, cy + 22, 6, 16), border_radius=3)
        # Kabel
        pygame.draw.line(surface, (60, 55, 70), (cx, cy + 38), (cx, cy + 55), 4)

    def _get_switch_rect(self) -> pygame.Rect:
        from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT
        return pygame.Rect(WINDOW_WIDTH - 130, WINDOW_HEIGHT // 2 - 40, 60, 80)
