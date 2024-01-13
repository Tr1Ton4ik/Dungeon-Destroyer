import math
import os
import sys
import pygame
from random import randint

FILE_TRANSLATOR = {  # переводит чиловое значение из файла уровня в текст
    '0': 'void',
    '1': 'wall_up',
    '2': 'wall_down',
    '3': 'wall_left',
    '4': 'wall_right',
    '5': 'wall_up_left_corner',
    '6': 'wall_up_right_corner',
    '7': 'wall_down_left_corner',
    '8': 'wall_down_right_corner',
    '9': 'floor',
    'A': 'decor_free',
    'B': 'decor_collision',
    'C': 'player',
    'D': 'enemy_group1',
    'E': 'enemy_group2',
    'F': 'enemy_group3',
    'G': 'enemy_group4',
    'H': 'traps1',
    'I': 'traps2',
    'J': None,
    'K': None
}

SIZE_COLLISION = {  # константа размеров модельки игрока, врагов и т.д.
    'player': (40, 1),
    'enemy_group1': (70, 1),
    'enemy_group2': (30, 1),
    'enemy_group3': (30, 1),
    'enemy_group4': (30, 1),
    'traps1': (30, 1),
    'traps2': (30, 1),
}
ShootingEvent = pygame.USEREVENT + 1
StartLevel1 = pygame.USEREVENT + 2
BackEvent = pygame.USEREVENT + 3


def load_image_data(name: str, color_key=None):
    '''открывает изображение из папки data'''
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_image(name: str, color_key=None):
    '''открывает изображение из папки data'''
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename: str) -> list:
    '''открытие файла с уровнем из папки levels'''
    filename = "levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    max_height = len(level_map)
    return list(map(lambda x: x.ljust(max_width, '0'), level_map)), (
        max_width, max_height)


def load_image(name: str) -> list:
    '''заглушка для текстур, пока не нарисуем'''
    f = pygame.Surface((20, 20))
    f.fill(pygame.Color('white'))
    if name == 'void.png':
        pass
    elif name == 'wall_up.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(0, 10, 20, 10))
    elif name == 'wall_down.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(0, 0, 20, 10))
    elif name == 'wall_left.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(10, 0, 10, 20))
    elif name == 'wall_right.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(0, 0, 10, 20))
    elif name == 'wall_up_left_corner.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(10, 10, 10, 10))
    elif name == 'wall_up_right_corner.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(0, 10, 10, 10))
    elif name == 'wall_down_left_corner.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(10, 0, 10, 10))
    elif name == 'wall_down_right_corner.png':
        pygame.draw.rect(f, pygame.Color('black'), pygame.Rect(0, 0, 10, 10))
    elif name == 'floor1.png':
        f.fill(pygame.Color('blue'))
    elif name == 'floor2.png':
        f.fill(pygame.Color('blue'))
    elif name == 'floor3.png':
        f.fill(pygame.Color('blue'))
    elif name == 'fon.png':
        return pygame.image.load(open('data/fon.png'))

    elif name == 'player.png':
        f = pygame.Surface((40, 70), pygame.SRCALPHA)
        pygame.draw.rect(f, pygame.Color('red'), pygame.Rect(0, 0, 40, 70))

    elif name == 'decor_free1.png' or name == 'decor_free2.png' or name == 'decor_free3.png':
        f = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(f, pygame.Color('red'), (10, 10), radius=6)

    elif name == 'enemy11.png' or name == 'enemy12.png' or name == 'enemy13.png':
        f = pygame.Surface((70, 40), pygame.SRCALPHA)
        pygame.draw.rect(f, pygame.Color('red'), pygame.Rect(0, 0, 70, 40))
    return f


def cut_sheet(sheet: pygame.Surface, columns: int, rows: int):
    rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
    frames = []
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)))
    return frames


def level_render(text_level: list) -> list:
    '''прогружает открытый уровень'''
    for y in range(len(text_level)):
        for x in range(len(text_level[y])):
            value = tile_type_translate(text_level[y][x])
            if value in Spase_tile.basic_spase_textures.keys():
                '''рендер карты'''
                Spase_tile(text_level[y][x], x, y)
            elif value == 'player':
                '''рендер игрока'''
                size_collision = SIZE_COLLISION[value]
                Hero(text_level[y][x], size_collision, x, y, 100)
                player_group.sprites()[0].add_weapons(
                    [Pistol(load_image_data('pistol.png', -1),
                            2, 0)])
            elif value in Enemy_group1_tile.basic_entitys_textures.keys():
                '''рендер врагов'''
                enemy_tile_group(text_level[y][x], x, y)


