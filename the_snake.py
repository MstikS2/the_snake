from random import randrange

import pygame

GRAPHICS_DIR = 'graphics/'

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 500
GRID_SIZE = 20
GAME_HEIGHT = SCREEN_HEIGHT - GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
icon = pygame.image.load(f'{GRAPHICS_DIR}SNAKE.ico')
pygame.display.set_icon(icon)

pygame.display.set_caption('Snake')

clock = pygame.time.Clock()


DIRECTION_KEYS = {
    (pygame.K_s, RIGHT): DOWN,
    (pygame.K_s, LEFT): DOWN,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_w, RIGHT): UP,
    (pygame.K_w, LEFT): UP,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_a, DOWN): LEFT,
    (pygame.K_a, UP): LEFT,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_d, DOWN): RIGHT,
    (pygame.K_d, UP): RIGHT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT
}


class GameObject:
    """The base class from which other game objects inherit."""

    def __init__(self) -> None:
        self.body_color = None
        self.position = ((SCREEN_WIDTH // 2), (GAME_HEIGHT // 2))

    def draw(self):
        """Preparing a method for drawing an object."""
        rect = (pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE)))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """A class describing an apple and actions with it."""

    def __init__(self):
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Sets a random position of the apple on the playing field."""
        while True:
            new_position = (randrange(0, SCREEN_WIDTH, GRID_SIZE),
                            randrange(0, GAME_HEIGHT, GRID_SIZE))
            # Checking if the apple has appeared in the snake:
            if not snake_positions or (new_position not in snake_positions):
                self.position = new_position
                break


class Snake(GameObject):
    """A class describing a snake and its behavior."""

    def __init__(self):
        super().__init__()
        self.reset()

    def draw(self):
        """Draws the snake."""
        # Draws snake head
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Erasing the last element
        # Checking the coincidence of the head and tail is needed for cases
        # When the head crawls onto the cell where the tail just was.
        # In this case, without checking, the cell with its head is painted
        # Over and in the future remains a hole in the snake in this place
        if self.last and self.last != self.get_head_position:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    @property
    def get_head_position(self):
        """Returns snake head position."""
        return self.positions[0]

    def move(self, apple):
        """
        Updates the position of the snake (adds a new head to the beginning
        of the list and removes the last element - the tail).
        """
        x_head_position, y_head_position = self.get_head_position
        new_x_head_position = (x_head_position
                               + self.direction[0] * 20) % SCREEN_WIDTH
        new_y_head_position = (y_head_position
                               + self.direction[1] * 20) % GAME_HEIGHT
        self.positions.insert(0, (new_x_head_position, new_y_head_position))
        # When the apple is eaten:
        if self.length == len(self.positions):
            self.last = None
        # When the apple is not eaten:
        else:
            # Removing a segment from the snake
            # And save the coordinates for shading in draw():
            self.last = self.positions.pop()

    def reset(self):
        """Resets the snake to its initial state."""
        # Erasing the snake:
        background_rect = pygame.Rect((0, 0), (SCREEN_WIDTH, GAME_HEIGHT))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, background_rect)
        # Reseting the snake:
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.body_color = SNAKE_COLOR

    def update_direction(self, new_direction):
        """Method for updating the direction after pressing the button."""
        self.direction = new_direction


def handle_keys(game_object: Snake):
    """Processes user actions."""
    for event in pygame.event.get():
        if (event.type == pygame.QUIT
           or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            cur_key_direction = (event.key, game_object.direction)
            if cur_key_direction in DIRECTION_KEYS:
                game_object.update_direction(DIRECTION_KEYS[cur_key_direction])
                # Preventing changing the direction more than 1 time
                # Per iteration
                break


def main():
    """Main game loop."""
    # Initializing PyGame:
    pygame.init()
    font = pygame.font.SysFont('Comic Sams MS', 30)
    apple = Apple()
    snake = Snake()
    # Block for displaying the score:
    score_background = pygame.Rect((0, GAME_HEIGHT),
                                   (SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        handle_keys(snake)
        clock.tick(SPEED)
        snake.move(apple)
        # Checking if snake ate the apple:
        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Checking if the snake has collided with itself:
        elif snake.get_head_position in snake.positions[2:]:
            clock.tick(0.5)
            snake.reset()
        apple.draw()
        snake.draw()
        # Score update:
        score = font.render(f'Score: {snake.length}', False, (0, 0, 0))
        pygame.draw.rect(screen, (230, 230, 230), score_background)
        screen.blit(score, (SCREEN_WIDTH / 2 - 50, GAME_HEIGHT))
        pygame.display.update()


if __name__ == '__main__':
    main()
