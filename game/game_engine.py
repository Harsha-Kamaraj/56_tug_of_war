import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)", facing=1)
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER", facing=-1)

        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

                # Computer AI settings
        self.base_pull_cooldown = 180      # ms between pulls when calm
        self.panic_threshold = 0.5         # panic once the player is 50% of the way to winning
        self.panic_min_cooldown = 120      # fastest pull interval at max panic (ms)
        self.panic_max_strength = 1.4      # strongest pull multiplier at max panic
        self.is_panicking = False
        self.last_computer_pull = pygame.time.get_ticks()
                # Match timer & sudden death
        self.match_duration = 45000        # ms before sudden death kicks in
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False
        self.power_multiplier = 1.0

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # Count a pull on every KEYDOWN that alternates from the previous key.
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
            if event.key != self.last_key:
                self.rope.pull_left(1.0 * self.power_multiplier)
                self.last_key = event.key
        
    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        # Match timer: switch to sudden death after 45 s
        self.elapsed_ms = now - self.match_start
        if not self.sudden_death and self.elapsed_ms >= self.match_duration:
            self.sudden_death = True
            self.power_multiplier = 2.0

        # danger: 0.0 = flag at centre (or on computer's side), 1.0 = flag at player's goal line
        center = self.width / 2
        danger = (center - self.rope.marker_x) / (center - self.rope.left_win_x)
        danger = max(0.0, min(1.0, danger))

        self.is_panicking = danger >= self.panic_threshold
        if self.is_panicking:
            # surge: 0.0 when panic just starts, 1.0 when the player is about to win
            surge = (danger - self.panic_threshold) / (1.0 - self.panic_threshold)
            cooldown = self.base_pull_cooldown - (self.base_pull_cooldown - self.panic_min_cooldown) * surge
            strength_boost = 1.0 + (self.panic_max_strength - 1.0) * surge
        else:
            cooldown = self.base_pull_cooldown
            strength_boost = 1.0

        if now - self.last_computer_pull >= cooldown:
            computer_variance = random.uniform(0.7, 1.2)
            self.rope.pull_right(computer_variance * strength_boost * self.power_multiplier)
            self.last_computer_pull = now

        self.update_animations()
        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def update_animations(self):
        self.rope.update()
        # advantage: +1 = player winning hard, -1 = computer winning hard
        advantage = max(-1.0, min(1.0, -self.rope.momentum / 20.0))
        self.player.set_momentum(advantage)
        self.computer.set_momentum(-advantage)
        self.player.update()
        self.computer.update()
        self.rope.set_ends(self.player.hand_pos(), self.computer.hand_pos())        

    def reset(self):
        self.rope.reset()
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.is_panicking = False
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False
        self.power_multiplier = 1.0

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen)
        self.player.render(screen)
        self.computer.render(screen)

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))
        # Match timer at the top
        seconds = self.elapsed_ms // 1000
        clock_text = f"{seconds // 60}:{seconds % 60:02d}"
        if self.sudden_death:
            timer_text = f"TIME {clock_text}  |  SUDDEN DEATH - 2x POWER!"
            timer_col = (255, 80, 80)
        else:
            left = (self.match_duration - self.elapsed_ms + 999) // 1000
            timer_text = f"TIME {clock_text}  |  Sudden death in {left}s"
            timer_col = (240, 240, 240)
        timer_surf = self.font_small.render(timer_text, True, timer_col)
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 12))

        # Big sudden death banner at the bottom
        if self.sudden_death and self.game_state == "PLAYING":
            sd_surf = self.font_big.render("SUDDEN DEATH!", True, (255, 60, 60))
            screen.blit(sd_surf, (self.width // 2 - sd_surf.get_width() // 2, self.height - 70))
        if self.is_panicking and self.game_state == "PLAYING":
            # Flash on/off every 150 ms
            if (pygame.time.get_ticks() // 150) % 2 == 0:
                panic_surf = self.font_big.render("PANIC SURGE!", True, (255, 70, 70))
                screen.blit(panic_surf, (self.width // 2 - panic_surf.get_width() // 2, 80))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
