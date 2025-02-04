"""The Snake game."""
from itertools import product
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

# Border color for "Game Over":
GO_BORDER_COLOR = (5, 5, 5)
# Border color for "You won!":
V_BORDER_COLOR = (240, 240, 240)
BORDER_WIDTH = 6

SCORE_COLOR = (10, 10, 10)

SCORE_BACKGROUND_COLOR = (200, 200, 200)

GAME_OVER_COLOR = (195, 9, 9)
VICTORY_COLOR = (20, 180, 20)

DIFFICULTIES = {'easy': 10, 'medium': 20, 'hard': 30}
DIFFICULTY_COLORS = {'easy': (0, 150, 0),
                     'medium': (150, 150, 0),
                     'hard': (150, 0, 0)}

SNAKE_DEF_LENGTH = 2

# Set this True if you don't want your results to be saved:
DEBUG = False

RESULTS_DIR = 'results/'

# Specify graphic files:
GRAPHICS_DIR = 'graphics/'
APPLE_SPRITE = 'Apple.png'
BACKGROUND_IMAGE = 'Ground.png'
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

CENTER_POSITION = (SCREEN_WIDTH // 2, GAME_HEIGHT // 2)

SCORE_POSITION = (SCREEN_WIDTH / 2, GAME_HEIGHT + GRID_SIZE / 2 + 4)

HIGHTSCORE_POSITION = (2 * GRID_SIZE, GAME_HEIGHT + GRID_SIZE / 2 + 4)

EVENT_TEXT_FONT_SIZE = SCREEN_WIDTH // 9
# Setting outline positions so that it protrudes per BORDER_WIDTH on each side:
CENTER_TEXT_OUTLINE_POS = product(
    (CENTER_POSITION[0] - BORDER_WIDTH, CENTER_POSITION[0] + BORDER_WIDTH),
    (CENTER_POSITION[1] - BORDER_WIDTH, CENTER_POSITION[1] + BORDER_WIDTH)
)

DIFFICULTY_SIZE = SCREEN_WIDTH // 18

# Create statistics files if does not exist:
open(f'{RESULTS_DIR}easy.txt', 'a').close()
open(f'{RESULTS_DIR}medium.txt', 'a').close()
open(f'{RESULTS_DIR}hard.txt', 'a').close()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 100)
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
        self.position = CENTER_POSITION

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


class EventText(TextObject):
    """The class template for text for game events like loss, victory etc."""

    def __init__(self):
        """Initialize the event inscript."""
        super().__init__()
        self.font = pygame.font.Font(f'{GRAPHICS_DIR}fonts/{MAIN_FONT}',
                                     EVENT_TEXT_FONT_SIZE)
        self.text_position = CENTER_POSITION
        self.event = ''
        self.border_color = None

    def __str__(self):
        """Generate the event string."""
        return self.event

    def _draw_outline(self, outline_position):
        text_inscript = self.font.render(self.__str__(),
                                         True, self.border_color)
        text_rect = text_inscript.get_rect(center=outline_position)
        screen.blit(text_inscript, text_rect)

    def draw(self):
        """Draw the event text."""
        # Making the outline
        for position in CENTER_TEXT_OUTLINE_POS:
            self._draw_outline(position)
        super().draw()


# Game classes:
class Apple(GameObject):
    """The class describing an apple and actions with it."""

    def __init__(self, snake):
        """Initialize an apple."""
        self.sprite = load_image(APPLE_SPRITE)
        self.randomize_position(snake)

    def randomize_position(self, snake):
        """Set a random position of the apple on the playing field."""
        # Generating a new apple if there are free positions, else victory:
        try:
            self.position = choice(get_free_positions(snake.positions))
        except IndexError:
            snake.won = True


