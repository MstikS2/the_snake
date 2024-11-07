from random import randrange

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
# Эти константы не нужны, но без них код не проходит автоматические тесты:
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self) -> None:
        self.body_color = None
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

    def draw(self):
        """
        Заготовка метода для отрисовки объекта,
        переопределяется в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self):
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, snake=None):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            new_position = (randrange(0, SCREEN_WIDTH, GRID_SIZE),
                            randrange(0, SCREEN_HEIGHT, GRID_SIZE))
            # Проверяем, не появилось ли яблоко в змее:
            if not snake or (new_position not in snake.positions):
                self.position = new_position
                break


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        super().__init__()
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR

    def draw(self):
        """Отрисовывает змейку."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

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
        # Проверяем, вышла ли змейка за границу экрана:
        if self.get_head_position[0] < 0:
            self.positions.insert(0, (SCREEN_WIDTH - GRID_SIZE,
                                      self.get_head_position[1]))
        elif self.get_head_position[1] < 0:
            self.positions.insert(0, (self.get_head_position[0],
                                      SCREEN_HEIGHT - GRID_SIZE))
        elif self.get_head_position[0] > SCREEN_WIDTH - GRID_SIZE:
            self.positions.insert(0, (0, self.get_head_position[1]))
        elif self.get_head_position[1] > SCREEN_HEIGHT - GRID_SIZE:
            self.positions.insert(0, (self.get_head_position[0], 0))
        # Если не вышла:
        else:
            self.positions.insert(
                0,
                (self.get_head_position[0] + self.direction[0] * 20,
                 self.get_head_position[1] + self.direction[1] * 20)
            )

        # Если яблоко не съедено:
        if self.get_head_position != apple.position:
            # Удаляем сегмент из змейки
            # И сохраняем координаты для закраски в draw():
            self.last = self.positions.pop(-1)
        else:
            self.length += 1
            apple.randomize_position(self)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        # Затираем змейку:
        for position in self.positions:
            position_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, position_rect)
        # Обнуляем змейку:
        self.__init__()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Обрабатывает действия пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (event.key in (pygame.K_UP, pygame.K_w)
               and game_object.direction != DOWN):
                game_object.next_direction = UP
            elif (event.key in (pygame.K_DOWN, pygame.K_s)
                  and game_object.direction != UP):
                game_object.next_direction = DOWN
            elif (event.key in (pygame.K_LEFT, pygame.K_a)
                  and game_object.direction != RIGHT):
                game_object.next_direction = LEFT
            elif (event.key in (pygame.K_RIGHT, pygame.K_d)
                  and game_object.direction != LEFT):
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:
        handle_keys(snake)
        snake.update_direction()
        clock.tick(SPEED)
        snake.move(apple)
        if snake.positions.count(snake.get_head_position) > 1:
            snake.reset()
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
