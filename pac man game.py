import pygame
import random
import sys
from enum import Enum

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Constants
SCREEN_WIDTH = 448
SCREEN_HEIGHT = 576
TILE_SIZE = 16
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 183, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
PELLET_COLOR = (255, 255, 255)

# Game states
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    LEVEL_COMPLETE = 2

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

# Ghost modes
class GhostMode(Enum):
    CHASE = 0
    SCATTER = 1
    FRIGHTENED = 2

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Original Pac-Man maze layout (28x36 tiles, but we'll use 28x31 for visible area)
# 0 = empty, 1 = wall, 2 = dot, 3 = power pellet, 4 = ghost house
maze_layout = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,4,4,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,0,2,0,0,0,1,4,4,4,4,4,4,1,0,0,0,2,0,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,3,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

class Player:
    def __init__(self):
        self.reset()
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        
    def reset(self):
        self.x = 14
        self.y = 23
        self.direction = Direction.LEFT
        self.next_direction = Direction.LEFT
        self.speed = 1
        self.score = 0
        self.lives = 3
        self.power_timer = 0
        self.is_powered = False
        
    def move(self, maze):
        # Check if next direction is valid
        new_x = self.x + self.next_direction.value[0]
        new_y = self.y + self.next_direction.value[1]
        
        if self.can_move(new_x, new_y, maze):
            self.direction = self.next_direction
        
        # Move in current direction
        new_x = self.x + self.direction.value[0]
        new_y = self.y + self.direction.value[1]
        
        if self.can_move(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
            
            # Wrap around tunnel
            if self.x < 0:
                self.x = 27
            elif self.x > 27:
                self.x = 0
                
            # Collect dot or power pellet
            tile_x, tile_y = int(self.x), int(self.y)
            if 0 <= tile_y < len(maze_layout) and 0 <= tile_x < len(maze_layout[0]):
                if maze_layout[tile_y][tile_x] == 2:  # Dot
                    maze_layout[tile_y][tile_x] = 0
                    self.score += 10
                elif maze_layout[tile_y][tile_x] == 3:  # Power pellet
                    maze_layout[tile_y][tile_x] = 0
                    self.score += 50
                    self.is_powered = True
                    self.power_timer = 300  # 5 seconds at 60 FPS
        
        # Update power timer
        if self.is_powered:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.is_powered = False
                
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def can_move(self, x, y, maze):
        # Check if position is valid in the maze
        tile_x, tile_y = int(x), int(y)
        
        # Allow tunnel wrap-around
        if tile_x < 0 or tile_x >= len(maze_layout[0]):
            return True
            
        if tile_y < 0 or tile_y >= len(maze_layout):
            return False
            
        # Check if the tile is a wall
        return maze_layout[tile_y][tile_x] != 1
    
    def draw(self):
        # Draw Pac-Man
        center_x = self.x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.y * TILE_SIZE + TILE_SIZE // 2
        
        # Draw Pac-Man body
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), TILE_SIZE // 2)
        
        # Draw Pac-Man mouth based on direction and animation frame
        mouth_angle = 45 - (self.animation_frame * 10)  # Animation makes mouth open and close
        
        if self.direction == Direction.RIGHT:
            start_angle = mouth_angle
            end_angle = 360 - mouth_angle
        elif self.direction == Direction.LEFT:
            start_angle = 180 + mouth_angle
            end_angle = 180 - mouth_angle
        elif self.direction == Direction.UP:
            start_angle = 270 + mouth_angle
            end_angle = 270 - mouth_angle
        elif self.direction == Direction.DOWN:
            start_angle = 90 + mouth_angle
            end_angle = 90 - mouth_angle
        else:
            start_angle = 45
            end_angle = 315
            
        # Draw mouth as a pie wedge
        pygame.draw.polygon(screen, BLACK, [
            (center_x, center_y),
            (center_x + TILE_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(start_angle).x,
             center_y + TILE_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(start_angle).y),
            (center_x + TILE_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(end_angle).x,
             center_y + TILE_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(end_angle).y)
        ])

class Ghost:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.direction = Direction.LEFT
        self.speed = 0.8
        self.mode = GhostMode.SCATTER
        self.mode_timer = 0
        self.frightened_timer = 0
        self.is_frightened = False
        self.is_eaten = False
        self.target_x = 0
        self.target_y = 0
        self.scatter_targets = {
            "blinky": (25, 0),
            "pinky": (2, 0),
            "inky": (27, 35),
            "clyde": (0, 35)
        }
        self.reset()
        
    def reset(self):
        self.x = 14
        self.y = 14
        self.direction = Direction.LEFT
        self.mode = GhostMode.SCATTER
        self.mode_timer = 0
        self.is_frightened = False
        self.is_eaten = False
        
    def move(self, maze, player, blinky=None):
        if self.is_eaten:
            # Return to ghost house when eaten
            if self.x == 14 and self.y == 14:
                self.is_eaten = False
                self.is_frightened = False
            else:
                self.target_x = 14
                self.target_y = 14
        elif self.is_frightened:
            # Random movement when frightened
            self.target_x = random.randint(0, 27)
            self.target_y = random.randint(0, 35)
        else:
            # Set target based on mode and ghost personality
            if self.mode == GhostMode.SCATTER:
                self.target_x, self.target_y = self.scatter_targets[self.name]
            else:  # CHASE mode
                if self.name == "blinky":
                    # Red - directly targets Pac-Man
                    self.target_x = player.x
                    self.target_y = player.y
                elif self.name == "pinky":
                    # Pink - targets 4 tiles ahead of Pac-Man
                    ahead_x = player.x + player.direction.value[0] * 4
                    ahead_y = player.y + player.direction.value[1] * 4
                    self.target_x = ahead_x
                    self.target_y = ahead_y
                elif self.name == "inky":
                    # Cyan - uses a complex targeting system
                    if blinky:
                        # Target is vector from Blinky to 2 tiles ahead of Pac-Man, then doubled
                        ahead_x = player.x + player.direction.value[0] * 2
                        ahead_y = player.y + player.direction.value[1] * 2
                        self.target_x = ahead_x + (ahead_x - blinky.x)
                        self.target_y = ahead_y + (ahead_y - blinky.y)
                    else:
                        self.target_x = player.x
                        self.target_y = player.y
                elif self.name == "clyde":
                    # Orange - targets Pac-Man when far, scatter target when close
                    dist_to_player = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
                    if dist_to_player > 8:
                        self.target_x = player.x
                        self.target_y = player.y
                    else:
                        self.target_x, self.target_y = self.scatter_targets[self.name]
        
        # Choose direction based on target
        self.choose_direction(maze)
        
        # Move in chosen direction
        new_x = self.x + self.direction.value[0] * self.speed
        new_y = self.y + self.direction.value[1] * self.speed
        
        if self.can_move(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
            
            # Wrap around tunnel
            if self.x < 0:
                self.x = 27
            elif self.x > 27:
                self.x = 0
        
        # Update mode timer
        self.mode_timer += 1
        if self.mode_timer >= 700:  # Switch mode every ~12 seconds
            self.mode_timer = 0
            if self.mode == GhostMode.CHASE:
                self.mode = GhostMode.SCATTER
            else:
                self.mode = GhostMode.CHASE
                
        # Update frightened timer
        if self.is_frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.is_frightened = False
    
    def choose_direction(self, maze):
        # Get possible directions (not including opposite of current direction)
        directions = [d for d in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT] 
                     if d.value != (-self.direction.value[0], -self.direction.value[1])]
        
        # Filter valid directions
        valid_directions = []
        for direction in directions:
            new_x = self.x + direction.value[0]
            new_y = self.y + direction.value[1]
            if self.can_move(new_x, new_y, maze):
                valid_directions.append(direction)
        
        # If no valid directions, allow opposite direction
        if not valid_directions:
            opposite = Direction((-self.direction.value[0], -self.direction.value[1]))
            new_x = self.x + opposite.value[0]
            new_y = self.y + opposite.value[1]
            if self.can_move(new_x, new_y, maze):
                self.direction = opposite
            return
        
        # Choose direction that minimizes distance to target
        best_direction = valid_directions[0]
        min_distance = float('inf')
        
        for direction in valid_directions:
            new_x = self.x + direction.value[0]
            new_y = self.y + direction.value[1]
            distance = ((new_x - self.target_x) ** 2 + (new_y - self.target_y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
        
        self.direction = best_direction
    
    def can_move(self, x, y, maze):
        # Check if position is valid in the maze
        tile_x, tile_y = int(x), int(y)
        
        # Allow tunnel wrap-around
        if tile_x < 0 or tile_x >= len(maze_layout[0]):
            return True
            
        if tile_y < 0 or tile_y >= len(maze_layout):
            return False
            
        # Check if the tile is a wall
        return maze_layout[tile_y][tile_x] != 1
    
    def draw(self):
        # Draw ghost
        center_x = self.x * TILE_SIZE + TILE_SIZE // 2
        center_y = self.y * TILE_SIZE + TILE_SIZE // 2
        
        if self.is_eaten:
            # Draw only eyes when eaten
            self.draw_eyes(center_x, center_y)
        elif self.is_frightened:
            # Draw blue ghost when frightened
            color = (0, 0, 255) if self.frightened_timer > 100 or self.frightened_timer % 10 < 5 else (255, 255, 255)
            self.draw_ghost_body(center_x, center_y, color)
            self.draw_eyes(center_x, center_y)
        else:
            # Draw normal ghost
            self.draw_ghost_body(center_x, center_y, self.color)
            self.draw_eyes(center_x, center_y)
    
    def draw_ghost_body(self, center_x, center_y, color):
        # Draw ghost body (semi-circle with wavy bottom)
        pygame.draw.circle(screen, color, (center_x, center_y - TILE_SIZE // 4), TILE_SIZE // 2)
        pygame.draw.rect(screen, color, (center_x - TILE_SIZE // 2, center_y - TILE_SIZE // 4, TILE_SIZE, TILE_SIZE // 2))
        
        # Draw wavy bottom
        for i in range(3):
            pygame.draw.rect(screen, color, 
                            (center_x - TILE_SIZE // 2 + i * TILE_SIZE // 3, 
                             center_y + TILE_SIZE // 4, 
                             TILE_SIZE // 3, TILE_SIZE // 4))
    
    def draw_eyes(self, center_x, center_y):
        # Draw ghost eyes
        eye_offset_x = TILE_SIZE // 4
        eye_offset_y = -TILE_SIZE // 8
        
        # Determine eye direction based on ghost direction
        pupil_offset_x, pupil_offset_y = 0, 0
        if self.direction == Direction.LEFT:
            pupil_offset_x = -2
        elif self.direction == Direction.RIGHT:
            pupil_offset_x = 2
        elif self.direction == Direction.UP:
            pupil_offset_y = -2
        elif self.direction == Direction.DOWN:
            pupil_offset_y = 2
        
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (center_x - eye_offset_x, center_y + eye_offset_y), TILE_SIZE // 6)
        pygame.draw.circle(screen, WHITE, (center_x + eye_offset_x, center_y + eye_offset_y), TILE_SIZE // 6)
        pygame.draw.circle(screen, BLACK, 
                          (center_x - eye_offset_x + pupil_offset_x, center_y + eye_offset_y + pupil_offset_y), 
                          TILE_SIZE // 12)
        pygame.draw.circle(screen, BLACK, 
                          (center_x + eye_offset_x + pupil_offset_x, center_y + eye_offset_y + pupil_offset_y), 
                          TILE_SIZE // 12)

def draw_maze():
    for y in range(len(maze_layout)):
        for x in range(len(maze_layout[0])):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            if maze_layout[y][x] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, rect)
                # Add inner border to walls for better visual
                pygame.draw.rect(screen, (0, 0, 150), rect, 1)
            elif maze_layout[y][x] == 2:  # Dot
                pygame.draw.circle(screen, PELLET_COLOR, 
                                  (x * TILE_SIZE + TILE_SIZE // 2, 
                                   y * TILE_SIZE + TILE_SIZE // 2), 
                                  TILE_SIZE // 8)
            elif maze_layout[y][x] == 3:  # Power pellet
                pygame.draw.circle(screen, PELLET_COLOR, 
                                  (x * TILE_SIZE + TILE_SIZE // 2, 
                                   y * TILE_SIZE + TILE_SIZE // 2), 
                                  TILE_SIZE // 3)

def check_collision(player, ghosts):
    for ghost in ghosts:
        # Simple collision detection based on proximity
        if (abs(player.x - ghost.x) < 0.8 and abs(player.y - ghost.y) < 0.8):
            if ghost.is_frightened:
                # Player eats ghost
                ghost.is_eaten = True
                ghost.is_frightened = False
                return 200  # Score for eating ghost
            elif not ghost.is_eaten:
                # Ghost catches player
                return -1  # Signal player death
    return 0  # No collision

def check_win():
    # Check if all dots and power pellets are collected
    for row in maze_layout:
        if 2 in row or 3 in row:  # If there are still dots or power pellets
            return False
    return True

def reset_maze():
    # Reset the maze to its original state
    global maze_layout
    maze_layout = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
        [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
        [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
        [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
        [0,0,0,0,0,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,0,0,0,0,0],
        [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
        [0,0,0,0,0,1,2,1,1,0,1,1,1,4,4,1,1,1,0,1,1,2,1,0,0,0,0,0],
        [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
        [0,0,0,0,0,0,2,0,0,0,1,4,4,4,4,4,4,1,0,0,0,2,0,0,0,0,0,0],
        [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
        [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
        [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
        [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
        [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
        [1,3,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,3,1],
        [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
        [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
        [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
        [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
        [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]

def main():
    player = Player()
    
    # Create ghosts with their original colors and names
    ghosts = [
        Ghost(14, 11, RED, "blinky"),
        Ghost(14, 14, PINK, "pinky"),
        Ghost(12, 14, CYAN, "inky"),
        Ghost(16, 14, ORANGE, "clyde")
    ]
    
    blinky = ghosts[0]  # Reference for Inky's targeting
    
    game_state = GameState.PLAYING
    level = 1
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    player.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT:
                    player.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    player.next_direction = Direction.RIGHT
                elif event.key == pygame.K_r and game_state != GameState.PLAYING:
                    # Restart game
                    player.reset()
                    for ghost in ghosts:
                        ghost.reset()
                    reset_maze()
                    game_state = GameState.PLAYING
                    level = 1
        
        if game_state == GameState.PLAYING:
            # Update game state
            player.move(maze_layout)
            
            # Activate power mode if player eats a power pellet
            if player.is_powered:
                for ghost in ghosts:
                    if not ghost.is_eaten:
                        ghost.is_frightened = True
                        ghost.frightened_timer = player.power_timer
            
            for ghost in ghosts:
                ghost.move(maze_layout, player, blinky)
            
            # Check for collisions
            collision_result = check_collision(player, ghosts)
            if collision_result == -1:  # Player caught by ghost
                player.lives -= 1
                if player.lives <= 0:
                    game_state = GameState.GAME_OVER
                else:
                    # Reset player and ghost positions
                    player.x = 14
                    player.y = 23
                    player.direction = Direction.LEFT
                    player.next_direction = Direction.LEFT
                    for ghost in ghosts:
                        ghost.reset()
            elif collision_result > 0:  # Player ate a ghost
                player.score += collision_result
            
            # Check for win
            if check_win():
                game_state = GameState.LEVEL_COMPLETE
                level += 1
        
        # Draw everything
        screen.fill(BLACK)
        draw_maze()
        player.draw()
        
        for ghost in ghosts:
            ghost.draw()
        
        # Draw score and lives
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(f"SCORE: {player.score}", True, WHITE)
        lives_text = font.render(f"LIVES: {player.lives}", True, WHITE)
        level_text = font.render(f"LEVEL: {level}", True, WHITE)
        screen.blit(score_text, (10, SCREEN_HEIGHT - 30))
        screen.blit(lives_text, (150, SCREEN_HEIGHT - 30))
        screen.blit(level_text, (280, SCREEN_HEIGHT - 30))
        
        # Draw game over or level complete message
        if game_state == GameState.GAME_OVER:
            game_over_font = pygame.font.SysFont(None, 48)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20))
        
        elif game_state == GameState.LEVEL_COMPLETE:
            level_font = pygame.font.SysFont(None, 48)
            level_text = level_font.render(f"LEVEL {level} COMPLETE!", True, YELLOW)
            restart_text = font.render("Press R to continue", True, WHITE)
            screen.blit(level_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 20))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()