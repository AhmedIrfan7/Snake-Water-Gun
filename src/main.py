import pygame
import random
import sys
import os
import time
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
PURPLE = (147, 112, 219)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)

# Game options
choices = {1: "Snake", -1: "Water", 0: "Gun"}
youDict = {"s": 1, "w": -1, "g": 0}

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Water Gun Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load sprites
        self.load_sprites()
        
        # Game state
        self.player_choice = None
        self.computer_choice = None
        self.game_result = None
        self.show_result = False
        self.show_loading = False
        self.loading_start_time = 0
        self.animation_time = 0
        
        # Button areas for clicking (invisible hitboxes) - Fixed positioning
        button_width, button_height = 120, 120
        center_y = HEIGHT // 2 + 50
        
        # Align buttons with the actual icon positions
        self.snake_button = pygame.Rect(WIDTH // 2 - 140 - button_width//2, center_y - button_height//2, button_width, button_height)
        self.water_button = pygame.Rect(WIDTH // 2 - button_width//2, center_y - button_height//2, button_width, button_height)
        self.gun_button = pygame.Rect(WIDTH // 2 + 140 - button_width//2, center_y - button_height//2, button_width, button_height)

    def load_sprites(self):
        """Load sprite images from assets folder"""
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        
        # Load and scale sprites
        sprite_size = (100, 100)
        
        self.snake_sprite = pygame.image.load(os.path.join(assets_path, 'SnakeSprite.png'))
        self.snake_sprite = pygame.transform.scale(self.snake_sprite, sprite_size)
        
        self.water_sprite = pygame.image.load(os.path.join(assets_path, 'WaterSprite.png'))
        self.water_sprite = pygame.transform.scale(self.water_sprite, sprite_size)
        
        self.gun_sprite = pygame.image.load(os.path.join(assets_path, 'GunSprite.png'))
        self.gun_sprite = pygame.transform.scale(self.gun_sprite, sprite_size)

    def draw_gradient_background(self, color1, color2):
        """Draw a gradient background"""
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

    def draw_text(self, text, size, color, x, y, center=False, shadow=False):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        
        if shadow:
            # Draw shadow
            shadow_surface = font.render(text, True, BLACK)
            shadow_rect = shadow_surface.get_rect()
            if center:
                shadow_rect.center = (x + 2, y + 2)
            else:
                shadow_rect.topleft = (x + 2, y + 2)
            self.screen.blit(shadow_surface, shadow_rect)
        
        if center:
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))

    def draw_choice_icon(self, sprite, x, y, hover=False):
        """Draw a choice icon with effects"""
        # Calculate animation offset
        if hover:
            offset = math.sin(self.animation_time * 8) * 3
        else:
            offset = 0
        
        # Draw glow effect if hovered
        if hover:
            glow_size = 120
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*LIGHT_BLUE, 100), (glow_size//2, glow_size//2), glow_size//2)
            glow_rect = glow_surface.get_rect()
            glow_rect.center = (x, y + offset)
            self.screen.blit(glow_surface, glow_rect)
        
        # Draw sprite
        sprite_rect = sprite.get_rect()
        sprite_rect.center = (x, y + offset)
        self.screen.blit(sprite, sprite_rect)

    def draw_result_icon(self, sprite, x, y, color):
        """Draw an icon for the result screen with minimal design"""
        # Simple background circle
        circle_size = 100
        pygame.draw.circle(self.screen, color, (x, y), circle_size//2)
        
        # Draw sprite
        sprite_rect = sprite.get_rect()
        sprite_rect.center = (x, y)
        self.screen.blit(sprite, sprite_rect)

    def draw_game_interface(self):
        """Draw the main game interface"""
        # Gradient background
        self.draw_gradient_background((240, 248, 255), (230, 240, 250))
        
        # Title with minimal shadows
        self.draw_text("Snake Water Gun", 64, PURPLE, WIDTH // 2, 80, center=True, shadow=True)
        self.draw_text("Choose Your Weapon!", 32, DARK_BLUE, WIDTH // 2, 130, center=True, shadow=False)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw choice icons with effects
        self.draw_choice_icon(self.snake_sprite, WIDTH // 2 - 140, HEIGHT // 2 + 50, 
                            self.snake_button.collidepoint(mouse_pos))
        self.draw_choice_icon(self.water_sprite, WIDTH // 2, HEIGHT // 2 + 50, 
                            self.water_button.collidepoint(mouse_pos))
        self.draw_choice_icon(self.gun_sprite, WIDTH // 2 + 140, HEIGHT // 2 + 50, 
                            self.gun_button.collidepoint(mouse_pos))
        
        # Labels below icons - no shadows for cleaner look
        self.draw_text("Snake", 28, GREEN, WIDTH // 2 - 140, HEIGHT // 2 + 120, center=True, shadow=False)
        self.draw_text("Water", 28, DARK_BLUE, WIDTH // 2, HEIGHT // 2 + 120, center=True, shadow=False)
        self.draw_text("Gun", 28, RED, WIDTH // 2 + 140, HEIGHT // 2 + 120, center=True, shadow=False)
        
        # Instructions - no shadow
        self.draw_text("Click on any icon to play!", 24, GRAY, WIDTH // 2, HEIGHT - 80, center=True, shadow=False)

    def draw_loading_screen(self):
        """Draw loading screen while computer is thinking"""
        # Animated gradient background
        time_offset = self.animation_time * 0.5
        color1 = (int(240 + math.sin(time_offset) * 20), 248, 255)
        color2 = (int(230 + math.cos(time_offset) * 20), 240, 250)
        self.draw_gradient_background(color1, color2)
        
        # Title - minimal shadow
        self.draw_text("Computer is thinking...", 48, PURPLE, WIDTH // 2, 150, center=True, shadow=True)
        
        # Loading animation with rotating dots - no shadow
        elapsed_time = time.time() - self.loading_start_time
        dot_count = int(elapsed_time * 3) % 4
        dots = "." * dot_count
        self.draw_text(f"Please wait{dots}", 32, DARK_BLUE, WIDTH // 2, 220, center=True, shadow=False)
        
        # Show player's choice with glow effect - no shadow
        self.draw_text("Your Choice:", 32, BLACK, WIDTH // 2, 300, center=True, shadow=False)
        
        choice_sprite = None
        choice_text = ""
        choice_color = BLACK
        
        if self.player_choice == 1:
            choice_sprite = self.snake_sprite
            choice_text = "Snake"
            choice_color = GREEN
        elif self.player_choice == -1:
            choice_sprite = self.water_sprite
            choice_text = "Water"
            choice_color = DARK_BLUE
        elif self.player_choice == 0:
            choice_sprite = self.gun_sprite
            choice_text = "Gun"
            choice_color = RED
        
        if choice_sprite:
            # Glow effect
            glow_size = 120
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*choice_color, 80), (glow_size//2, glow_size//2), glow_size//2)
            glow_rect = glow_surface.get_rect()
            glow_rect.center = (WIDTH // 2, 380)
            self.screen.blit(glow_surface, glow_rect)
            
            # Sprite
            sprite_rect = choice_sprite.get_rect()
            sprite_rect.center = (WIDTH // 2, 380)
            self.screen.blit(choice_sprite, sprite_rect)
            
            self.draw_text(choice_text, 28, choice_color, WIDTH // 2, 450, center=True, shadow=False)

    def draw_result_screen(self):
        """Draw the result screen with minimal, clean design"""
        # Simple gradient background
        if self.game_result == "win":
            self.draw_gradient_background((240, 255, 240), (220, 255, 220))
        elif self.game_result == "lose":
            self.draw_gradient_background((255, 240, 240), (255, 220, 220))
        else:
            self.draw_gradient_background((245, 245, 245), (235, 235, 235))
        
        # Result title - minimal shadow
        if self.game_result == "win":
            self.draw_text("You Win!", 48, GREEN, WIDTH // 2, 100, center=True, shadow=True)
        elif self.game_result == "lose":
            self.draw_text("You Lose!", 48, RED, WIDTH // 2, 100, center=True, shadow=True)
        else:
            self.draw_text("It's a Draw!", 48, GRAY, WIDTH // 2, 100, center=True, shadow=True)
        
        # Choices display
        center_y = HEIGHT // 2
        
        # Player choice (left) - no shadows
        player_x = WIDTH // 3
        self.draw_text("You", 24, BLACK, player_x, center_y - 80, center=True, shadow=False)
        
        player_color = GREEN if self.game_result == "win" else (150, 150, 150)
        if self.player_choice == 1:
            self.draw_result_icon(self.snake_sprite, player_x, center_y - 20, player_color)
            self.draw_text("Snake", 20, GREEN, player_x, center_y + 60, center=True, shadow=False)
        elif self.player_choice == -1:
            self.draw_result_icon(self.water_sprite, player_x, center_y - 20, player_color)
            self.draw_text("Water", 20, DARK_BLUE, player_x, center_y + 60, center=True, shadow=False)
        elif self.player_choice == 0:
            self.draw_result_icon(self.gun_sprite, player_x, center_y - 20, player_color)
            self.draw_text("Gun", 20, RED, player_x, center_y + 60, center=True, shadow=False)
        
        # VS - no shadow
        self.draw_text("vs", 32, GRAY, WIDTH // 2, center_y - 20, center=True, shadow=False)
        
        # Computer choice (right) - no shadows
        computer_x = 2 * WIDTH // 3
        self.draw_text("Computer", 24, BLACK, computer_x, center_y - 80, center=True, shadow=False)
        
        computer_color = RED if self.game_result == "lose" else (150, 150, 150)
        if self.computer_choice == 1:
            self.draw_result_icon(self.snake_sprite, computer_x, center_y - 20, computer_color)
            self.draw_text("Snake", 20, GREEN, computer_x, center_y + 60, center=True, shadow=False)
        elif self.computer_choice == -1:
            self.draw_result_icon(self.water_sprite, computer_x, center_y - 20, computer_color)
            self.draw_text("Water", 20, DARK_BLUE, computer_x, center_y + 60, center=True, shadow=False)
        elif self.computer_choice == 0:
            self.draw_result_icon(self.gun_sprite, computer_x, center_y - 20, computer_color)
            self.draw_text("Gun", 20, RED, computer_x, center_y + 60, center=True, shadow=False)
        
        # Simple instruction - no shadows
        self.draw_text("Click anywhere to play again", 20, GRAY, WIDTH // 2, HEIGHT - 80, center=True, shadow=False)
        self.draw_text("Press ESC to quit", 16, GRAY, WIDTH // 2, HEIGHT - 50, center=True, shadow=False)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.show_result:
                        # Reset game state
                        self.player_choice = None
                        self.computer_choice = None
                        self.game_result = None
                        self.show_result = False
                        self.show_loading = False
                    elif not self.show_loading:
                        # Check which button was clicked
                        if self.snake_button.collidepoint(event.pos):
                            return 1  # Snake
                        elif self.water_button.collidepoint(event.pos):
                            return -1  # Water
                        elif self.gun_button.collidepoint(event.pos):
                            return 0  # Gun
        return None

    def run(self):
        while self.running:
            self.animation_time += 0.1
            
            self.screen.fill(WHITE)
            
            if self.show_loading:
                # Loading screen
                self.draw_loading_screen()
                
                # Check if loading time is complete (2 seconds)
                if time.time() - self.loading_start_time >= 2:
                    self.show_loading = False
                    self.show_result = True
                    
            elif self.show_result:
                # Result screen
                self.draw_result_screen()
                self.handle_input()
            else:
                # Main game interface
                self.draw_game_interface()
                
                # Handle player input
                you = self.handle_input()
                
                if you is not None:
                    self.player_choice = you
                    self.computer_choice = random.choice([-1, 0, 1])
                    
                    # Determine result
                    if self.computer_choice == you:
                        self.game_result = "draw"
                    elif (self.computer_choice == -1 and you == 1) or (self.computer_choice == 0 and you == -1) or (self.computer_choice == 1 and you == 0):
                        self.game_result = "win"
                    else:
                        self.game_result = "lose"
                    
                    # Start loading screen
                    self.show_loading = True
                    self.loading_start_time = time.time()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()