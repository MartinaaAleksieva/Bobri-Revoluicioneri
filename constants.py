import pygame

# Screen dimensions
WIDTH = 1200
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
CAP_COLOR = (101, 67, 33) # Darker brown for the cap
BLUE = (0, 0, 255) # Added Blue color for reloading text

# Game constants for ammo and reload
MAX_AMMO = 15
RELOAD_TIME_SECONDS = 2 # Time in seconds to recharge (reload)
BULLET_DELAY = 350 # Delay between shots in milliseconds

# Stage speeds for difficulty
STAGE_ONE_SPEED = 100
STAGE_TWO_SPEED = 300

# Global variables for UI bounds (initialized in GameManager)
ENEMY_MIN_Y = 0
BEAVER_MAX_Y_UPPER = 0