class DifficultyButtonInscript(TextObject):
    """The class for inscription on the difficulty buttton in the main menu."""

    difficulties = tuple(DIFFICULTIES.keys())

    def __init__(self, difficulty):
        """Initialize the difficulty button inscription."""
        self.difficulty = difficulty
        super().__init__()
        self.font = pygame.font.Font(f'{GRAPHICS_DIR}fonts/{MAIN_FONT}',
                                     DIFFICULTY_SIZE)
        self.text_color = DIFFICULTY_COLORS[difficulty]
        self.text_position = (
            GAME_HEIGHT // len(self.difficulties)
            * (self.difficulties.index(difficulty) + 1),
            CENTER_POSITION[1]
        )

    def __str__(self):
        """Return difficulty string."""
        return self.difficulty


class GameOverInscript(EventText):
    """The class descibing the inscript, what apears when the game is over."""

    def __init__(self):
        """Initialize the game over inscript."""
        super().__init__()
        self.text_color = GAME_OVER_COLOR
        self.event = 'Game Over'
        self.border_color = GO_BORDER_COLOR


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
        self.score = snake_length - SNAKE_DEF_LENGTH

    def draw(self, snake_length):
        """Draw the score."""
        self._update(snake_length)
        super().draw()


class Hightscore(Score):
    """The class describing the hightscore."""

    def __init__(self, hightscore):
        """Initialize the hightscore."""
        super().__init__(hightscore)
        self.text_position = HIGHTSCORE_POSITION
        self.background_color = None

    def __str__(self):
        """Generate the hightscore string."""
        return f'HS: {self.hightscore}'

    def _update(self, hightscore):
        """Update the hightscore."""
        self.hightscore = hightscore


class Snake(GameObject):
    """The class describing a snake and its behavior."""

    won = False

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
        if self.length > SNAKE_DEF_LENGTH:
            # Drawing the neck:
            self._erase_sprite(self.prev_head_pos)
            if self.rotated:
                screen.blit(self.turning_bodies[(self.directions_que[-1],
                                                 self.direction)],
                            self.prev_head_pos)
            else:
                screen.blit(self.body_sprite_rotated[self.direction],
                            self.prev_head_pos)
        # Deleting point from rotate history if snake body passed it:
        if self.rotate_points and self.positions[-1] == self.rotate_points[0]:
            del self.rotate_points[0]
            del self.directions_que[0]
        # Drawing the tail:
        self._erase_sprite(self.positions[-1])
        screen.blit(self.tail_sprite_rotated[
            self.directions_que[0] if self.directions_que
            else self.direction
        ], self.positions[-1])
        # Erasing the head cell in case apple has been eaten:
        head_position = self.get_head_position
        self._erase_sprite(head_position)
        # Drawing snake head
        screen.blit(self.head_sprite_rotated[self.direction], head_position)
        # Reseting the rotate flag:
        self.rotated = False

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
        self.won = False
        # Erasing the snake:
        fill_background()
        # Reseting the snake:
        self.length = SNAKE_DEF_LENGTH
        self.positions = [self.position]
        self.direction = RIGHT
        self.rotated = False
        # We will append direction change history here
        # For correct tail rendering:
        self.directions_que = []
        self.rotate_points = []

    def update_direction(self, new_direction):
        """Update the direction after pressing the button."""
        self.direction = new_direction


class VictoryInscript(EventText):
    """The class descibing the inscript, what apears when the game is won."""

    def __init__(self):
        """Initialize the victory inscript."""
        super().__init__()
        self.text_color = VICTORY_COLOR
        self.event = 'You won!'
        self.border_color = V_BORDER_COLOR


def is_quited(event):
    """Check if quit event happend."""
    return (event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)


def handle_keys(difficulty: str, game_object: Snake, results: dict):
    """Process user actions."""
    snake_length = game_object.length
    for event in pygame.event.get():
        if is_quited(event):
            if snake_length > SNAKE_DEF_LENGTH:
                save_results(f'{difficulty}.txt', snake_length, results)
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            cur_key_direction = (event.key, game_object.direction)
            if cur_key_direction in DIRECTION_KEYS:
                game_object.rotated = True
                game_object.directions_que.append(game_object.direction)
                game_object.rotate_points.append(game_object.get_head_position)
                game_object.update_direction(DIRECTION_KEYS[cur_key_direction])
                # Preventing changing the direction more than 1 time
                # Per iteration:
                break


