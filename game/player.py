import math
import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    SKIN = (240, 210, 180)

    def __init__(self, x, y, color, label, facing=1):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.facing = facing      # +1: rope is to the right (player), -1: rope is to the left (computer)
        self.lean = 10.0          # current backward lean in degrees
        self.target_lean = 10.0
        self.font = pygame.font.SysFont(None, 24)

    def set_momentum(self, advantage):
        """advantage: -1.0 (losing hard) .. +1.0 (winning hard)."""
        self.target_lean = 12 + 16 * advantage     # about -4 deg (stumbling forward) .. 28 deg (heaving back)

    def update(self):
        # Ease towards the target so the lean looks smooth
        self.lean += (self.target_lean - self.lean) * 0.15

    def _point(self, along, across):
        """Point on the body: 'along' = distance up from the feet, 'across' = towards the rope."""
        a = math.radians(self.lean)
        f = self.facing
        up = (-f * math.sin(a), -math.cos(a))      # leaning back tilts the top away from the rope
        side = (f * math.cos(a), -math.sin(a))     # perpendicular, pointing at the rope
        feet_x, feet_y = self.x, self.y + 35
        return (feet_x + up[0] * along + side[0] * across,
                feet_y + up[1] * along + side[1] * across)

    def hand_pos(self):
        return self._point(35, 30)

    def render(self, surface):
        """Draw avatar (leaning) and label."""
        # Body
        body = [self._point(0, -20), self._point(0, 20), self._point(70, 20), self._point(70, -20)]
        pygame.draw.polygon(surface, self.color, body)

        # Arm reaching to the rope
        pygame.draw.line(surface, self.SKIN, self._point(58, 8), self.hand_pos(), 6)

        # Head
        hx, hy = self._point(86, 0)
        pygame.draw.circle(surface, self.SKIN, (int(hx), int(hy)), 16)

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))