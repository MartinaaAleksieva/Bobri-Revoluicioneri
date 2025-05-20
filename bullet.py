import pygame
import math
from constants import BLACK

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10  # Bullet speed (pixels per frame)
        self.angle = angle  # Direction in degrees (0 = right, 90 = up)
        self.radius = 5  # Bullet size
        # Rectangle for collision detection and drawing
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        # Move bullet in the direction of the gun's angle
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y -= self.speed * math.sin(rad)
        # Update rect position for collision detection
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen):
        # Draw the bullet as a black circle at its current position
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)