def handle_main_menu() -> str:
    """Maintain the main menu, return difficulty when choosed."""
    fill_background()
    difficulties = (
        DifficultyButtonInscript('easy'),
        DifficultyButtonInscript('medium'),
        DifficultyButtonInscript('hard')
    )
    for difficulty in difficulties:
        difficulty.draw()
    pygame.display.update()
    # Checking difficulty choosing:
    while True:
        for event in pygame.event.get():
            if is_quited(event):
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (CENTER_POSITION[1] - 100
                   < event.pos[1] < CENTER_POSITION[1] + 100):
                    choosed_difficulty = difficulties[
                        2 - (SCREEN_WIDTH - event.pos[0])
                        // (SCREEN_WIDTH // len(difficulties))
                    ].__str__()
                    fill_background()
                    return choosed_difficulty


def get_results(file_name: str) -> dict:
    """Get result from specific files."""
    with open(RESULTS_DIR + file_name, 'r', encoding="utf-8") as file:
        try:
            hightscore = int(file.readline().strip('\n'))
            averange_score = int(file.readline().strip('\n'))
            games_played = int(file.readline())
        except ValueError:
            hightscore = 0
            averange_score = 0
            games_played = 0
    results = {
        'hightscore': hightscore,
        'averange_score': averange_score,
        'games_played': games_played
    }
    return results


def save_results(file_name: str, snake_length: int, results: dict):
    """Save game results."""
    if not DEBUG:
        games_played = results['games_played'] + 1
        results['averange_score'] = int(((results['averange_score'] *
                                        results['games_played'] +
                                        snake_length - SNAKE_DEF_LENGTH) /
                                        games_played))
        results['games_played'] = games_played
        with open(RESULTS_DIR + file_name, 'w', encoding="utf-8") as file:
            file.write(f'{results["hightscore"]}\n'
                       f'{results["averange_score"]}\n{games_played}')


def win():
    """Generate and draw victory inscript."""
    victory = VictoryInscript()
    victory.draw()
    pygame.display.update()
    clock.tick(0.1)


def main():
    """Maintain the game."""
    # Initialising pygame and the objects:
    pygame.init()
    snake = Snake()
    apple = Apple(snake)
    score = Score(snake.length)
    # The backround is filled during snake.reset() in snake.__init__().
    # Now drawing the lower row for score
    # So it won't be empty during difficulty choosing:
    score.draw(snake.length)
    # Starting main menu to choose difficulty:
    difficulty = handle_main_menu()
    # Getting statistics:
    results = get_results(f'{difficulty}.txt')
    hightscore = Hightscore(results['hightscore'])

    # Starting the game:
    while True:
        clock.tick(DIFFICULTIES[difficulty])
        handle_keys(difficulty, snake, results)
        snake.move()
        # Checking if snake ate the apple:
        if snake.get_head_position == apple.position:
            snake.length += 1
            if snake.length > results['hightscore'] + SNAKE_DEF_LENGTH:
                results['hightscore'] = snake.length - SNAKE_DEF_LENGTH
            apple.randomize_position(snake)
            if snake.won:
                win()
                save_results(f'{difficulty}.txt', snake.length, results)
                snake.reset()
                apple.randomize_position(snake)
        # Checking if the snake has collided with itself:
        elif snake.get_head_position in snake.positions[2:]:
            save_results(f'{difficulty}.txt', snake.length, results)
            game_over_inscript = GameOverInscript()
            game_over_inscript.draw()
            pygame.display.update()
            clock.tick(0.5)
            snake.reset()
        apple.draw()
        snake.draw()
        score.draw(snake.length)
        hightscore.draw(results['hightscore'])
        pygame.display.update()


if __name__ == '__main__':
    main()
