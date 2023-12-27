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
    '''заглушка для текстурЮ пока не нарисуем'''
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
    elif name == 'player.png':
        f = pygame.Surface((40, 70), pygame.SRCALPHA)
        pygame.draw.rect(f, pygame.Color('red'), pygame.Rect(0, 0, 40, 70))
    elif name == 'fon.png':
        return pygame.image.load(open('data/fon.png'))
    return f


def level_render(text_level: list) -> list:
    '''прогружает открытый уровень'''
    new_player = entitys = x = y = None
    for y in range(len(text_level)):
        for x in range(len(text_level[y])):
            value = FILE_TRANSLATOR[text_level[y][x]]
            if value in Spase_tile.basic_spase_textures.keys():
                Spase_tile(text_level[y][x], x, y)  # рендер карты
            # elif FILE_TRANSLATOR[text_level[y][x]] in ['D', 'E', 'F', 'G']: entity_tile_group(text_level[y][x], x, y)  # рендер врагов
            elif value in ['player']:
                Entity_tile(text_level[y][x], (40, 1), x,
                            y)  # рендер игрока карты
                # вернем игрока, а также размер поля в клетках
                Bullet(0, 0, 10, 10, 0)
    return new_player, entitys, x, y


def start_screen() -> None:
    '''стартовое окно'''
    intro_text = ["ЗАСТАВКА",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    display.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()
        text_coord += 2
        intro_rect.y = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        display.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def terminate() -> None:
    '''закрыть окно'''
    pygame.quit()
    sys.exit()


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
        'decor_collision': [load_image('decor_collision1.png'),
                            load_image('decor_collision2.png'),
                            load_image('decor_collision3.png')],
    }

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(spase_group, all_sprites_group)
        try:
            tile_type = FILE_TRANSLATOR[tile_type]

        except pygame.error as message:
            print('level file is broken')
            raise SystemExit(message)
        except KeyError:
            if tile_type not in FILE_TRANSLATOR.values():
                raise KeyError('wrong key')

        if tile_type[:4] == 'wall':
            '''группа стен для колизии существ'''
            walls_group.add(self)
            if tile_type[5:] == 'up':
                walls_group_up.add(self)
            elif tile_type[5:] == 'down':
                walls_group_down.add(self)
            elif tile_type[5:] == 'left':
                walls_group_left.add(self)
            elif tile_type[5:] == 'right':
                walls_group_right.add(self)
            print(tile_type[5:])

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
                    pos_x + 0.5) - entity_image.get_rect().width * 0.5),
                                                   int(tile_height * (
                                                           pos_y + 1) - entity_image.get_rect().height))

    def __init__(self, tile_type: str, size_collision: list, pos_x: str,
                 pos_y: str):
        '''загрузка модельки и тектуры, отдельно'''
        try:
            tile_type = FILE_TRANSLATOR[tile_type]
        except pygame.error as message:
            if tile_type not in FILE_TRANSLATOR.keys():
                print('level file is broken')
                raise SystemExit(message)
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

    def update(self, tick, *args, **kwargs):
        key = args[0]
        move = (0, 0)
        if key[pygame.K_UP]:
            move = (0, -int(speed_up * tick + 1))
        if key[pygame.K_DOWN]:
            move = (0, +int(speed_down * tick + 1))
        if key[pygame.K_LEFT]:
            move = (-int(speed_left * tick + 1), 0)
        if key[pygame.K_RIGHT]:
            move = (+int(speed_right * tick + 1), 0)
        self.rect = self.rect.move(*move)
        self.entity_image.rect = self.entity_image.rect.move(*move)
        if pygame.sprite.spritecollideany(self, walls_group):
            move = (-move[0], -move[1])
            self.rect = self.rect.move(*move)
            self.entity_image.rect = self.entity_image.rect.move(*move)


class MainHero(Entity_tile):
    pass


#
# def entity_tile_group(tile_tipe: str, x: str, y: str) -> None:
#     if FILE_TRANSLATOR[tile_tipe] == 'enemy_group1': Enemy_group1_tile(x, y)
#     elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group2': Enemy_group2_tile(x, y)
#     elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group3': Enemy_group3_tile(x, y)
#     elif FILE_TRANSLATOR[tile_tipe] == 'enemy_group4': Enemy_group4_tile(x, y)


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, delta_x: int, delta_y: int, damage: int):
        super().__init__(all_sprites_group, bullets_group)
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
        self.x, self.y = (delta_x // distance) * BULLET_SPEED, (
                delta_y // distance * BULLET_SPEED)
        self.damage = damage
        self.image = load_image_data('bullet.png')
        self.rect = self.image.get_rect()

    def update(self, *args, **kwargs):
        self.rect = self.rect.move(self.x, self.y)
        if pygame.sprite.spritecollide(self, walls_group, dokill=0):
            self.kill()


if __name__ == '__main__':
    pygame.init()
    FPS = 50
    FOV = (10, 10)
    tile_width = tile_height = 80
    speed_up = speed_down = speed_left = speed_right = 180
    BULLET_SPEED = 10

    pygame.key.set_repeat(1, 50)

    pygame.sprite.Sprite()
    all_sprites_group = pygame.sprite.Group()
    entity_group = pygame.sprite.Group()
    entity_image_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    spase_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    walls_group_up = pygame.sprite.Group()
    walls_group_down = pygame.sprite.Group()
    walls_group_left = pygame.sprite.Group()
    walls_group_right = pygame.sprite.Group()
    void_spase_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()

    loaded_level = load_level('level_test1.txt')

    size_display = WIDTH, HEIGHT = FOV[0] * tile_width, FOV[1] * tile_height
    size_screen = (
        tile_width * loaded_level[1][0], tile_height * loaded_level[1][1])

    display = pygame.display.set_mode(size_display)
    screen = pygame.Surface(size_screen)
    screen2 = pygame.Surface(size_screen)
    map = pygame.Surface(size_screen)
    clock = pygame.time.Clock()
    running = True
    start_screen()
    level_render(loaded_level[0])
    spase_group.draw(map)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                entity_group.update(clock.get_time() / 1000,
                                    pygame.key.get_pressed())
        display.fill(pygame.Color("black"))
        screen.blit(map, (0, 0))
        bullets_group.draw(screen)
        bullets_group.update()
        entity_group.draw(screen)
        walls_group_down.draw(screen)
        display.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
    terminate()
