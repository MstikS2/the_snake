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

    def draw(self):
        """Отрисовывает змейку."""
        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
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
        x_head_position, y_head_position = self.get_head_position
        new_x_head_position = (x_head_position
                               + self.direction[0] * 20) % SCREEN_WIDTH
        new_y_head_position = (y_head_position
                               + self.direction[1] * 20) % GAME_HEIGHT
        self.positions.insert(0, (new_x_head_position, new_y_head_position))
        # При съеденном яблоке:
        if self.length == len(self.positions):
            self.last = None
        # При несъеденном яблоке:
        else:
            # Удаляем сегмент из змейки
            # И сохраняем координаты для закраски в draw():
            self.last = self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        # Затираем змейку:
        background_rect = pygame.Rect((0, 0), (SCREEN_WIDTH, GAME_HEIGHT))
        pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, background_rect)
        # Обнуляем змейку:
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.body_color = SNAKE_COLOR

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
            cur_key_direction = (event.key, game_object.direction)
            if cur_key_direction in DIRECTION_KEYS:
                game_object.update_direction(DIRECTION_KEYS[cur_key_direction])
                # Оказалось, что если, например, при движении вправо,
                # Быстро нажать клавишу вверх и клавишу влево, то змейка
                # Развернётся на 180 градусов, не успев переползти
                # На клетку вверх. В результате, либо она просто двигается
                # Назад, если состоит из 1 клетки, либо сталкивается
                # Со своей шеей. Чтобы предотвратить обрабатывание более
                # 1 изменения направления в ходе 1 итерации главного цикла:
                break


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
        snake.move(apple)
        # Проверяем, съела ли змейка яблоко:
        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Проверяем, не столкнулась ли змейка с собой:
        elif snake.get_head_position in snake.positions[2:]:
            clock.tick(0.5)
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
