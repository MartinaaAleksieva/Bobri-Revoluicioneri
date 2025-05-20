import pygame
import random
import math
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beaver Shooter Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)

# Beaver class
class Beaver:
    def __init__(self):
        self.x = 100  # Fixed x-position
        self.y = HEIGHT - 50  # Ground level
        self.width = 40
        self.height = 40
        self.hp = 30
        self.angle = 0  # Gun angle in degrees (0 = straight, -90 = up, 90 = down)
        self.speed = 5  # Running speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        # Update position (move background instead to simulate running)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle = min(self.angle + 5, 90)  # Limit angle to 90 (down)        
        if keys[pygame.K_DOWN]:
            self.angle = max(self.angle - 5, -90)  # Limit angle to -90 (up)
        if keys[pygame.K_w]:
            self.y = max(self.y - 5, 50)  
        if keys[pygame.K_s]:
            self.y = min(self.y + 5, HEIGHT - 50)  
        # Update rect position
        self.rect.y = self.y

    def draw(self, screen):
        # Draw beaver (simple rectangle)
        pygame.draw.rect(screen, BROWN, self.rect)
        # Draw gun (line from beaver's center)
        gun_length = 30
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2
        rad = math.radians(self.angle)
        gun_end_x = gun_x + gun_length * math.cos(rad)
        gun_end_y = gun_y - gun_length * math.sin(rad)
        pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_end_x, gun_end_y), 3)

    def shoot(self):
        # Create bullet at gun tip
        gun_length = 30
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2
        rad = math.radians(self.angle)
        bullet_x = gun_x + gun_length * math.cos(rad)
        bullet_y = gun_y - gun_length * math.sin(rad)
        return Bullet(bullet_x, bullet_y, self.angle)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.radius = 5
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y -= self.speed * math.sin(rad)
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

# Enemy class
class Enemy:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(50, HEIGHT - 50)
        self.width = 20
        self.height = 20
        self.speed = random.randint(3, 6)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

# GameManager class
class GameManager:
    def __init__(self):
        self.beaver = Beaver()
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.spawn_counter = 0
        self.spawn_interval = 60  # Frames between enemy spawns
        self.font = pygame.font.SysFont("arial", 24)

    def update(self):
        if self.game_over:
            return

        # Update beaver
        self.beaver.update()

        # Update bullets
        self.bullets = [bullet for bullet in self.bullets if 0 < bullet.x < WIDTH and 0 < bullet.y < HEIGHT]
        for bullet in self.bullets:
            bullet.update()

        # Spawn enemies
        self.spawn_counter += 1
        if self.spawn_counter >= self.spawn_interval:
            self.enemies.append(Enemy())
            self.spawn_counter = 0

        # Update enemies
        self.enemies = [enemy for enemy in self.enemies if enemy.x > -enemy.width]
        for enemy in self.enemies:
            enemy.update()

        # Check collisions
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.beaver.rect):
                self.beaver.hp -= 10
                self.enemies.remove(enemy)
                if self.beaver.hp <= 0:
                    self.game_over = True

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break

        # Update score
        # self.score += 0.1

    def draw(self, screen):
        screen.fill(WHITE)
        self.beaver.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {int(self.score)}", True, BLACK)
        hp_text = self.font.render(f"HP: {self.beaver.hp}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(hp_text, (10, 40))
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press R to Restart", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.bullets.append(self.beaver.shoot())
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Restart game
        return True

# Game setup
game = GameManager()

def setup():
    pass  # Initialization handled in GameManager

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
        await asyncio.sleep(1.0 / 60)  # 60 FPS

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())