class HealthBar:
    def __init__(self, screen, x, y, width, height):
        self.x, self.y, self.width, self.height, self.screen = (x, y, width,
                                                                height, screen)

    def draw(self):
        draw = pygame.draw.rect
        player = player_group.sprites()[0]
        ratio = player.hp / player.max_hp
        draw(screen, 'red', (self.x, self.y, self.width, self.height))
        draw(screen, 'green',
             (self.x, self.y, self.width * ratio, self.height))


class ScreenButton:
    def __init__(self, x, y, width, height, text, image_path,
                 hover_image_path=None, sound_path=None):
        self.x, self.y, self.width, self.height, self.text = (x, y, width,
                                                              height, text)
        # загружаю картинку кнопки
        self.image = load_image_data(image_path, -1)
        self.image = pygame.transform.scale(self.image, (width, height))
        # Загружаю подсветку при наведении
        self.hover_image = self.image
        if hover_image_path:
            self.hover_image = load_image_data(hover_image_path, -1)
            self.hover_image = pygame.transform.scale(self.hover_image,
                                                      (width, height))

        self.rect = self.image.get_rect(topleft=(x, y))
        # Загружаю звук нажатия
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def draw(self, screen):
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event, UserEvent):
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                self.is_hovered):
            if self.sound:
                self.sound.play()
            pygame.event.post(
                pygame.event.Event(UserEvent, button=self))


