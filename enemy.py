import pygame
import random
import constants # Import constants module

class Enemy:
    def __init__(self, score=0):
        self.x = constants.WIDTH
        self.width = 100
        self.height = 80
        
        # Calculate min_y and max_y for enemy spawning and movement
        # Upper limit: ENEMY_MIN_Y (below the UI)
        # Lower limit: constants.HEIGHT - self.height (bottom of the screen, ensuring full visibility)
        self.min_y = int(constants.ENEMY_MIN_Y)
        self.max_y = constants.HEIGHT - self.height # Ensures enemy stays fully on screen below the game area
        
        # Randomly spawn within the valid vertical range
        self.y = random.randint(self.min_y, self.max_y)
        
        self.image = pygame.image.load("vidra.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
        if score < constants.STAGE_ONE_SPEED:
            self.speed = random.randint(1, 3)
        elif score < constants.STAGE_TWO_SPEED:
            self.speed = random.randint(3, 5)
        else:
            self.speed = random.randint(5, 8)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
        
        # Apply vertical constraints during update
        # Ensure enemy doesn't go above the min_y (UI boundary)
        self.y = max(self.y, self.min_y)
        # Ensure enemy doesn't go below the max_y (bottom of screen)
        self.y = min(self.y, self.max_y)
        self.rect.y = self.y # Update rect's y after clamping

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))