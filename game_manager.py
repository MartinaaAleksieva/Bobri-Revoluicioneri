import pygame
from beaver import Beaver
from enemy import Enemy
import constants # Import constants module to access and modify shared variables

class GameManager:
    def __init__(self):
        # --- UI boundary calculation for HUD and game area ---
        temp_font = pygame.font.SysFont("arial", 24)
        ammo_text_height = temp_font.render(f"Ammo: {constants.MAX_AMMO}/{constants.MAX_AMMO}", True, constants.BLACK).get_height()
        vertical_offset = 30 # Space below ammo text for game area
        # Calculate the minimum Y for game elements to stay below the HUD
        calculated_min_y_for_game_area = 40 + ammo_text_height + 5 + vertical_offset
        # Update global constants for use in Beaver and Enemy
        constants.ENEMY_MIN_Y = calculated_min_y_for_game_area
        constants.BEAVER_MAX_Y_UPPER = calculated_min_y_for_game_area

        # --- Game state initialization ---
        self.beaver = Beaver() # Main player character
        self.bullets = []      # List of active bullets
        self.enemies = []      # List of active enemies
        self.score = 0         # Player's score
        self.game_over = False # Game over state
        self.spawn_counter = 0 # Counter for enemy spawn timing
        self.spawn_interval = 60  # Frames between enemy spawns
        self.font = pygame.font.SysFont("arial", 24) # Main font
        self.reloading_font = pygame.font.SysFont("arial", 24, bold=True) # Font for reloading message
        self.scream_played = False # Track if game over sound played
        self.scream_sound = pygame.mixer.Sound("screaming_beaver.mp3") # Game over sound
        # Load and scale the end game image for game over background
        self.end_image = pygame.image.load("endImg.jpeg").convert()
        self.end_image = pygame.transform.scale(self.end_image, (constants.WIDTH, constants.HEIGHT))

    def update(self):
        if self.game_over:
            # Play game over sound and clear enemies
            if not self.scream_played:
                self.scream_sound.play()
                self.scream_played = True
            self.enemies = []
            return

        # --- Handle reloading mechanics ---
        if self.beaver.reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.beaver.reload_timer >= constants.RELOAD_TIME_SECONDS * 1000:
                self.beaver.current_ammo = self.beaver.max_ammo
                self.beaver.reloading = False
                self.beaver.reload_timer = 0

        self.beaver.update() # Update player movement and state

        # --- Update bullets ---
        # Only keep bullets within screen and below HUD
        self.bullets = [bullet for bullet in self.bullets if 
                        0 < bullet.x < constants.WIDTH and 
                        bullet.y > 0 and 
                        bullet.y >= constants.ENEMY_MIN_Y]
        for bullet in self.bullets:
            bullet.update()

        # --- Enemy spawning ---
        self.spawn_counter += 1
        if self.spawn_counter >= self.spawn_interval:
            self.enemies.append(Enemy(self.score)) # Spawn new enemy
            self.spawn_counter = 0

        # --- Update enemies, prevent merging, handle off-screen ---
        enemies_to_keep = []
        for i, enemy in enumerate(self.enemies):
            enemy.update()
            from constants import ENEMY_MIN_Y
            if enemy.rect.y < ENEMY_MIN_Y:
                enemy.rect.y = int(ENEMY_MIN_Y)
            # Prevent merging: if two enemies overlap, move the one behind
            for prev_enemy in self.enemies[:i]:
                if enemy.rect.colliderect(prev_enemy.rect):
                    enemy.x = prev_enemy.x + prev_enemy.width
                    enemy.rect.x = enemy.x
            # If enemy goes off screen, penalize score and check for game over
            if enemy.x <= -enemy.width:
                if self.score > 0:
                    self.score = max(0, self.score - 10)
                    if self.score == 0:
                        self.game_over = True
                # If score is already 0, just remove the enemy
            else:
                enemies_to_keep.append(enemy)
        self.enemies = enemies_to_keep

        # --- Collision: Enemy with Beaver ---
        for enemy in self.enemies[:]: 
            if enemy.rect.colliderect(self.beaver.rect):
                self.beaver.hp -= 10 # Lose HP on collision
                self.enemies.remove(enemy) 
                if self.beaver.hp <= 0:
                    self.game_over = True

        # --- Collision: Bullet with Enemy ---
        bullets_to_keep = []
        for bullet in self.bullets:
            hit_enemy = False
            for enemy in self.enemies[:]: 
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy) 
                    self.score += 10 
                    hit_enemy = True
                    break 
            if not hit_enemy:
                bullets_to_keep.append(bullet) 
        self.bullets = bullets_to_keep

    def draw(self, screen):
        if self.game_over:
            # Draw end image as background on game over
            screen.blit(self.end_image, (0, 0))
        else:
            screen.fill((255, 255, 255)) # Fill with WHITE from constants
        self.beaver.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        # --- Draw HUD (Score, HP, Stage, Ammo) ---
        # HP (top left)
        hp_text = self.font.render(f"HP: {self.beaver.hp}", True, constants.BLACK)
        screen.blit(hp_text, (10, 10))
        # Ammo (top left, below HP)
        ammo_text = self.font.render(f"Ammo: {self.beaver.current_ammo}/{self.beaver.max_ammo}", True, constants.BLACK)
        screen.blit(ammo_text, (10, 40))
        # Stage (centered at top)
        if self.score < constants.STAGE_ONE_SPEED:
            stage = 1
        elif self.score < constants.STAGE_TWO_SPEED:
            stage = 2
        else:
            stage = 3
        stage_text = self.font.render(f"Stage: {stage}", True, constants.BLACK)
        stage_text_rect = stage_text.get_rect(center=(constants.WIDTH // 2, 25)) 
        screen.blit(stage_text, stage_text_rect)
        # Score (top right)
        score_text = self.font.render(f"Score: {int(self.score)}", True, constants.BLACK)
        score_rect = score_text.get_rect(topright=(constants.WIDTH - 10, 10))
        screen.blit(score_text, score_rect)
        # Display reloading message below the stage text
        if self.beaver.reloading:
            reloading_text = self.reloading_font.render("RELOADING...", True, constants.BLUE)
            reloading_text_rect = reloading_text.get_rect(center=(constants.WIDTH // 2, stage_text_rect.bottom + 20))
            screen.blit(reloading_text, reloading_text_rect)
        # Display Game Over message (large, bold, with shadow and outline)
        if self.game_over:
            big_font = pygame.font.SysFont("arial", 56, bold=True)
            text = "Game Over! Press R to Restart"
            # Draw shadow
            shadow = big_font.render(text, True, (0,0,0))
            shadow_rect = shadow.get_rect(center=(constants.WIDTH // 2, constants.HEIGHT // 2 + 3))
            screen.blit(shadow, shadow_rect)
            # Draw outline (white)
            outline = big_font.render(text, True, (255,255,255))
            outline_rect = outline.get_rect(center=(constants.WIDTH // 2, constants.HEIGHT // 2 - 3))
            screen.blit(outline, outline_rect)
            # Draw main text (red)
            game_over_text = big_font.render(text, True, constants.RED)
            game_over_rect = game_over_text.get_rect(center=(constants.WIDTH // 2, constants.HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # Handle shooting
                if event.key == pygame.K_SPACE and not self.game_over:
                    bullet = self.beaver.shoot()
                    if bullet:
                        self.bullets.append(bullet)
                    elif self.beaver.current_ammo == 0 and not self.beaver.reloading:
                        self.beaver.reloading = True
                        self.beaver.reload_timer = pygame.time.get_ticks()
                # Handle restart and manual reload
                if event.key == pygame.K_r:
                    if self.game_over:
                        self.__init__()  # Restart game
                    elif not self.beaver.reloading and self.beaver.current_ammo < self.beaver.max_ammo:
                        self.beaver.reloading = True
                        self.beaver.reload_timer = pygame.time.get_ticks()
        return True