def start_screen() -> None:
    pygame.init()

    running_start_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    fon = pygame.transform.scale(load_image_data('start_screen.png'),
                                 (800, 800), )
    running_start_screen.blit(fon, (0, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == StartLevel1:
                running = False
                choose_level()
            button.handle_event(event, StartLevel1)
        button.check_hover(pygame.mouse.get_pos())
        button.draw(running_start_screen)
        pygame.display.flip()


def choose_level():
    pygame.init()
    choose_level_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == StartGameEvent:
                running = False
                return
            if event.type == BackEvent:
                running = False
                start_screen()
            button.handle_event(event, StartLevel1)
            back_button.handle_event(event, BackEvent)
        back_button.draw(choose_level_screen)
        back_button.check_hover(pygame.mouse.get_pos())
        button.check_hover(pygame.mouse.get_pos())
        button.draw(choose_level_screen)
        pygame.display.flip()


def terminate() -> None:
    '''закрыть окно'''
    pygame.quit()
    sys.exit()


def tile_type_translate(tile_type):
    '''переводит значение из файла в текстовое'''
    try:
        tile_type = FILE_TRANSLATOR[tile_type]
    except pygame.error as message:
        print('level file is broken')
        raise SystemExit(message)
    except KeyError:
        if tile_type not in FILE_TRANSLATOR.values():
            raise KeyError('wrong key')
    return tile_type


class Spase_tile(pygame.sprite.Sprite):
    '''класс прогрузки карты'''
    basic_spase_textures = {
        'void': load_image('void.png'),
        'wall_up': load_image('wall_up.png'),
        'wall_down': load_image('wall_down.png'),
        'wall_left': load_image('wall_left.png'),
        'wall_right': load_image('wall_right.png'),
        'wall_up_left_corner': load_image('wall_up_left_corner.png'),
        'wall_up_right_corner': load_image('wall_up_right_corner.png'),
        'wall_down_left_corner': load_image('wall_down_left_corner.png'),
        'wall_down_right_corner': load_image('wall_down_right_corner.png'),
        'floor': [load_image('floor1.png'), load_image('floor2.png'),
                  load_image('floor3.png')],
        'decor_free': [load_image('decor_free1.png'),
                       load_image('decor_free2.png'),
                       load_image('decor_free3.png')],
    }

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(spase_group, all_sprites_group)
        tile_type = tile_type_translate(tile_type)
        self.add_group(tile_type, pos_x, pos_y)
        self.make_texture(tile_type, pos_x, pos_y)

    def add_group(self, tile_type, pos_x, pos_y):
        '''добавляет в необходимую групу'''
        if tile_type[:4] == 'void':
            void_spase_group.add(self)
        elif tile_type[:5] == 'decor':
            decor_group.add(self)
            Spase_tile('floor', pos_x, pos_y)
        elif tile_type[:4] == 'wall':
            '''добавление в группу стен для колизии существ'''
            walls_group.add(self)
            if tile_type[5:] == 'up':
                walls_group_up.add(self)
            elif tile_type[5:] == 'down':
                walls_group_down.add(self)
            elif tile_type[5:] == 'left':
                walls_group_left.add(self)
            elif tile_type[5:] == 'right':
                walls_group_right.add(self)

    def make_texture(self, tile_type, pos_x, pos_y):
        '''загружает текстуру объекта'''
        image = self.basic_spase_textures[tile_type]
        self.image = pygame.transform.scale(
            image if not isinstance(image, list) else image[
                randint(0, len(image) - 1)], (tile_width, tile_height))
        pygame.draw.line(self.image, pygame.Color('black'), (tile_width, 0),
                         (tile_width, tile_height),
                         3)  # метка клеток, потом удалить
        pygame.draw.line(self.image, pygame.Color('black'), (0, tile_height),
                         (tile_width, tile_height),
                         3)  # метка клеток, потом удалить
        pygame.draw.circle(self.image, pygame.Color('black'),
                           (0.5 * tile_width, 0.5 * tile_height),
                           1)  # метка клеток, потом удалить
        self.rect = pygame.Rect(tile_width * pos_x, tile_height * pos_y,
                                tile_width, tile_height)


class Entity_tile(pygame.sprite.Sprite):
    '''родительский класс существ(игрока, врагов и т.д.)'''
    basic_entitys_textures = {
        'player': load_image('player.png'),
        'enemy_group1': [load_image('enemy11.png'), load_image('enemy12.png'),
                         load_image('enemy13.png')],
        'enemy_group2': [load_image('enemy21.png'), load_image('enemy22.png'),
                         load_image('enemy23.png')],
        'enemy_group3': [load_image('enemy31.png'), load_image('enemy32.png'),
                         load_image('enemy33.png')],
        'enemy_group4': [load_image('enemy41.png'), load_image('enemy42.png'),
                         load_image('enemy43.png')],
        'traps1': [load_image('trap11.png'), load_image('trap12.png'),
                   load_image('trap13.png')],
        'traps2': [load_image('trap21.png'), load_image('trap22.png'),
                   load_image('trap23.png')]
    }

    class Entity_image(pygame.sprite.Sprite):
        '''текстурка существа отдельная от модельки'''

        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(entity_image_group, entity_group,
                             all_sprites_group)
            entity_image = Entity_tile.basic_entitys_textures[tile_type]
            self.image = entity_image if not isinstance(entity_image,
                                                        list) else \
                entity_image[randint(0, len(entity_image) - 1)]
            self.rect = self.image.get_rect().move(int(tile_width * (
                    pos_x + 0.5) - self.image.get_rect().width * 0.5),
                                                   int(tile_height * (
                                                           pos_y + 1) - self.image.get_rect().height))

    def __init__(self, tile_type: str, size_collision: list, pos_x: str,
                 pos_y: str, max_hp: int):
        '''загрузка модельки и тектуры, отдельно'''
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y)
        self.max_hp = max_hp
        self.hp = max_hp

    def make_model(self, tile_type, size_collision, pos_x, pos_y):
        '''загружает текстуру и модельку объекта'''
        self.entity_image = self.Entity_image(tile_type, pos_x, pos_y)
        super().__init__(entity_group, all_sprites_group)
        Spase_tile('floor', pos_x, pos_y)
        self.image = pygame.Surface(size_collision, pygame.SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color('green'), pygame.Rect(0, 0,
                                                                        *size_collision))  # заглушка для модельки, чтобы было видно
        self.rect = self.image.get_rect().move(int(tile_width * (
                pos_x + 0.5) - self.image.get_rect().width * 0.5),
                                               int(tile_height * (
                                                       pos_y + 1 - self.image.get_rect().height * 0.3) - self.image.get_rect().height))

    def attack(self):
        pass


class Player_group_tile(Entity_tile):
    '''класс реализующий игрока'''

    def __init__(self, tile_type: str, size_collision: list, pos_x: str,
                 pos_y: str, max_hp: int):
        self.max_hp = max_hp
        self.hp = max_hp
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y)
        player_group.add(self)

    def update(self, tick, keys):
        '''перемещение игрока'''
        move = [0, 0]
        if keys[pygame.K_UP]:
            move[1] -= int(player_speed * tick + 1) // (sum(keys) + 1) ** 0.5
        if keys[pygame.K_DOWN]:
            move[1] += int(player_speed * tick + 1) // (sum(keys) + 1) ** 0.5
        if keys[pygame.K_LEFT]:
            move[0] -= int(player_speed * tick + 1) // (sum(keys) + 1) ** 0.5
        if keys[pygame.K_RIGHT]:
            move[0] += int(player_speed * tick + 1) // (sum(keys) + 1) ** 0.5
        self.rect = self.rect.move(*move)
        self.entity_image.rect = self.entity_image.rect.move(*move)
        if pygame.sprite.spritecollideany(self, walls_group):
            move = (-move[0], -move[1])
            self.rect = self.rect.move(*move)
            self.entity_image.rect = self.entity_image.rect.move(*move)

    def attack(self):
        pass


