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
        
        self.hp = 30 # Beaver's health points
        self.angle = 0  # Gun angle in degrees (0 = straight, -90 = up, 90 = down)
        self.speed = 5  # Running speed (vertical movement)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) # For collision detection

        # Ammo and Reloading attributes
        self.max_ammo = constants.MAX_AMMO # Maximum bullets before reload
        self.current_ammo = self.max_ammo # Current ammo
        self.reloading = False # Is the beaver currently reloading?
        self.reload_timer = 0 # Time when reload started (ms)
        self.last_shot_time = 0  # Last time a bullet was shot (ms)
        
        # Load ricochet sound for shooting
        self.ricochet_sound = pygame.mixer.Sound("shot.mp3")
        
        # Load beaver image and scale to fit
        self.image = pygame.image.load("bobar_1.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
        # Load gun image and scale to fit
        self.gun_image = pygame.image.load("pushka.png").convert_alpha()
        self.gun_width = 80  # Gun image width
        self.gun_height = 40  # Gun image height
        self.gun_image = pygame.transform.scale(self.gun_image, (self.gun_width, self.gun_height))
        
        # Initialize gun_tip with a default, will be updated in draw
        self.gun_tip = (self.x + self.width, self.y + self.height // 2)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle = min(self.angle + 5, 90) # Aim gun up
        if keys[pygame.K_DOWN]:
            self.angle = max(self.angle - 5, -90) # Aim gun down
        if keys[pygame.K_w]:
            # Move up, but don't go above the HUD (ammo text)
            self.y = max(self.y - self.speed, constants.BEAVER_MAX_Y_UPPER)
        if keys[pygame.K_s]:
            # Move down, but don't go below the bottom of the screen
            self.y = min(self.y + self.speed, constants.HEIGHT - self.height)
        # Update rect position after y movement for collision
        self.rect.y = self.y

    def draw(self, screen):
        # Draw beaver sprite
        screen.blit(self.image, (self.x, self.y))
        # Draw gun (pushka.png) rotated by angle and positioned at the beaver's side
        gun_x = self.x + self.width
        gun_y = self.y + self.height // 2 - self.gun_height // 2
        
        rotated_gun = pygame.transform.rotate(self.gun_image, self.angle)
        rotated_rect = rotated_gun.get_rect(center=(gun_x, gun_y + self.gun_height // 2))
        screen.blit(rotated_gun, rotated_rect.topleft)
        # Update gun_tip for bullet spawn
        self.gun_tip = self._calculate_gun_tip(gun_x, gun_y)

    def _calculate_gun_tip(self, gun_x, gun_y):
        # Calculate the tip of the gun barrel for bullet spawn, accounting for rotation
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
        # Only shoot if there's ammo, not reloading, and enough time has passed since last shot
        if self.current_ammo > 0 and not self.reloading and (current_time - self.last_shot_time >= constants.BULLET_DELAY):
            if hasattr(self, 'gun_tip'):
                bullet_x, bullet_y = self.gun_tip
            else:
                # Fallback if gun_tip not set yet
                gun_length = 30
                gun_x = self.x + self.width
                gun_y = self.y + self.height // 2
                rad = math.radians(self.angle)
                bullet_x = gun_x + gun_length * math.cos(rad)
                bullet_y = gun_y - gun_length * math.sin(rad)
            self.current_ammo -= 1 # Decrease ammo count
            self.last_shot_time = current_time # Update last shot time
            self.ricochet_sound.play() # Play shooting sound
            if self.current_ammo == 0:
                self.reloading = True
                self.reload_timer = pygame.time.get_ticks()
            return Bullet(bullet_x, bullet_y, self.angle)
        return None # Return None if unable to shoot