import pygame
import random
import math
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Screen dimensions
STAGE_ONE_SPEED = 100
STAGE_TWO_SPEED = 300

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
CAP_COLOR = (101, 67, 33) # Darker brown for the cap
BLUE = (0, 0, 255) # Added Blue color for reloading text

# Game constants for ammo and reload
MAX_AMMO = 15
RELOAD_TIME_SECONDS = 2 # Time in seconds to recharge (reload)

# Define the lower bound for enemy spawning and upper bound for beaver/bullets based on UI
ENEMY_MIN_Y = 0 # Placeholder, will be updated based on ammo text position
BEAVER_MAX_Y_UPPER = 0 # Placeholder, will be updated based on ammo text position
# BULLET_MIN_Y will be the same as ENEMY_MIN_Y/BEAVER_MAX_Y_UPPER

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

        # Ammo and Reloading attributes
        self.max_ammo = MAX_AMMO
        self.current_ammo = self.max_ammo
        self.reloading = False
        self.reload_timer = 0 # This will store the time when reload started (in milliseconds)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle = min(self.angle + 5, 90)
        if keys[pygame.K_DOWN]:
            self.angle = max(self.angle - 5, -90)
        if keys[pygame.K_w]:
            # Ensure beaver doesn't go above the calculated upper limit (ammo line)
            self.y = max(self.y - 5, BEAVER_MAX_Y_UPPER)
        if keys[pygame.K_s]:
            self.y = min(self.y + 5, HEIGHT - 50)
        # Update rect position after y movement
        self.rect.y = self.y

    def draw(self, screen):
        # Draw beaver (simple rectangle)
        pygame.draw.rect(screen, BROWN, self.rect)

        # Draw the CAP
        cap_width = self.width * 0.75
        cap_height = self.height * 0.3
        cap_x = self.x + (self.width - cap_width) / 2
        cap_y = self.y - cap_height

        pygame.draw.rect(screen, CAP_COLOR, (cap_x, cap_y, cap_width, cap_height))

        brim_width = cap_width * 0.6
        brim_height = 5
        brim_x = cap_x + cap_width * 0.4
        brim_y = cap_y + cap_height - (brim_height / 2)
        pygame.draw.rect(screen, CAP_COLOR, (brim_x, brim_y, brim_width, brim_height))

        # Draw gun (line from beaver's center)
        gun_length = 30
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2
        rad = math.radians(self.angle)
        gun_end_x = gun_x + gun_length * math.cos(rad)
        gun_end_y = gun_y - gun_length * math.sin(rad)
        pygame.draw.line(screen, BLACK, (gun_x, gun_y), (gun_end_x, gun_end_y), 3)

    def shoot(self):
        # Only shoot if there's ammo and not currently reloading
        if self.current_ammo > 0 and not self.reloading:
            gun_length = 30
            gun_x = self.x + self.width
            gun_y = self.y + self.height // 2
            rad = math.radians(self.angle)
            bullet_x = gun_x + gun_length * math.cos(rad)
            bullet_y = gun_y - gun_length * math.sin(rad)
            self.current_ammo -= 1 # Decrease ammo count
            return Bullet(bullet_x, bullet_y, self.angle)
        return None # Return None if unable to shoot

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
    def __init__(self, score=0):
        self.x = WIDTH
        # Use the global ENEMY_MIN_Y for random Y generation
        # Ensure enemy spawn Y is at least ENEMY_MIN_Y and not too low
        self.y = random.randint(int(ENEMY_MIN_Y), HEIGHT - 50)
        self.width = 20
        self.height = 20
        # Set speed based on score (difficulty stages)
        if score < STAGE_ONE_SPEED:
            self.speed = random.randint(1, 3)
        elif score < STAGE_TWO_SPEED:
            self.speed = random.randint(3, 5)
        else:
            self.speed = random.randint(5, 8)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
        # Ensure enemy doesn't go below the ENEMY_MIN_Y (move upwards into UI)
        if self.rect.y < ENEMY_MIN_Y:
            self.rect.y = int(ENEMY_MIN_Y)


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
        # New font for the reloading message: larger and bold
        self.reloading_font = pygame.font.SysFont("arial", 48, bold=True)


        # Define a font for initial text sizing to set ENEMY_MIN_Y and BEAVER_MAX_Y_UPPER
        temp_font = pygame.font.SysFont("arial", 24)
        # Calculate the bottom edge of the ammo text
        # Ammo is displayed at (10, 40). Its top is 40.
        ammo_text_height = temp_font.render(f"Ammo: {MAX_AMMO}/{MAX_AMMO}", True, BLACK).get_height()
        
        # --- MODIFIED LINES FOR LOWERING BEAVER AND ENEMIES ---
        # We increase the Y-coordinate to push them lower on the screen
        vertical_offset = 30 # Adjust this value to make them higher/lower
        
        global ENEMY_MIN_Y
        # ENEMY_MIN_Y is where the top of an enemy can be. We add the offset.
        ENEMY_MIN_Y = 40 + ammo_text_height + 5 + vertical_offset

        global BEAVER_MAX_Y_UPPER
        # BEAVER_MAX_Y_UPPER is the lowest Y (highest point) the beaver's top can reach.
        # It's set to the same value as ENEMY_MIN_Y so the beaver also stays below the HUD.
        BEAVER_MAX_Y_UPPER = ENEMY_MIN_Y
        # --- END MODIFIED LINES ---


    def update(self):
        if self.game_over:
            return

        # Handle reloading mechanics
        if self.beaver.reloading:
            current_time = pygame.time.get_ticks() # Get current time in milliseconds
            # Check if enough time has passed for reloading
            if current_time - self.beaver.reload_timer >= RELOAD_TIME_SECONDS * 1000:
                self.beaver.current_ammo = self.beaver.max_ammo # Reload to max ammo
                self.beaver.reloading = False # Stop reloading
                self.beaver.reload_timer = 0 # Reset timer

        # Update beaver
        self.beaver.update()

        # Update bullets
        # Keep bullets only if they are within screen bounds AND below the ENEMY_MIN_Y (which is now our HUD boundary)
        # --- MODIFIED LINE FOR BULLET BOUNDARY ---
        self.bullets = [bullet for bullet in self.bullets if 0 < bullet.x < WIDTH and bullet.y > 0 and bullet.y >= ENEMY_MIN_Y]
        # --- END MODIFIED LINE ---
        for bullet in self.bullets:
            bullet.update()

        # Spawn enemies (passing current score for difficulty scaling)
        self.spawn_counter += 1
        if self.spawn_counter >= self.spawn_interval:
            self.enemies.append(Enemy(self.score)) # Pass the current score to Enemy constructor
            self.spawn_counter = 0

        # Update enemies
        # Keep enemies only if they are still on screen (not passed the left edge)
        self.enemies = [enemy for enemy in self.enemies if enemy.x > -enemy.width]
        for enemy in self.enemies:
            enemy.update()
            # Ensure enemy doesn't move above the ENEMY_MIN_Y (which is just below the ammo text)
            if enemy.rect.y < ENEMY_MIN_Y:
                enemy.rect.y = int(ENEMY_MIN_Y)


        # Check collisions: Enemy with Beaver
        # Iterate over a copy of the list to safely remove elements
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.beaver.rect):
                self.beaver.hp -= 10
                self.enemies.remove(enemy) # Remove enemy if it hits the beaver
                if self.beaver.hp <= 0:
                    self.game_over = True

        # Check collisions: Bullet with Enemy
        bullets_to_keep = []
        for bullet in self.bullets:
            hit_enemy = False
            for enemy in self.enemies[:]: # Iterate over a copy of enemies
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy) # Remove enemy
                    self.score += 10 # Increase score
                    hit_enemy = True
                    break # Bullet hit an enemy, so this bullet is "used"
            if not hit_enemy:
                bullets_to_keep.append(bullet) # Keep bullet if it didn't hit any enemy
        self.bullets = bullets_to_keep


    def draw(self, screen):
        screen.fill(WHITE)
        self.beaver.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        # Draw HUD (Score, HP, Stage, Ammo)

        # HP (top left)
        hp_text = self.font.render(f"HP: {self.beaver.hp}", True, BLACK)
        screen.blit(hp_text, (10, 10))

        # Ammo (top left, below HP)
        ammo_text = self.font.render(f"Ammo: {self.beaver.current_ammo}/{self.beaver.max_ammo}", True, BLACK)
        screen.blit(ammo_text, (10, 40)) # Position of the ammo text

        # Determine stage
        if self.score < STAGE_ONE_SPEED:
            stage = 1
        elif self.score < STAGE_TWO_SPEED:
            stage = 2
        else:
            stage = 3
        stage_text = self.font.render(f"Stage: {stage}", True, BLACK)

        # Center the stage text
        stage_text_rect = stage_text.get_rect(center=(WIDTH // 2, 25)) # Center the text horizontally, 25 pixels from top
        screen.blit(stage_text, stage_text_rect)

        # Score (top right)
        score_text = self.font.render(f"Score: {int(self.score)}", True, BLACK)
        score_rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(score_text, score_rect)


        # Display reloading message
        if self.beaver.reloading:
            reloading_text = self.reloading_font.render("RELOADING...", True, BLUE) # Changed color to BLUE
            # Center the reloading text on screen (vertically centered)
            reloading_text_rect = reloading_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(reloading_text, reloading_text_rect)


        # Display Game Over message
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press R to Restart", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # Centered this too
            screen.blit(game_over_text, game_over_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Attempt to shoot, and only add bullet if shoot was successful (returned a bullet)
                    bullet = self.beaver.shoot()
                    if bullet:
                        self.bullets.append(bullet)
                    # If tried to shoot but ammo was 0 and not already reloading, start reload
                    elif self.beaver.current_ammo == 0 and not self.beaver.reloading:
                        self.beaver.reloading = True
                        self.beaver.reload_timer = pygame.time.get_ticks() # Record start time

                # Handle 'R' key for restart or manual reload
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.__init__()  # Restart game
                    # Manual reload: only if game not over, not already reloading, and ammo not full
                    elif not self.beaver.reloading and self.beaver.current_ammo < self.beaver.max_ammo:
                        self.beaver.reloading = True
                        self.beaver.reload_timer = pygame.time.get_ticks()

        return True

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