class Enemy_group1_tile(Entity_tile):
    '''класс реализующий 1 группу врагов'''

    def __init__(self, tile_type, size_collision, pos_x, pos_y):
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y)
        enemy_group.add(self.entity_image, self)
        enemy_image_group.add(self.entity_image)

    def update(self, tick):
        '''передвижение врагов, работает хреново'''
        player = player_group.sprites()[0]
        pos_player_center = (player.rect.x + player.rect.width * 0.5,
                             player.rect.y + player.rect.height * 0.5)
        pos_enemy_center = (self.rect.x + self.rect.width * 0.5,
                            self.rect.y + self.rect.height * 0.5)
        pos_delta = (pos_player_center[0] - pos_enemy_center[0],
                     pos_player_center[1] - pos_enemy_center[1])
        distance = ((pos_delta[0]) ** 2 + (pos_delta[1]) ** 2) ** 0.5
        try:
            pos_delta = (pos_delta[0] / distance, pos_delta[1] / distance)
            move = (int(tick * enemy_speed + 1) * pos_delta[0],
                    int(tick * enemy_speed + 1) * pos_delta[1])
            # if distance <= 15: print('connect')
            self.rect = self.rect.move(*move)
            self.entity_image.rect = self.entity_image.rect.move(*move)
        except ZeroDivisionError:
            pass
        except pygame.error as message:
            print('position error')
            raise SystemExit(message)


def enemy_tile_group(tile_tipe: str, x: str, y: str) -> None:
    '''подберает нужний класс врага'''
    value = tile_type_translate(tile_tipe)
    size_collision = SIZE_COLLISION[value]
    if value == 'enemy_group1': Enemy_group1_tile(tile_tipe, size_collision, x,
                                                  y)
    # elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group2': Enemy_group2_tile(x, y)
    # elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group3': Enemy_group3_tile(x, y)
    # elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group4': Enemy_group4_tile(x, y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Hero(Player_group_tile):
    '''Класс мушкетера за которого можно играть'''

    def __init__(self, tile_type, size_collision, pos_x, pos_y, max_hp):
        super().__init__(tile_type, size_collision, pos_x, pos_y, max_hp)
        self.weapons = []
        self.now_weapon = None

    def attack(self, mouse_x, mouse_y):
        self.now_weapon.attack(mouse_x, mouse_y)

    def add_weapons(self, weapons: list):
        self.weapons += weapons
        self.now_weapon = self.weapons[0]


class Weapon(pygame.sprite.Sprite):
    '''Класс оружия'''

    def __init__(self, image: pygame.Surface, count: int, damage):
        super().__init__(weapon_group, all_sprites_group)
        player = player_group.sprites()[0].rect
        x, y = player.x, player.y

        self.damage = damage
        self.rect = pygame.Rect(x, y, *image.get_size())
        self.image = image

        self.frames = cut_sheet(self.image, count, 1)
        self.image = self.frames[0]
        self.original_image = self.image = pygame.transform.scale(self.image,
                                                                  (30, 30))

    def update(self, *args, **kwargs):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player = player_group.sprites()[0].rect
        x, y = player.x, player.y
        self.rect.x = x
        self.rect.y = y
        angle = math.degrees(math.atan2(mouse_y - self.rect.y, mouse_x -
                                        self.rect.x))
        if angle < 0:
            angle += 360
        self.image = pygame.transform.rotate(self.original_image, -angle + 180)


