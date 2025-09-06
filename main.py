import pygame
import json
import abc

pygame.init()

# Размер экрана и загрузка изображений
sc_width, sc_height = 1280, 720
screen = pygame.display.set_mode((sc_width, sc_height))
pygame.display.set_caption("Ball vs. Squares")
fon = pygame.image.load("img/game/fon.png")
restart_img = pygame.image.load("img/ui/restart.png")
menu_img = pygame.image.load("img/ui/menu.png")
start_img = pygame.image.load("img/ui/start.png")
exit_img = pygame.image.load("img/ui/exit.png")
end_img = pygame.image.load("img/ui/end.png")
exit_menu_img = pygame.image.load("img/ui/back.png")
heart_lives_img = pygame.image.load("img/ui/heart.png")
pizza_img = pygame.image.load("img/ui/pizza.png")
img_icon = pygame.image.load("img/ui/gg1.ico")
icon = pygame.display.set_icon(img_icon)

# Звуки
pygame.mixer.init()
sound_dead = pygame.mixer.Sound("sounds/sound/dead1.mp3")
teleport_sound = pygame.mixer.Sound("sounds/sound/teleport1.mp3")
jump_sound = pygame.mixer.Sound("sounds/sound/jump1.mp3")
take_coin = pygame.mixer.Sound("sounds/sound/take_coin.mp3")

# Музыка

# Кадры в секунду
clock = pygame.time.Clock()
fps = 120

score = 0 # Счет
lives = 5 # Жизни
tile_size = 40  # Размер блока
game_over = 1 # Состояние игры (1 - игра идет, 0 - игра останавливается, 2 - переход на следующий уровень 3 - экран финала)
main_menu = True # Состояние меню (T - показывается, F - не показывается)
font = pygame.font.SysFont(None, 40) # Шрифт и размер для надписи score
font_large = pygame.font.SysFont(None, 100) # Шрифт и размер в конце


class Button:
    """ Класс кнопки"""
    def __init__(self, x, y, image, scale_factor=1.1):
        """Получение значений координат и изображение"""
        self.original_image = image
        self.original_x = x
        self.original_y = y
        self.scale_factor = scale_factor

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw_button(self):
        """Получение значений координат и изображение и проверка нажатия"""
        action = False
        pos = pygame.mouse.get_pos() # Получение позиции мышки

        if self.rect.collidepoint(pos):
            # Увеличение
            width = int(self.original_image.get_width() * self.scale_factor)
            height = int(self.original_image.get_height() * self.scale_factor)
            self.image = pygame.transform.scale(self.original_image, (width, height))
            self.rect = self.image.get_rect()
            self.rect.center = (self.original_x + self.original_image.get_width() // 2,
                                self.original_y + self.original_image.get_height() // 2)
        else:
            # Возвращение обычного размера
            self.image = self.original_image
            self.rect = self.image.get_rect()
            self.rect.x = self.original_x
            self.rect.y = self.original_y

        if self.rect.collidepoint(pos): # Проверка, находится ли точка (pos) внутри прямоугольника кнопки
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # Проверка нажата ли ЛКМ
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0: # Если отпущена сбрасываем флаг "нажата"
            self.clicked = False

        screen.blit(self.image, self.rect) # Отрисовка
        return action


class Player:
    def __init__(self, x, y, speed):
        """Получение значений координат и установка нужных атрибутов"""
        self.images_right = [] # Спрайты движения вправо
        self.images_left = [] # Спрайты движения влево
        self.index = 0 # Текущий кадр анимации
        self.counter = 0 # Счётчик для скорости анимации
        self.direction = 0 # Направление (1 - вправо, -1 - влево)

        for num in range(1, 18):
            img_right = pygame.image.load(f"img/character/gg{num}.png")
            img_right = pygame.transform.scale(img_right, (35, 35)) # Масштабирование
            img_left = pygame.transform.flip(img_right, True, False) # Зеркальное отражение
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index] # Текущее изображение и рисовка прямоугольника для коллизии
        self.rect = self.image.get_rect()

        self.dead_image = pygame.image.load("img/character/dead.png") # Изображение при проигрыше
        self.dead_image = pygame.transform.scale(self.dead_image, (35, 35))

        # Позиция и скорость
        self.speed = speed
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.jump_y = 0 # Вертикальная скорость прыжка
        self.jumped = False # Флаг прыжка
        self.last_jump_time = 0 # Время последнего прыжка
        self.jump_cooldown = 700 # Задержка между прыжками (мс)

    def movement(self, game_over):
        """Обработка нажатий игрока и действия"""
        dx, dy = 0, 0
        walk_cooldown = 1
        col_edge = 40

        if game_over == 1:
            # Обработка ввода с клавиатуры
            key = pygame.key.get_pressed()
            press_time = pygame.time.get_ticks()

            # Движение вправо/влево
            if key[pygame.K_RIGHT]:
                dx += self.speed
                self.counter += 1
                self.direction = 1
            elif key[pygame.K_LEFT]:
                dx -= self.speed
                self.counter += 1
                self.direction = -1
            # Проверка границ экрана по X
            if self.rect.left + dx < 0:  # Левая граница
                dx = -self.rect.left  # Останавливаем у края
            elif self.rect.right + dx > sc_width:  # Правая граница
                dx = sc_width - self.rect.right

            # Проверка границ по Y (верхняя граница)
            if self.rect.top + dy < 0:  # Верх экрана
                dy = -self.rect.top
                self.jump_y = 0  # Сбрасываем прыжок

            # Сброс анимации при отсутствии движения на первый кадр и остановка в последнем направлении
            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT]):
                self.counter = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Прыжок, если прошло времени чем 750 мл, то прыгать можно
            if key[pygame.K_SPACE] and not self.jumped and press_time - self.last_jump_time >= self.jump_cooldown:
                self.jump_y = -15
                self.jumped = True
                self.last_jump_time = press_time
                jump_sound.play()

            if not key[pygame.K_SPACE]:
                self.jumped = False

            # Чит для прыжка
            if key[pygame.K_LCTRL] and key[pygame.K_F8]:
                self.jump_cooldown = 0

            # Анимация и ее сброс
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1

                # Если индекс превысил число допустимых кадров сбрасываем на начальный кадр
                if self.index >= len(self.images_right):
                    self.index = 0

                # В зависимости от направления движения выбираем кадр анимации
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Гравитация для прыжка
            self.jump_y += 1 # Каждый кадр добавляется 1
            if self.jump_y > 10:
                self.jump_y = 10 # Максимальная скорость падения, чтобы падал не быстро
            dy += self.jump_y

            # Проверка коллизии по x, y для блока
            for tile in world.tile_list:
                # Проверка пересечения по x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # Проверка пересечения по y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.jump_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.jump_y = 0
                    elif self.jump_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.jump_y = 0

            # Проверка коллизии с призраками
            if pygame.sprite.spritecollide(self, ghost_group, False) or pygame.sprite.spritecollide(self, ghost_group_2, False) or pygame.sprite.spritecollide(self, ghost_group_3,  False) or pygame.sprite.spritecollide(self, spike_group, False):
                sound_dead.play()
                return 0

            # Проверка коллизии с флажками
            if pygame.sprite.spritecollide(self, teleport_group, False):
                return 2

            # Обновление координат игрока
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > sc_height:
                self.rect.bottom = sc_height

        elif game_over == 0:
            self.image = self.dead_image
            self.rect.y -= 5

        # Отрисовка игрока
        screen.blit(self.image, self.rect)
        return game_over

    # Функция для рестарта
    def reset(self, x, y, speed):
        """Возвращение в начальное состояние"""
        self.__init__(x, y, speed)


