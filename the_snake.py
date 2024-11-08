from random import randrange

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 500
GRID_SIZE = 20
GAME_HEIGHT = SCREEN_HEIGHT - GRID_SIZE
# Эти константы не нужны, но без них код не проходит автоматические тесты:
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


DIRECTION_KEYS = {
    (pygame.K_s, pygame.K_DOWN, LEFT, RIGHT): DOWN,
    (pygame.K_w, pygame.K_UP, LEFT, RIGHT): UP,
    (pygame.K_a, pygame.K_LEFT, UP, DOWN): LEFT,
    (pygame.K_d, pygame.K_RIGHT, UP, DOWN): RIGHT
}


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self) -> None:
        self.body_color = None
        self.position = ((SCREEN_WIDTH // 2), (GAME_HEIGHT // 2))

    def draw(self):
        """Заготовка метода для отрисовки объекта."""
        rect = (pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE)))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self):
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            new_position = (randrange(0, SCREEN_WIDTH, GRID_SIZE),
                            randrange(0, GAME_HEIGHT, GRID_SIZE))
            # Проверяем, не появилось ли яблоко в змее:
            if not snake_positions or (new_position not in snake_positions):
                self.position = new_position
                break


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.body_color = SNAKE_COLOR

    def draw(self):
        """Отрисовывает змейку."""
        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last != self.positions[0]:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    @property
    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self, apple):
        """
        Обновляет позицию змейки (добовляет новую голову в начало списка
        и удаляет последний элемент - хвост).
        """
        self.positions.insert(
            0,
            ((self.get_head_position[0] + self.direction[0] * 20)
             % SCREEN_WIDTH,
             (self.get_head_position[1] + self.direction[1] * 20)
             % GAME_HEIGHT)
        )

        # Если яблоко не съедено:
        if self.get_head_position != apple.position:
            # Удаляем сегмент из змейки
            # И сохраняем координаты для закраски в draw():
            self.last = self.positions.pop(-1)
        # Если яблоко съедено:
        else:
            self.length += 1
            apple.randomize_position(self.positions)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        # Затираем змейку:
        background_rect = pygame.Rect((0, 0), (SCREEN_WIDTH, GAME_HEIGHT))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, background_rect)
        # Обнуляем змейку:
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT

    def update_direction(self, new_direction):
        """Метод обновления направления после нажатия на кнопку."""
        self.direction = new_direction


def handle_keys(game_object: Snake):
    """Обрабатывает действия пользователя."""
    for event in pygame.event.get():
        if (event.type == pygame.QUIT
           or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            for keys in DIRECTION_KEYS:
                if event.key in keys and game_object.direction in keys:
                    game_object.update_direction(DIRECTION_KEYS[keys])


def main():
    """Основной игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    font = pygame.font.SysFont('Comic Sams MS', 30)
    apple = Apple()
    snake = Snake()
    # Блок для вывода счёта:
    score_background = pygame.Rect((0, GAME_HEIGHT),
                                   (SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        handle_keys(snake)
        clock.tick(SPEED)
        # Если змейка съела яблоко, метод move не обновляет позицию
        # Последнего сегмента, из-за чего эта позиция не передаётся в draw,
        # draw его не закрашивает и змейка увеличивается на 1 сегмент.
        snake.move(apple)
        # Проверяем, не столкнулась ли змейка с собой:
        if snake.positions.count(snake.get_head_position) > 1:
            snake.reset()
        apple.draw()
        snake.draw()
        # Обновление счёта:
        score = font.render(f'Score: {snake.length}', False, (0, 0, 0))
        pygame.draw.rect(screen, (230, 230, 230), score_background)
        screen.blit(score, (SCREEN_WIDTH / 2 - 50, GAME_HEIGHT))
        pygame.display.update()


if __name__ == '__main__':
    main()
