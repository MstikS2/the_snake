"""The Snake game."""
from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 1000
GRID_SIZE = 40
GAME_HEIGHT = SCREEN_HEIGHT - GRID_SIZE
GAME_SPACE = [(i, j) for j in range(0, GAME_HEIGHT - GRID_SIZE, GRID_SIZE)
              for i in range(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE)]

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BORDER_COLOR = (0, 0, 0)

SCORE_COLOR = (10, 10, 10)

SCORE_BACKGROUND_COLOR = (230, 230, 230)

GAME_OVER_COLOR = (190, 32, 32)

DIFFICULTY_COLORS = {'easy': (0, 0, 0), 'medium': (0, 0, 0), 'hard': (0, 0, 0)}

DIFFICULTIES = {'easy': 10, 'medium': 20, 'hard': 30}

# Specify graphic files:
GRAPHICS_DIR = 'graphics/'
APPLE_SPRITE = 'Apple.png'
BACKGROUND_IMAGE = 'Grass.png'
MAIN_FONT = 'Font Over.otf'
SCORE_FONT = 'agat-8.ttf'
SNAKE_SPRITES_DIR = 'Snake/'
SNAKE_HEAD_SPRITE = 'Snake_head.png'
SNAKE_BODY_SPRITE = 'Snake_body.png'
SNAKE_TAIL_SPRITE = 'Snake_tail.png'
SNAKE_TURNING_DOWNLEFT = 'Snake_turning_downleft.png'
SNAKE_TURNING_DOWNRIGHT = 'Snake_turning_downright.png'
SNAKE_TURNING_LEFTUP = 'Snake_turning_leftup.png'
SNAKE_TURNING_UPRIGHT = 'Snake_turning_upright.png'

SCORE_POSITION = (SCREEN_WIDTH / 2, GAME_HEIGHT + GRID_SIZE / 2 + 4)

HIGHTSCORE_FONT_SIZE = GRID_SIZE / 2
HIGHTSCORE_POSITION = (SCREEN_WIDTH / 2 + 4 * GRID_SIZE,
                       SCREEN_HEIGHT - GRID_SIZE / 4)

GAME_OVER_FONT_SIZE = SCREEN_WIDTH // 9
GAME_OVER_POSITION = (SCREEN_WIDTH / 2, GAME_HEIGHT / 2)
GAME_OVER_OUTLINE_POS = (
    (GAME_OVER_POSITION[0] - 4, GAME_OVER_POSITION[1] - 4),
    (GAME_OVER_POSITION[0] + 4, GAME_OVER_POSITION[1] - 4),
    (GAME_OVER_POSITION[0] - 4, GAME_OVER_POSITION[1] + 4),
    (GAME_OVER_POSITION[0] + 4, GAME_OVER_POSITION[1] + 4)
)

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


def get_free_positions(snake_positions: list) -> list:
    """Return list of free cells on the game board."""
    if snake_positions:
        return list(set(GAME_SPACE) - set(snake_positions))
    else:
        return GAME_SPACE


def load_image(image_file: str,
               size=(GRID_SIZE, GRID_SIZE)) -> pygame.surface.Surface:
    """Load image and transform it, return pygame image surface."""
    img = pygame.image.load(GRAPHICS_DIR + image_file)
    return pygame.transform.scale(img, size)


def fill_background():
    """Fill the game board with background image."""
    screen.blit(load_image(BACKGROUND_IMAGE, (SCREEN_WIDTH, GAME_HEIGHT)),
                (0, 0))


