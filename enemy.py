import pygame
import random
import constants # Import constants module

class Enemy:
    def __init__(self, score=0):
        self.x = constants.WIDTH  # Start at the far right edge of the screen
        self.width = 100
        self.height = 80
        
        # Calculate min_y and max_y for enemy spawning and movement
        # min_y: Top boundary (just below the HUD, set by GameManager)
        # max_y: Bottom boundary (bottom of the screen, ensures enemy is fully visible)
        self.min_y = int(constants.ENEMY_MIN_Y)
        self.max_y = constants.HEIGHT - self.height
        
        # Randomly spawn within the valid vertical range (between HUD and bottom)
        self.y = random.randint(self.min_y, self.max_y)
        
        # Load and scale the enemy image (vidra)
        self.image = pygame.image.load("vidra.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
        # Set speed based on score (difficulty increases as score increases)
        if score < constants.STAGE_ONE_SPEED:
            self.speed = random.randint(1, 3)
        elif score < constants.STAGE_TWO_SPEED:
            self.speed = random.randint(3, 5)
        else:
            self.speed = random.randint(5, 8)
        # Create a rect for collision detection and movement
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed  # Move enemy leftwards
        self.rect.x = self.x  # Update rect's x position
        
        # --- Apply vertical constraints during update ---
        # Ensure enemy doesn't go above the min_y (HUD boundary)
        self.y = max(self.y, self.min_y)
        # Ensure enemy doesn't go below the max_y (bottom of screen)
        self.y = min(self.y, self.max_y)
        self.rect.y = self.y # Update rect's y after clamping

    def draw(self, screen):
        # Draw the enemy sprite at its current position
        screen.blit(self.image, (self.x, self.y))