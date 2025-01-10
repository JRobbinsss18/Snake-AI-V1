# SnakeGame class
# Class to play Snake AND handle how data is sent to Agent
import pygame
import random

# Snake game
class SnakeGame:
    
    # Initialize game
    def __init__(self, width=640, height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.reset()
    
    # Reset game
    def reset(self):
        self.snake_pos = [self.width / 2, self.height / 2]
        self.snake_body = [[self.snake_pos[0], self.snake_pos[1]]]
        self.food_pos = [random.randrange(1, (self.width//10)) * 10, random.randrange(1, (self.height//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
    
    # If collision occurs return true
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snake_pos
        # Checks if the snake collides with boundaries
        if pt[0] < 0 or pt[0] > self.width-10 or pt[1] < 0 or pt[1] > self.height-10:
            return True
        # Checks if the snake collides with itself
        if pt in self.snake_body[1:]:
            return True
        return False

    # Display Score
    def display_score(self):
        font = pygame.font.SysFont('arial', 35)
        score_surface = font.render(f'Score: {self.score}', True, (255, 255, 255))
        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.width / 10, 15)
        self.screen.blit(score_surface, score_rect)

    # Get State
    def get_state(self):
        # Head position
        head_x, head_y = self.snake_pos
        # Food position
        food_x, food_y = self.food_pos
        # Bool directionals
        dir_left = self.direction == 'LEFT'
        dir_right = self.direction == 'RIGHT'
        dir_up = self.direction == 'UP'
        dir_down = self.direction == 'DOWN'

        # Put state together
        state = [
            # Food location relative to snake head
            (food_x < head_x),  # Food left
            (food_x > head_x),  # Food right
            (food_y < head_y),  # Food up
            (food_y > head_y),  # Food down

            # Current direction
            dir_left,
            dir_right,
            dir_up,
            dir_down,

            # Danger straight
            self.is_collision([head_x + (dir_right - dir_left) * 10, head_y + (dir_down - dir_up) * 10]),
            # Danger right
            self.is_collision([head_x + (dir_down - dir_up) * 10, head_y + (dir_left - dir_right) * 10]),
            # Danger left
            self.is_collision([head_x + (dir_up - dir_down) * 10, head_y + (dir_right - dir_left) * 10])
            ]
        return state

    def calculate_reward(self, eaten, collided):
        if collided:
            return -10
        reward = 5 if eaten else 0
        return reward

    
    def step(self, action):
        # Set up action dictionary
        action_dict = {0: 'UP', 1: 'DOWN', 2: 'LEFT', 3: 'RIGHT'}
        self.change_to = action_dict[action]

        # Handle change
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        elif self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

        # Move snakes head
        if self.direction == 'UP':
            self.snake_pos[1] -= 10
        elif self.direction == 'DOWN':
            self.snake_pos[1] += 10
        elif self.direction == 'LEFT':
            self.snake_pos[0] -= 10
        elif self.direction == 'RIGHT':
            self.snake_pos[0] += 10

        # Check if snake eats food
        eaten = self.snake_pos == self.food_pos
        if eaten:
            self.score += 1
            self.food_spawn = False
        else:
            self.snake_body.pop()

        # Spawn new food if needed
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (self.width//10)) * 10, random.randrange(1, (self.height//10)) * 10]
            self.food_spawn = True

        # Increment Snake's body if needed
        self.snake_body.insert(0, list(self.snake_pos))

        # Check for collision
        collided = self.is_collision()
        
        # Calculate reward
        reward = self.calculate_reward(eaten, collided)
        
        # Prepare for next state
        next_state = self.get_state()
        return next_state, reward, collided

    # Update game, handles actual game mechanics
    def update_game(self):
        # Moving the snake according to the current direction
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        elif self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        elif self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

        # Move the snake's head based on the direction
        if self.direction == 'UP':
            self.snake_pos[1] -= 10
        elif self.direction == 'DOWN':
            self.snake_pos[1] += 10
        elif self.direction == 'LEFT':
            self.snake_pos[0] -= 10
        elif self.direction == 'RIGHT':
            self.snake_pos[0] += 10
        self.manage_snake_body()

    # Actual game visuals
    def render_game(self):
        self.screen.fill((0, 0, 0))
        for pos in self.snake_body:
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))
        self.display_score()
        pygame.display.update()

    # Snake mechanics
    def manage_snake_body(self):
        self.snake_body.insert(0, list(self.snake_pos))
        if self.snake_pos == self.food_pos:
            self.score += 1
            self.food_spawn = False
        else:
            self.snake_body.pop()
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (self.width//10)) * 10, random.randrange(1, (self.height//10)) * 10]
            self.food_spawn = True

    # Game driver
    def run(self, training=False, render=True):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not training:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.change_to = 'UP'
                        elif event.key == pygame.K_DOWN:
                            self.change_to = 'DOWN'
                        elif event.key == pygame.K_LEFT:
                            self.change_to = 'LEFT'
                        elif event.key == pygame.K_RIGHT:
                            self.change_to = 'RIGHT'

            # Update the game state
            if training:
                # Agent decides action based on current state
                action = agent.act(self.get_state())
                # Execute action (step) and update game state
                _, _, done = self.step(action)
            else:
                # Update game state
                self.update_game()
            # Render game
            if render:
                self.render_game()
            # Check if game should end
            if self.is_collision():
                running = False
            
            self.clock.tick(30) # SPEED OF GAME <-------------------------------
        pygame.quit()

# Main
if __name__ == "__main__":
    game = SnakeGame()
    game.run()