class World:
    """Проверка значений в матрице мира"""
    def __init__(self, data):
        self.tile_list = []
        block_img = pygame.image.load("img/game/block1.png")
        block_img_2 = pygame.image.load("img/game/block2.png")
        # Цикл прохода по массиву и обработка значений
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:

                if tile == 1: # Если в массиве 1, то рисуется блок
                    img = pygame.transform.scale(block_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:
                    img = pygame.transform.scale(block_img_2, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                elif tile == 3:
                    ghost = Enemy(col_count * tile_size, row_count * tile_size)
                    ghost_group.add(ghost)
                elif tile == 4:
                    ghost_2 = Enemy2(col_count * tile_size, row_count * tile_size)
                    ghost_group_2.add(ghost_2)
                elif tile == 5:
                    ghost_3 = Enemy3(col_count * tile_size, row_count * tile_size)
                    ghost_group_3.add(ghost_3)
                elif tile == 6:
                    teleport = Teleport(col_count * tile_size, row_count * tile_size)
                    teleport_group.add(teleport)
                elif tile == 7:
                    spike = Spike(col_count * tile_size, row_count * tile_size)
                    spike_group.add(spike)
                elif tile == 8:
                    coin = Coin(col_count * tile_size, row_count * tile_size)
                    coin_group.add(coin)

                col_count += 1
            row_count += 1

    def draw(self):
        """Отрисовка"""
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class GameObjects(abc.ABC):
    """Абстрактный класс для всех игровых объектов"""
    @abc.abstractmethod
    def __init__(self, x, y):
        self.rect = None
        self.image = None

    def parameters(self, x, y, size_width, size_height, path):
        """Параметры для игровых объектов"""
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, (size_width, size_height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Enemy(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 40, 40, "img/game/enemy.png")
        self.move_x = 5
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_x
        self.move_counter += 1
        if self.move_counter >= 20:
            self.move_x *= -1
            self.move_counter *= -1


class Enemy2(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 80, 40, "img/game/enemy2.png")
        self.move_x = 7
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_x
        self.move_counter += 1
        if self.move_counter >= 25:
            self.move_x *= -1
            self.move_counter *= -1


class Enemy3(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 40, 80, "img/game/enemy3.png")
        self.move_x = 3
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_x
        self.move_counter += 1
        if self.move_counter >= 35:
            self.move_x *= -1
            self.move_counter *= -1


class Teleport(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 40, 42, "img/game/flag.png")


class Spike(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 40, 40, "img/game/spike.png")


class Coin(pygame.sprite.Sprite, GameObjects):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        GameObjects.__init__(self, x, y)
        self.parameters(x, y, 40, 40, "img/game/coin.png")


def load_level(): # Функция для считывания значений из файла
    with open('levels/levels.json', 'r') as file:
        data = json.load(file)
    return data['levels']

if __name__ == '__main__':
    levels = load_level()
    current_level = 0


    # Экземпляры классов
    player = Player(110, 700, 5)

    ghost_group = pygame.sprite.Group()
    teleport_group = pygame.sprite.Group()
    spike_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    ghost_group_2 = pygame.sprite.Group()
    ghost_group_3 = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()

    world = World(levels[current_level])

    restart_button = Button(500, 300, restart_img)
    start_button = Button(300, 350, start_img)
    exit_button = Button(700, 350, exit_img)
    exit_menu_button = Button(470, 400, exit_menu_img)

    run = True
    while run:  # Цикл игры
        clock.tick(fps)

        if main_menu:
            screen.blit(menu_img, (0, 0))
            authors_text = font.render('Authors - Daniil Raspopov, Ilya Saukov', True, (255, 255, 255))
            screen.blit(authors_text, (5, 690))
            if exit_button.draw_button():
                run = False
            if start_button.draw_button():
                main_menu = False

        else:
            screen.blit(fon, (0, 0))
            world.draw()

            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                take_coin.play()

            # Отрисовка
            score_text = font.render(f'{score}', True, (255, 255, 255))
            lives_text = font.render(f'{lives}', True, (255, 255, 255))
            screen.blit(score_text, (55, 10))
            screen.blit(lives_text, (140, 10))
            screen.blit(pizza_img, (0, 1))
            screen.blit(heart_lives_img, (95 ,-1))

            ghost_group.draw(screen)
            ghost_group.update()
            ghost_group_2.draw(screen)
            ghost_group_2.update()
            ghost_group_3.draw(screen)
            ghost_group_3.update()
            platform_group.draw(screen)
            platform_group.update()
            teleport_group.draw(screen)
            spike_group.draw(screen)
            coin_group.draw(screen)

            # Обработка перехода на следующий уровень
            if game_over == 2:
                teleport_sound.play()
                current_level += 1
                if current_level < len(levels):
                    # Чистка группы и загрузка следующего уровня
                    ghost_group.empty()
                    ghost_group_2.empty()
                    ghost_group_3.empty()
                    teleport_group.empty()
                    platform_group.empty()
                    spike_group.empty()
                    coin_group.empty()
                    world = World(levels[current_level])
                    player.reset(110, 700, 5)
                    game_over = 1
                else:
                    game_over = 3

            # Все уровни пройдены
            if game_over == 3:

                screen.blit(end_img, (0, 0))
                ghost_group.empty()
                ghost_group_2.empty()
                ghost_group_3.empty()
                platform_group.empty()
                teleport_group.empty()
                player.reset(100, 900, 5)

                score_number = font_large.render(f'{score}', True, (255, 255, 0))
                score_rect = score_number.get_rect(center=(600, 320))
                screen.blit(score_number, score_rect)

                # Обработка нажатия кнопки выхода в меню
                if exit_menu_button.draw_button():
                    current_level = 0
                    ghost_group.empty()
                    ghost_group_2.empty()
                    ghost_group_3.empty()
                    teleport_group.empty()
                    spike_group.empty()
                    platform_group.empty()
                    coin_group.empty()
                    world = World(levels[current_level])
                    player.reset(110, 700, 5)
                    game_over = 1
                    score = 0
                    main_menu = True
                    lives = 5

            game_over = player.movement(game_over)

            if game_over == 0: # Если проигрыш
                if restart_button.draw_button():
                    lives -= 1
                    game_over = 1
                    score = 0

                    if lives <= 0:
                        current_level = 0
                        lives = 5
                        ghost_group.empty()
                        ghost_group_2.empty()
                        ghost_group_3.empty()
                        teleport_group.empty()
                        spike_group.empty()
                        platform_group.empty()
                        coin_group.empty()
                        world = World(levels[current_level])

                    player.reset(110, 700, 5)

        for event in pygame.event.get():
             if event.type == pygame.QUIT:
                run = False

        pygame.display.update()
    pygame.quit()
