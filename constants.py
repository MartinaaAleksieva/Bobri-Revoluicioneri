import pygame

# Screen dimensions
WIDTH = 1200
HEIGHT = 600

# Colors (used for drawing game elements and UI)
WHITE = (255, 255, 255)   # Background and HUD
BLACK = (0, 0, 0)         # Text, bullets, outlines
RED = (255, 0, 0)         # Game over text, HP
BROWN = (139, 69, 19)     # Beaver color (if needed)
GREEN = (0, 255, 0)       # Not used, but available for future features
CAP_COLOR = (101, 67, 33) # Darker brown for the beaver's cap
BLUE = (0, 0, 255)        # Blue color for reloading text

# Game constants for ammo and reload mechanics
MAX_AMMO = 15                 # Maximum bullets before reload
RELOAD_TIME_SECONDS = 2       # Time (in seconds) to reload
BULLET_DELAY = 350            # Delay (in ms) between shots to prevent spamming

# Stage speeds for difficulty scaling
STAGE_ONE_SPEED = 100         # Score threshold for stage 1
STAGE_TWO_SPEED = 300         # Score threshold for stage 2

# Global variables for UI bounds (set in GameManager based on HUD layout)
ENEMY_MIN_Y = 0               # Minimum Y for enemy spawn (keeps enemies below HUD)
BEAVER_MAX_Y_UPPER = 0        # Maximum Y the beaver can move up (keeps beaver below HUD)