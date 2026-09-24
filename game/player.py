import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

    def render(self, surface):
        """Draw avatar and label."""
        # Body
        body_rect = pygame.Rect(self.x - 20, self.y - 35, 40, 70)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=6)

        # Head
        pygame.draw.circle(surface, (240, 210, 180), (self.x, self.y - 50), 16)

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))