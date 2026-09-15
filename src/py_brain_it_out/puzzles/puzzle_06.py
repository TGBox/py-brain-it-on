"""
puzzle_06.py — Level 6: "Schreibe die größte Zahl!"

TRICK: Keine Zahl ist groß genug. Aber "unendlich", "∞" oder "Unendlich"
werden akzeptiert — oder der Zahlenwert des Textes übersteigt alles.
"""
from __future__ import annotations

import pygame

from ..puzzles.base_puzzle import BasePuzzle
from ..settings import (
    COLOR_BG, COLOR_CORAL, COLOR_TEXT, COLOR_WHITE,
    COLOR_TEAL, COLOR_YELLOW, FONT_SIZE_LG, FONT_SIZE_MD, FONT_SIZE_SM,
)
from ..ui.components import (
    get_font, draw_rounded_rect, draw_text_centered,
    RoundedButton, TextInputField,
)
from ..ui.animations import ShakeEffect


# Akzeptierte Antworten (Kleinbuchstaben)
_VALID_ANSWERS = {
    "unendlich", "∞", "infinity", "inf",
    "∞ ∞", "unendlichkeit",
}

# Sehr große Zahlen als Schrift (Spaßantwort)
_FUNNY_BIG = {
    "googol", "googolplex", "graham", "grahams zahl",
}


class Puzzle06(BasePuzzle):
    LEVEL_NUMBER = 6
    TITLE = "Level 6"
    QUESTION = "Schreibe die größte Zahl!"
    HINT = "Keine Zahl ist die 'größte'. Aber es gibt etwas, das größer als alle Zahlen ist..."

    def __init__(self, game, on_solved, on_wrong):
        super().__init__(game, on_solved, on_wrong)
        self._shake = ShakeEffect()
        input_rect = pygame.Rect(200, 310, 400, 55)
        self._input = TextInputField(
            input_rect,
            placeholder="Deine Antwort...",
            font_size=FONT_SIZE_MD,
            max_chars=20,
            on_submit=self._check_answer,
        )
        self._input.active = True
        self._submit_btn = RoundedButton(
            "Bestätigen",
            pygame.Rect(300, 385, 200, 50),
            on_click=lambda: self._check_answer(self._input.text),
        )
        self._wrong_count = 0
        self._feedback_text = ""
        self._feedback_timer = 0.0
        self._funny_mode = False  # Wenn sehr große Zahl eingegeben wurde

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._solved:
            return
        self._input.handle_event(event)
        self._submit_btn.handle_event(event)

    def update(self, dt: float) -> None:
        self._shake.update(dt)
        self._input.update(dt)
        self._submit_btn.update(dt)
        if self._feedback_timer > 0:
            self._feedback_timer -= dt

    def draw(self, surface: pygame.Surface, area: pygame.Rect) -> None:
        w, h = area.width, area.height
        ox, oy = area.x, area.y
        surface.fill(COLOR_BG, area)

        # Dekoratives Mathe-Symbol-Hintergrund
        font_deco = get_font(80)
        symbols = ["∞", "∑", "π", "√", "∫"]
        positions = [(100, 150), (650, 130), (120, 420), (680, 420), (400, 480)]
        colors_deco = [(220, 210, 200)] * 5
        for sym, pos, col in zip(symbols, positions, colors_deco):
            s = font_deco.render(sym, True, col)
            surface.blit(s, s.get_rect(center=pos))

        # Nummernlinie (visualisiert die Unmöglichkeit)
        line_y = oy + 230
        pygame.draw.line(surface, (180, 170, 165), (ox + 50, line_y), (ox + w - 50, line_y), 3)
        for i in range(8):
            x = ox + 60 + i * 100
            pygame.draw.line(surface, (160, 150, 145), (x, line_y - 8), (x, line_y + 8), 2)
            num = str(i * 10)
            font_sm = get_font(14)
            n_surf = font_sm.render(num, True, (160, 150, 145))
            surface.blit(n_surf, n_surf.get_rect(center=(x, line_y + 20)))
        # Pfeil ins Unendliche
        arrow_end = (ox + w - 50, line_y)
        pygame.draw.polygon(surface, (180, 170, 165), [
            arrow_end,
            (arrow_end[0] - 12, line_y - 7),
            (arrow_end[0] - 12, line_y + 7),
        ])
        font_inf = get_font(24)
        inf_surf = font_inf.render("→ ∞", True, COLOR_CORAL)
        surface.blit(inf_surf, inf_surf.get_rect(midleft=(ox + w - 80, line_y - 30)))

        # Eingabefeld
        shake_x = int(self._shake.offset_x)
        self._input.rect.x = 200 + shake_x
        self._submit_btn.rect.x = 300 + shake_x
        self._input.draw(surface)
        self._submit_btn.draw(surface)
        self._input.rect.x = 200
        self._submit_btn.rect.x = 300

        # Feedback
        if self._feedback_timer > 0 and self._feedback_text:
            font_fb = get_font(FONT_SIZE_SM)
            alpha = min(255, int(255 * self._feedback_timer))
            fb_surf = font_fb.render(self._feedback_text, True, COLOR_CORAL)
            fb_surf.set_alpha(alpha)
            surface.blit(fb_surf, fb_surf.get_rect(center=(ox + w // 2, oy + h - 40)))

        # Witziger Kommentar nach mehreren Versuchen
        if self._wrong_count >= 2:
            font_joke = get_font(15)
            jokes = [
                "Ist 999999999 wirklich die größte?",
                "Was ist mit einer Million? Einer Milliarde?",
                "Tipp: Zahlen hören nie auf...",
            ]
            joke = jokes[min(self._wrong_count - 2, len(jokes) - 1)]
            j_surf = font_joke.render(joke, True, (160, 150, 145))
            surface.blit(j_surf, j_surf.get_rect(center=(ox + w // 2, oy + h - 25)))

    def _check_answer(self, text: str) -> None:
        if self._solved:
            return
        clean = text.strip().lower().replace(" ", "")
        if clean in _VALID_ANSWERS or clean in _FUNNY_BIG:
            self._solve()
        else:
            # Versuchen, als Zahl zu parsen → immer falsch (keine Zahl ist groß genug)
            self._wrong()
            self._shake.start()
            self._wrong_count += 1
            if self._wrong_count == 1:
                self._feedback_text = f'"{text.strip()}" ist groß, aber nicht die GRÖSSTE!'
            elif self._wrong_count == 2:
                self._feedback_text = "Es gibt immer eine größere Zahl..."
            else:
                self._feedback_text = "Denk mal außerhalb der Zahlen... 😉"
            self._feedback_timer = 3.0
            self._input.clear()