# Base classes:
class GameObject:
    """The base class from which other game objects inherit."""

    def __init__(self):
        """Initialize a game object."""
        self.sprite = None
        self.position = ((SCREEN_WIDTH // 2), (GAME_HEIGHT // 2))

    def draw(self):
        """Draw an object."""
        screen.blit(self.sprite, self.position)

    def _erase_sprite(self, position):
        """Erase the sprite and restore the background cell."""
        background = load_image(BACKGROUND_IMAGE,
                                (SCREEN_WIDTH, GAME_HEIGHT))
        erasing_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        background_cell = background.subsurface(erasing_rect)
        screen.blit(background_cell, position)


class TextObject:
    """The base class from which other text objects inherit."""

    def __init__(self):
        """Initialize a text object."""
        self.font = None
        self.text_color = None
        self.text_position = None
        self.background_color = None
        self.background_rect = None

    def draw(self):
        """Draw the text."""
        text_inscript = self.font.render(self.__str__(), True,
                                         self.text_color)
        if self.background_color:
            pygame.draw.rect(screen, self.background_color,
                             self.background_rect)
        text_rect = text_inscript.get_rect(center=self.text_position)
        screen.blit(text_inscript, text_rect)


# Game classes:
class Apple(GameObject):
    """The class describing an apple and actions with it."""

    def __init__(self):
        """Initialize an apple."""
        self.sprite = load_image(APPLE_SPRITE)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Set a random position of the apple on the playing field."""
        self.position = choice(get_free_positions(snake_positions))


class DifficultButtonInscript(TextObject):
    """The class for inscription on the difficulty buttton in the main menu."""

    def __init__(self, difficulty):
        """Initialize the difficulty button inscription."""
        super().__init__()
        self.font = pygame.font.Font(f'{GRAPHICS_DIR}fonts/{MAIN_FONT}',
                                     GRID_SIZE - 4)
        self.text_color = DIFFICULTY_COLORS[difficulty]


class GameOverInscript(TextObject):
    """The class descibing the inscript, what apears when the game is over."""

    def __init__(self):
        """Initialize the game over inscript."""
        super().__init__()
        self.font = pygame.font.Font(f'{GRAPHICS_DIR}fonts/{MAIN_FONT}',
                                     GAME_OVER_FONT_SIZE)
        self.text_color = GAME_OVER_COLOR
        self.text_position = GAME_OVER_POSITION

    def __str__(self):
        """Generate the game over string."""
        return 'Game over'

    def _draw_outline(self, outline_position):
        text_inscript = self.font.render(self.__str__(), True, BORDER_COLOR)
        text_rect = text_inscript.get_rect(center=outline_position)
        screen.blit(text_inscript, text_rect)

    def draw(self):
        """Draw the game over."""
        # Making the outline
        for position in GAME_OVER_OUTLINE_POS:
            self._draw_outline(position)
        super().draw()


class Score(TextObject):
    """The class describing the score."""

    def __init__(self, snake_length):
        """Initialize the score."""
        self.font = pygame.font.Font(f'{GRAPHICS_DIR}fonts/{SCORE_FONT}',
                                     GRID_SIZE)
        self.text_color = SCORE_COLOR
        self.text_position = SCORE_POSITION
        self.background_color = SCORE_BACKGROUND_COLOR
        self.background_rect = pygame.Rect((0, GAME_HEIGHT),
                                           (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._update(snake_length)

    def __str__(self):
        """Generate the score string."""
        return f'Score: {self.score}'

    def _update(self, snake_length):
        """Update the score."""
        self.score = snake_length

    def draw(self, snake_length):
        """Draw the score."""
        self._update(snake_length)
        super().draw()


class Snake(GameObject):
    """The class describing a snake and its behavior."""

    def __init__(self):
        """Initialize a snake."""
        super().__init__()
        self.reset()
        # Loading snake sprites and rotating them:
        self.head_sprite = load_image(SNAKE_SPRITES_DIR + SNAKE_HEAD_SPRITE)
        self.head_sprite_rotated = self._rotate_sprite(self.head_sprite)
        self.body_sprite = load_image(SNAKE_SPRITES_DIR + SNAKE_BODY_SPRITE)
        self.body_sprite_rotated = self._rotate_sprite(self.body_sprite)
        self.tail_sprite = load_image(SNAKE_SPRITES_DIR + SNAKE_TAIL_SPRITE)
        self.tail_sprite_rotated = self._rotate_sprite(self.tail_sprite)
        # This dict contains correct body turning sprites for every turning
        # (Load an image and flip + rotate if needed)
        # !!! DO NOT CONFUSE THE DIRECTION IN THIS DICT
        # AND THE ANGLE IN THE FILE NAME !!!
        self.turning_bodies = {
            (UP, RIGHT): load_image(SNAKE_SPRITES_DIR +
                                    SNAKE_TURNING_DOWNRIGHT),
            (UP, LEFT): load_image(SNAKE_SPRITES_DIR +
                                   SNAKE_TURNING_DOWNLEFT),
            (RIGHT, DOWN): pygame.transform.rotate(pygame.transform.flip(
                load_image(SNAKE_SPRITES_DIR + SNAKE_TURNING_UPRIGHT),
                False, True
            ), -90),
            (RIGHT, UP): load_image(SNAKE_SPRITES_DIR + SNAKE_TURNING_LEFTUP),
            (DOWN, LEFT): pygame.transform.rotate(pygame.transform.flip(
                load_image(SNAKE_SPRITES_DIR + SNAKE_TURNING_LEFTUP),
                True, False
            ), 90),
            (DOWN, RIGHT): load_image(SNAKE_SPRITES_DIR +
                                      SNAKE_TURNING_UPRIGHT),
            (LEFT, UP): pygame.transform.rotate(pygame.transform.flip(
                load_image(SNAKE_SPRITES_DIR + SNAKE_TURNING_DOWNLEFT),
                False, True
            ), -90),
            (LEFT, DOWN): pygame.transform.rotate(pygame.transform.flip(
                load_image(SNAKE_SPRITES_DIR + SNAKE_TURNING_DOWNRIGHT),
                True, False
            ), 90),
        }

    def draw(self):
        """Draw the snake."""
        # Drawing body sprite instead of head and the tail:
        if self.length > 2:
            # Drawing the neck:
            self._erase_sprite(self.prev_head_pos)
            if self.rotated:
                screen.blit(self.turning_bodies[(self.directions_stack[-1],
                                                 self.direction)],
                            self.prev_head_pos)
            else:
                screen.blit(self.body_sprite_rotated[self.direction],
                            self.prev_head_pos)
        # Drawing the tail:
        self._erase_sprite(self.positions[-1])
        screen.blit(self.tail_sprite_rotated[
            self.directions_stack[0] if self.directions_stack
            else self.direction
        ], self.positions[-1])
        # Erasing the head cell in case apple has been eaten:
        head_position = self.get_head_position
        self._erase_sprite(head_position)
        # Drawing snake head
        screen.blit(self.head_sprite_rotated[self.direction], head_position)
        # Reseting the rotate flag:
        self.rotated = False
        # Deleting point from rotate history if snake body passed it:
        if self.rotate_points and self.positions[-1] == self.rotate_points[0]:
            del self.rotate_points[0]
            del self.directions_stack[0]

        # Erasing the last element
        # Checking the coincidence of the head and tail is needed for cases
        # When the head crawls onto the cell where the tail just was.
        # In this case, without checking, the cell with its head is painted
        # Over and in the future remains a hole in the snake in this place
        if self.last and self.last != head_position:
            self._erase_sprite(self.last)

    @property
    def get_head_position(self) -> tuple:
        """Returns snake head position."""
        return self.positions[0]

    def move(self):
        """Update the position of the snake.

        Add a new head to the beginning of the list
        and remove the last element - the tail.
        """
        self.prev_head_pos = self.get_head_position
        new_x_head_position = (self.prev_head_pos[0]
                               + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        new_y_head_position = (self.prev_head_pos[1]
                               + self.direction[1] * GRID_SIZE) % GAME_HEIGHT
        self.positions.insert(0, (new_x_head_position, new_y_head_position))
        # When the apple is eaten:
        if self.length == len(self.positions):
            self.last = None
        # When the apple is not eaten:
        else:
            # Removing a segment from the snake
            # And save the coordinates for shading in draw():
            self.last = self.positions.pop()
        if self.rotate_points and self.positions[-1] == self.rotate_points[0]:
            del self.rotate_points[0]
            del self.directions_stack[0]

    def _rotate_sprite(self, sprite: pygame.surface.Surface) -> dict:
        """Return dict with correctly rotated sprite for every direction."""
        sprites = {
            UP: sprite,
            LEFT: pygame.transform.flip(
                pygame.transform.rotate(sprite, 90), False, True
            ),
            RIGHT: pygame.transform.rotate(sprite, -90),
            DOWN: pygame.transform.flip(sprite, False, True)
        }
        return sprites

    def reset(self):
        """Reset the snake to its initial state."""
        # Erasing the snake:
        fill_background()
        # Reseting the snake:
        self.length = 2
        self.positions = [self.position]
        self.direction = RIGHT
        self.rotated = False
        # We will append direction change history here
        # For correct tail rendering:
        self.directions_stack = []
        self.rotate_points = []

    def update_direction(self, new_direction):
        """Update the direction after pressing the button."""
        self.direction = new_direction


def handle_keys(game_object: Snake):
    """Process user actions."""
    for event in pygame.event.get():
        if (event.type == pygame.QUIT
           or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            cur_key_direction = (event.key, game_object.direction)
            if cur_key_direction in DIRECTION_KEYS:
                game_object.rotated = True
                game_object.directions_stack.append(game_object.direction)
                game_object.rotate_points.append(game_object.get_head_position)
                game_object.update_direction(DIRECTION_KEYS[cur_key_direction])
                # Preventing changing the direction more than 1 time
                # Per iteration:
                break


def handle_main_menu():
    """Maintain the main menu."""
    pygame.init()
    fill_background()


def main():
    """Maintain the game."""
    # Initializing PyGame and opjects:
    handle_main_menu()
    apple = Apple()
    snake = Snake()
    score = Score(snake.length)
    game_over_inscript = GameOverInscript()

    # Starting the game:
    while True:
        clock.tick(DIFFICULTIES['medium'])
        handle_keys(snake)
        snake.move()
        # Checking if snake ate the apple:
        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Checking if the snake has collided with itself:
        elif snake.get_head_position in snake.positions[2:]:
            game_over_inscript.draw()
            pygame.display.update()
            clock.tick(0.5)
            snake.reset()
        apple.draw()
        snake.draw()
        score.draw(snake.length)
        pygame.display.update()


if __name__ == '__main__':
    main()
