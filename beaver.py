import pygame
import math
import constants # Import constants module to access shared variables
from bullet import Bullet # Bullet class import

class Beaver:
    def __init__(self):
        self.width = 80
        self.height = 80
        self.x = 100  # Fixed x-position

        # Initial y-position: Ensure the beaver spawns above the absolute bottom line,
        # considering its height. constants.HEIGHT is the bottom of the screen.
        self.y = constants.HEIGHT - self.height # Spawn at the very bottom edge of the playable area
        
        self.hp = 30
        self.angle = 0  # Gun angle in degrees (0 = straight, -90 = up, 90 = down)
        self.speed = 5  # Running speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Ammo and Reloading attributes
        self.max_ammo = constants.MAX_AMMO
        self.current_ammo = self.max_ammo
        self.reloading = False
        self.reload_timer = 0 # This will store the time when reload started (in milliseconds)
        self.last_shot_time = 0  # Track last time a bullet was shot
        
        # Load ricochet sound
        self.ricochet_sound = pygame.mixer.Sound("shot.mp3")
        
        # Load beaver image
        self.image = pygame.image.load("bobar_1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
        # Load gun image
        self.gun_image = pygame.image.load("pushka.png").convert_alpha()
        self.gun_width = 80  # Increased gun width
        self.gun_height = 40  # Increased gun height
        self.gun_image = pygame.transform.scale(self.gun_image, (self.gun_width, self.gun_height))
        
        # Initialize gun_tip with a default, will be updated in draw
        self.gun_tip = (self.x + self.width, self.y + self.height // 2)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle = min(self.angle + 5, 90)
        if keys[pygame.K_DOWN]:
            self.angle = max(self.angle - 5, -90)
        if keys[pygame.K_w]:
            # Ensure beaver doesn't go above the calculated upper limit (BEAVER_MAX_Y_UPPER)
            # The top of the beaver (self.y) should not be less than BEAVER_MAX_Y_UPPER
            self.y = max(self.y - self.speed, constants.BEAVER_MAX_Y_UPPER)
        if keys[pygame.K_s]:
            # Ensure beaver doesn't go below the bottom line (ground level)
            # The bottom of the beaver (self.y + self.height) should not exceed constants.HEIGHT
            # So, self.y should not exceed (constants.HEIGHT - self.height)
            self.y = min(self.y + self.speed, constants.HEIGHT - self.height)
        # Update rect position after y movement
        self.rect.y = self.y

    def draw(self, screen):
        # Draw beaver using image instead of rectangle
        screen.blit(self.image, (self.x, self.y))
        # Draw gun (pushka.png) rotated by angle and positioned at the beaver's side
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2 - self.gun_height // 2
        
        rotated_gun = pygame.transform.rotate(self.gun_image, self.angle)
        
        rotated_rect = rotated_gun.get_rect(center=(gun_x, gun_y + self.gun_height // 2))
        
        screen.blit(rotated_gun, rotated_rect.topleft)
        
        self.gun_tip = self._calculate_gun_tip(gun_x, gun_y)

    def _calculate_gun_tip(self, gun_x, gun_y):
        pivot_x = gun_x 
        pivot_y = gun_y + self.gun_height // 2

        tip_offset_x = self.gun_width 
        tip_offset_y = 0 

        rad = math.radians(-self.angle)
        rotated_tip_x = pivot_x + tip_offset_x * math.cos(rad) - tip_offset_y * math.sin(rad)
        rotated_tip_y = pivot_y + tip_offset_x * math.sin(rad) + tip_offset_y * math.cos(rad)
        
        return (rotated_tip_x, rotated_tip_y)

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if self.current_ammo > 0 and not self.reloading and (current_time - self.last_shot_time >= constants.BULLET_DELAY):
            if hasattr(self, 'gun_tip'):
                bullet_x, bullet_y = self.gun_tip
            else:
                gun_length = 30
                gun_x = self.x + self.width
                gun_y = self.y + self.height // 2
                rad = math.radians(self.angle)
                bullet_x = gun_x + gun_length * math.cos(rad)
                bullet_y = gun_y - gun_length * math.sin(rad)
            self.current_ammo -= 1
            self.last_shot_time = current_time
            self.ricochet_sound.play()
            if self.current_ammo == 0:
                self.reloading = True
                self.reload_timer = pygame.time.get_ticks()
            return Bullet(bullet_x, bullet_y, self.angle)
        return None