import pygame
import asyncio
import platform
from game_manager import GameManager
from constants import WIDTH, HEIGHT

# Initialize Pygame
pygame.init()

# Screen dimensions
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beaver Shooter Game")

# Game setup
game = GameManager()

def setup():
    pass

def update_loop():
    running = game.handle_events()
    if not running:
        return False
    game.update()
    game.draw(screen)
    pygame.display.flip()
    return True

async def main():
    setup()
    while True:
        if not update_loop():
            break
        await asyncio.sleep(1.0 / 60) # 60 FPS

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())