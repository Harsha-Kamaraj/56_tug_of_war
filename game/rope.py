import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = float(screen_width // 2)

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

        self.velocity = 0.0
        self.momentum = 0.0   # < 0: player side is winning, > 0: computer side is winning
        self.tension = 0.0    # 0.0 = slack rope, 1.0 = maximum struggle

        # Rope end points; the engine moves these to follow the pullers' hands
        self.left_end = (60, self.center_y)
        self.right_end = (screen_width - 60, self.center_y)

    def pull_left(self, strength=1.0):
        amount = self.pull_step * strength
        self.marker_x -= amount
        self._register_pull(-amount)

    def pull_right(self, strength=1.0):
        amount = self.pull_step * strength
        self.marker_x += amount
        self._register_pull(amount)

    def _register_pull(self, signed_amount):
        self.momentum += signed_amount
        self.tension = min(1.0, self.tension + 0.08)

    def update(self):
        # Called once per frame: momentum and tension fade when nobody pulls
        self.momentum *= 0.9
        self.tension *= 0.97

    def set_ends(self, left_end, right_end):
        self.left_end = left_end
        self.right_end = right_end

    def rope_y(self, x, now):
        """Height of the rope at screen position x (sag when slack, hum when tense)."""
        lx, ly = self.left_end
        rx, ry = self.right_end
        t = max(0.0, min(1.0, (x - lx) / (rx - lx)))
        base = ly + (ry - ly) * t
        envelope = math.sin(math.pi * t)          # 0 at the hands, 1 in the middle

        sag = (1.0 - self.tension) * 22 * envelope
        hum_amp = max(0.0, self.tension - 0.35) * 7
        hum = hum_amp * math.sin(t * math.pi * 14 + now * 0.05) * envelope
        return base + sag + hum

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0
        self.momentum = 0.0
        self.tension = 0.0

    def render(self, surface):
        now = pygame.time.get_ticks()

        # Rope colour gets brighter/hotter as tension rises
        slack_col = (180, 140, 90)
        tense_col = (235, 175, 95)
        col = tuple(int(s + (t - s) * self.tension) for s, t in zip(slack_col, tense_col))

        lx = int(self.left_end[0])
        rx = int(self.right_end[0])
        points = [(x, self.rope_y(x, now)) for x in range(lx, rx + 1, 6)]
        points.append((rx, self.rope_y(rx, now)))
        pygame.draw.lines(surface, col, False, points, 8)

        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        # The flag rides on the rope, so it bobs with the sag / hum
        flag_y = int(self.rope_y(self.marker_x, now))
        flag_rect = pygame.Rect(int(self.marker_x) - 12, flag_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)