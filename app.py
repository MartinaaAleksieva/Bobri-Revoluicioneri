import pygame
import asyncio
import platform
from game_manager import GameManager
from constants import WIDTH, HEIGHT

# Initialize Pygame and set up the main window
pygame.init()

# Create the game window with specified width and height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beaver Shooter Game")

# Instantiate the main game manager (handles all game logic and state)
game = GameManager()

def setup():
    # Placeholder for any future setup logic (currently unused)
    pass

def update_loop():
    # Handle user input/events; if user quits, stop the loop
    running = game.handle_events()
    if not running:
        return False
    # Update game state (movement, collisions, etc.)
    game.update()
    # Draw everything to the screen
    game.draw(screen)
    # Refresh the display
    pygame.display.flip()
    return True

async def main():
    setup()  # Run any setup code
    while True:
        if not update_loop():
            break  # Exit loop if user quits
        await asyncio.sleep(1.0 / 60) # Run at ~60 FPS

# Entry point: run the game loop depending on platform
if platform.system() == "Emscripten":
    # For web (Pyodide/emscripten), use ensure_future
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())