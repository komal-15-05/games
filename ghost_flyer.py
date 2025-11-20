import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (150, 0, 255)
DARK_BLUE = (20, 30, 80)
LIGHT_BLUE = (135, 206, 250)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Ghost properties
GHOST_SIZE = 40
GHOST_SPEED = 5
BASE_GRAVITY = 0.8
BASE_JUMP_STRENGTH = -12

# Level system
LEVELS = {
    1: {"name": "Peaceful Clouds", "gravity": 0.8, "jump": -12, "speed": 3, "gap": 220, "bg_color": (135, 206, 250)},
    2: {"name": "Windy Skies", "gravity": 0.9, "jump": -13, "speed": 4, "gap": 200, "bg_color": (100, 150, 255)},
    3: {"name": "Storm Clouds", "gravity": 1.0, "jump": -14, "speed": 5, "gap": 180, "bg_color": (70, 100, 200)},
    4: {"name": "Lightning Zone", "gravity": 1.1, "jump": -15, "speed": 6, "gap": 160, "bg_color": (50, 50, 150)},
    5: {"name": "Nightmare Realm", "gravity": 1.2, "jump": -16, "speed": 7, "gap": 140, "bg_color": (30, 20, 100)}
}

# Obstacle properties
OBSTACLE_WIDTH = 60

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-3, -1)
        self.life = 30
        self.max_life = 30
        self.color = color
        self.size = random.uniform(2, 5)
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # gravity
        self.life -= 1
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(s, (self.x - self.size, self.y - self.size))

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.size = GHOST_SIZE
        self.animation_time = 0
        self.trail_particles = []
        self.glow_radius = 0
        
    def update(self, gravity, jump_strength):
        # Apply gravity
        self.velocity_y += gravity
        self.y += self.velocity_y
        
        # Keep ghost on screen
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        if self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity_y = 0
        
        # Update animation
        self.animation_time += 0.2
        
        # Update glow effect
        self.glow_radius = 5 + 3 * math.sin(self.animation_time)
        
        # Add trail particles
        if random.random() < 0.3:
            self.trail_particles.append(Particle(
                self.x + self.size//2 + random.uniform(-5, 5),
                self.y + self.size//2 + random.uniform(-5, 5),
                (200, 200, 255)
            ))
        
        # Update particles
        for particle in self.trail_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.trail_particles.remove(particle)
    
    def jump(self, jump_strength):
        self.velocity_y = jump_strength
        # Add jump particles
        for _ in range(8):
            self.trail_particles.append(Particle(
                self.x + self.size//2 + random.uniform(-10, 10),
                self.y + self.size + random.uniform(-5, 5),
                (255, 255, 255)
            ))
    
    def draw(self, screen):
        # Draw trail particles
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Draw glow effect
        glow_surface = pygame.Surface((self.size + self.glow_radius * 2, self.size + self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (100, 100, 255, 30), 
                          (self.size//2 + self.glow_radius, self.size//2 + self.glow_radius), 
                          self.size//2 + self.glow_radius)
        screen.blit(glow_surface, (self.x - self.glow_radius, self.y - self.glow_radius))
        
        # Draw ghost body with gradient effect
        center_x = int(self.x + self.size//2)
        center_y = int(self.y + self.size//2)
        
        # Main body
        pygame.draw.circle(screen, WHITE, (center_x, center_y), self.size//2)
        pygame.draw.circle(screen, (240, 240, 255), (center_x - 3, center_y - 3), self.size//2 - 5)
        
        # Animated wavy tail
        tail_wave = math.sin(self.animation_time) * 3
        tail_points = [
            (self.x, self.y + self.size),
            (self.x + self.size//4, self.y + self.size - 10 + tail_wave),
            (self.x + self.size//2, self.y + self.size + tail_wave),
            (self.x + 3*self.size//4, self.y + self.size - 10 - tail_wave),
            (self.x + self.size, self.y + self.size)
        ]
        pygame.draw.polygon(screen, WHITE, tail_points)
        
        # Animated eyes
        eye_size = 6
        eye_offset = math.sin(self.animation_time * 2) * 1
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size//3), int(self.y + self.size//3 + eye_offset)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x + 2*self.size//3), int(self.y + self.size//3 + eye_offset)), eye_size)
        
        # Eye shine
        pygame.draw.circle(screen, WHITE, (int(self.x + self.size//3 + 2), int(self.y + self.size//3 - 2 + eye_offset)), 2)
        pygame.draw.circle(screen, WHITE, (int(self.x + 2*self.size//3 + 2), int(self.y + self.size//3 - 2 + eye_offset)), 2)

class Obstacle:
    def __init__(self, x, gap_size, level):
        self.x = x
        self.gap_y = random.randint(100, SCREEN_HEIGHT - gap_size - 100)
        self.gap_size = gap_size
        self.width = OBSTACLE_WIDTH
        self.passed = False
        self.level = level
        self.animation_time = 0
        
    def update(self, speed):
        self.x -= speed
        self.animation_time += 0.1
        
    def draw(self, screen):
        # Enhanced obstacle graphics based on level
        if self.level <= 2:
            # Peaceful/Windy - Green pipes with highlights
            top_color = (0, 200, 0)
            bottom_color = (0, 150, 0)
            highlight_color = (100, 255, 100)
        elif self.level <= 3:
            # Storm - Darker with lightning effect
            flash = abs(math.sin(self.animation_time * 3)) * 50
            top_color = (50 + flash, 50 + flash, 150 + flash)
            bottom_color = (30 + flash, 30 + flash, 100 + flash)
            highlight_color = (100 + flash, 100 + flash, 200 + flash)
        else:
            # Nightmare - Dark purple/red with pulsing
            pulse = abs(math.sin(self.animation_time * 2)) * 30
            top_color = (100 + pulse, 0, 50 + pulse)
            bottom_color = (80 + pulse, 0, 30 + pulse)
            highlight_color = (150 + pulse, 50, 100 + pulse)
        
        # Top obstacle with gradient
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        pygame.draw.rect(screen, top_color, top_rect)
        pygame.draw.rect(screen, bottom_color, (self.x + 5, 0, self.width - 10, self.gap_y))
        pygame.draw.rect(screen, highlight_color, (self.x, 0, 8, self.gap_y))
        
        # Bottom obstacle with gradient
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, SCREEN_HEIGHT - self.gap_y - self.gap_size)
        pygame.draw.rect(screen, top_color, bottom_rect)
        pygame.draw.rect(screen, bottom_color, (self.x + 5, self.gap_y + self.gap_size, self.width - 10, SCREEN_HEIGHT - self.gap_y - self.gap_size))
        pygame.draw.rect(screen, highlight_color, (self.x, self.gap_y + self.gap_size, 8, SCREEN_HEIGHT - self.gap_y - self.gap_size))
        
        # Add caps
        cap_height = 20
        pygame.draw.rect(screen, highlight_color, (self.x - 5, self.gap_y - cap_height, self.width + 10, cap_height))
        pygame.draw.rect(screen, highlight_color, (self.x - 5, self.gap_y + self.gap_size, self.width + 10, cap_height))
        
    def collides_with(self, ghost):
        # Check collision with ghost
        if (ghost.x < self.x + self.width and 
            ghost.x + ghost.size > self.x):
            if (ghost.y < self.gap_y or 
                ghost.y + ghost.size > self.gap_y + self.gap_size):
                return True
        return False

def draw_gradient_background(screen, color1, color2):
    """Draw a vertical gradient background"""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def main():
    print("Starting Ghost Flyer game...")
    print("Game window should open now!")
    print("Controls: SPACE to fly, R to restart after game over")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ghost Flyer - Kiro Style!")
    clock = pygame.time.Clock()
    
    # Create ghost
    ghost = Ghost(100, SCREEN_HEIGHT // 2)
    
    # Game variables
    obstacles = []
    score = 0
    current_level = 1
    game_over = False
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    big_font = pygame.font.Font(None, 48)
    
    # Level transition
    level_transition = False
    transition_timer = 0
    show_level_name = False
    level_name_timer = 0
    
    def get_current_level_data():
        return LEVELS.get(current_level, LEVELS[5])  # Default to max level
    
    def reset_game():
        nonlocal ghost, obstacles, score, current_level, game_over, level_transition, transition_timer
        ghost = Ghost(100, SCREEN_HEIGHT // 2)
        obstacles = []
        score = 0
        current_level = 1
        game_over = False
        level_transition = False
        transition_timer = 0
        # Create initial obstacles
        level_data = get_current_level_data()
        for i in range(3):
            obstacles.append(Obstacle(SCREEN_WIDTH + i * 300, level_data["gap"], current_level))
    
    # Initialize game
    reset_game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not level_transition:
                    level_data = get_current_level_data()
                    ghost.jump(level_data["jump"])
                elif event.key == pygame.K_r and game_over:
                    reset_game()
        
        level_data = get_current_level_data()
        
        if not game_over and not level_transition:
            # Update ghost
            ghost.update(level_data["gravity"], level_data["jump"])
            
            # Check for level progression
            if score > 0 and score % 10 == 0 and score // 10 + 1 > current_level:
                if current_level < 5:  # Max level
                    current_level += 1
                    level_transition = True
                    transition_timer = 120  # 2 seconds at 60 FPS
                    show_level_name = True
                    level_name_timer = 180  # 3 seconds
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update(level_data["speed"])
                
                # Check collision
                if obstacle.collides_with(ghost):
                    game_over = True
                
                # Check if obstacle passed
                if not obstacle.passed and obstacle.x + obstacle.width < ghost.x:
                    obstacle.passed = True
                    score += 1
                
                # Remove obstacles that are off screen
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
            
            # Add new obstacles
            if len(obstacles) < 3:
                last_obstacle = obstacles[-1] if obstacles else None
                if last_obstacle is None or last_obstacle.x < SCREEN_WIDTH - 300:
                    obstacles.append(Obstacle(SCREEN_WIDTH, level_data["gap"], current_level))
        
        # Handle level transition
        if level_transition:
            transition_timer -= 1
            if transition_timer <= 0:
                level_transition = False
                # Clear old obstacles and create new ones for the new level
                obstacles = []
                for i in range(3):
                    obstacles.append(Obstacle(SCREEN_WIDTH + i * 300, level_data["gap"], current_level))
        
        if show_level_name:
            level_name_timer -= 1
            if level_name_timer <= 0:
                show_level_name = False
        
        # Draw everything
        # Dynamic background based on level
        bg_color = level_data["bg_color"]
        darker_bg = tuple(max(0, c - 50) for c in bg_color)
        draw_gradient_background(screen, bg_color, darker_bg)
        
        # Draw ghost
        ghost.draw(screen)
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        level_text = small_font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(level_text, (10, 50))
        
        # Draw level name
        if show_level_name:
            level_name = level_data["name"]
            name_text = big_font.render(level_name, True, GOLD)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH//2, 100))
            # Add shadow
            shadow_text = big_font.render(level_name, True, BLACK)
            screen.blit(shadow_text, (name_rect.x + 2, name_rect.y + 2))
            screen.blit(name_text, name_rect)
        
        # Draw level transition effect
        if level_transition:
            alpha = int(255 * (transition_timer / 120))
            transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            transition_surface.set_alpha(alpha)
            transition_surface.fill(WHITE)
            screen.blit(transition_surface, (0, 0))
            
            if transition_timer > 60:
                level_up_text = big_font.render("LEVEL UP!", True, GOLD)
                text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(level_up_text, text_rect)
        
        # Draw game over screen
        if game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(game_over_text, text_rect)
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(final_score_text, score_rect)
            
            restart_text = small_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
        
        # Draw instructions
        if not game_over and not level_transition:
            instruction_text = small_font.render("Press SPACE to fly!", True, WHITE)
            screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()