class Pistol(Weapon):
    def __init__(self, image, count, damage):
        super().__init__(image, count, damage)

    def attack(self, mouse_x, mouse_y):
        Bullet(mouse_x, mouse_y, self.damage)


class Bullet(pygame.sprite.Sprite):
    '''Класс пули'''

    def __init__(self, mouse_x: int, mouse_y: int, damage: int):
        super().__init__(all_sprites_group, bullets_group)
        self.damage = damage
        weapon = player_group.sprites()[0].now_weapon.rect
        x, y = weapon.x + weapon.w//2, weapon.y + weapon.h//2
        # Нахожу угол траектории полета
        self.angle = math.atan2(mouse_y - y, mouse_x - x)
        self.image = load_image_data('bullet.png')
        self.rect = pygame.Rect(x, y,
                                self.image.get_width(),
                                self.image.get_height())

    def update(self, *args, **kwargs):
        # Скорость взависимости от угла
        self.rect.x += round(BULLET_SPEED * math.cos(self.angle))
        self.rect.y += round(BULLET_SPEED * math.sin(self.angle))
        # Пересечение с игроком или препятствиями
        collide = pygame.sprite.spritecollideany
        if collide(self, enemy_group) or collide(self, walls_group):
            self.kill()


if __name__ == '__main__':
    pygame.init()
    FPS = 60
    FOV = (10, 10)
    tile_width = tile_height = 80
    player_speed = 180
    enemy_speed = 80
    speed_up = speed_down = speed_left = speed_right = 180
    BULLET_SPEED = 10

    pygame.key.set_repeat(1, 50)

    all_sprites_group = pygame.sprite.Group()
    entity_group = pygame.sprite.Group()
    entity_image_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    enemy_image_group = pygame.sprite.Group()
    spase_group = pygame.sprite.Group()
    decor_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    walls_group_up = pygame.sprite.Group()
    walls_group_down = pygame.sprite.Group()
    walls_group_left = pygame.sprite.Group()
    walls_group_right = pygame.sprite.Group()
    void_spase_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    weapon_group = pygame.sprite.Group()

    loaded_level = load_level('level_test1.txt')

    size_display = WIDTH, HEIGHT = FOV[0] * tile_width, FOV[1] * tile_height
    size_screen = (
        tile_width * loaded_level[1][0], tile_height * loaded_level[1][1])

    display = pygame.display.set_mode(size_display)
    screen = pygame.Surface(size_screen)
    map = pygame.Surface(size_screen)

    button = ScreenButton(WIDTH // 2 - 50, 100, 100, 100, '1 уровень',
                          'button.png', 'button_hover.png',
                          'data/click.mp3')
    back_button = ScreenButton(0, 0, 100, 100, 'Назад',
                               'button.png', 'button_hover.png',
                               'data/click.mp3')

    level_render(loaded_level[0])
    spase_group.draw(map)
    decor_group.draw(map)

    ShootingEvent = pygame.USEREVENT + 1
    StartGameEvent = pygame.USEREVENT + 2

    clock = pygame.time.Clock()
    running = True
    shooting = True
    start_screen()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(num_buttons=3)[0]:
                    if shooting:
                        pygame.time.set_timer(ShootingEvent, 250)
                        shooting = False
                    elif not shooting:
                        pygame.time.set_timer(ShootingEvent, 0)
                        shooting = True
            if event.type == ShootingEvent:
                player_group.sprites()[0].attack(*pygame.mouse.get_pos())
            if event.type == BackEvent:
                choose_level()
            back_button.handle_event(event, BackEvent)
        keys = pygame.key.get_pressed()
        if any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT],
                keys[pygame.K_RIGHT]]):
            player_group.update(clock.get_time() / 1000, keys)
            weapon_group.update()
        enemy_group.update(clock.get_time() / 1000)

        screen.blit(map, (0, 0))
        bullets_group.draw(screen)
        bullets_group.update()
        entity_group.draw(screen)
        walls_group_down.draw(screen)
        weapon_group.draw(screen)
        weapon_group.update()
        back_button.draw(screen)
        back_button.check_hover(pygame.mouse.get_pos())
        display.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
    terminate()
