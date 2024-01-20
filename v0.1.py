import math
import os
import sys
import pygame
from random import randint

FPS = 60
FPS_entity_swap = 8
FOV = (10, 10)
tile_width = tile_height = 80
player_speed = 180
enemy_speed = 80
BULLET_SPEED = 10
size_display = WIDTH, HEIGHT = FOV[0] * tile_width, FOV[1] * tile_height
display = pygame.display.set_mode(size_display)
monsters_can_attack_list = []

pygame.init()
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
SIZE_SPRITE = {  # кол. строк и столбов у спрайта игрока, врагов и т.д.
    'player': (3, 1),
    'enemy_group1': (1, 1),
    'enemy_group2': (1, 1),
    'enemy_group3': (1, 1),
    'enemy_group4': (1, 1),
    'traps1': (1, 1),
    'traps2': (1, 1),
}

ShootingEvent = pygame.USEREVENT + 1
StartLevel1 = pygame.USEREVENT + 2
BackEvent = pygame.USEREVENT + 3
ENTITYIMAGESWAP = pygame.USEREVENT + 4
ChooseLevelEvent = pygame.USEREVENT + 5
DeleteAllAfterSwordEvent = pygame.USEREVENT + 6
AcceptAttackEvent = pygame.USEREVENT + 7
StaminaRecoveryEvent = pygame.USEREVENT + 8
ReloadPistolEvent = pygame.USEREVENT + 9
RecoveryEnemyAttack = pygame.USEREVENT + 10
DeleteEnemyEffects = pygame.USEREVENT + 11


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


def load_image(name: str, actual=False) -> list:
    '''заглушка для текстур, пока не нарисуем'''
    if actual:
        return load_image_data(name)
    tile_width = tile_height = 80
    f = pygame.Surface((tile_width, tile_height))
    w = tile_width
    h = tile_height
    f.fill(pygame.Color('white'))
    if name == 'void.png':
        pass
    elif name == 'wall_up.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(0, h * 0.5, w, h * 0.5))
    elif name == 'wall_down.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(0, 0, w, h * 0.5))
    elif name == 'wall_left.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(w * 0.5, 0, w * 0.5, h))
    elif name == 'wall_right.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(0, 0, w * 0.5, h))
    elif name == 'wall_up_left_corner.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(w * 0.5, h * 0.5, w * 0.5, h * 0.5))
    elif name == 'wall_up_right_corner.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(0, h * 0.5, w * 0.5, h * 0.5))
    elif name == 'wall_down_left_corner.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(w * 0.5, 0, w * 0.5, h * 0.5))
    elif name == 'wall_down_right_corner.png':
        pygame.draw.rect(f, pygame.Color('black'),
                         pygame.Rect(0, 0, w * 0.5, h * 0.5))
    elif name == 'floor1.png' or name == 'floor2.png' or name == 'floor3.png':
        f.fill(pygame.Color('blue'))
    elif name == 'fon.png':
        return pygame.image.load(open('data/fon.png'))

    elif name == 'player.png':
        f = pygame.Surface((40 * 3, 70), pygame.SRCALPHA)
        pygame.draw.rect(f, pygame.Color('red'), pygame.Rect(0, 0, 40, 70))
        pygame.draw.rect(f, pygame.Color('green'), pygame.Rect(40, 0, 40, 70))
        pygame.draw.rect(f, pygame.Color('white'), pygame.Rect(80, 0, 40, 70))

    elif name == 'decor_free1.png' or name == 'decor_free2.png' or name == 'decor_free3.png':
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(f, pygame.Color('red'), (w * 0.5, h * 0.5),
                           radius=w * 0.3)

    elif name == 'decor_collision1.png' or name == 'decor_collision2.png' or name == 'decor_collision3.png':
        f = pygame.Surface((w * 0.5, h * 0.5))
        f.fill(pygame.Color('red'))

    elif name == 'enemy11.png' or name == 'enemy12.png' or name == 'enemy13.png':
        f = pygame.Surface((70, 40), pygame.SRCALPHA)
        pygame.draw.rect(f, pygame.Color('red'), pygame.Rect(0, 0, 70, 40))
    return f


def terminate() -> None:
    '''закрыть окно'''
    pygame.quit()
    sys.exit()


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
                load = load_image_data
            elif value in Enemy_group1_tile.basic_entitys_textures.keys():
                '''рендер врагов'''
                enemy_tile_group(text_level[y][x], x, y)


class Bar:

    def __init__(self, screen, x, y, width, height):
        self.x, self.y, self.width, self.height, self.screen = (x, y, width,
                                                                height, screen)

    def draw(self):
        pass


class StaminaBar(Bar):
    max_stamina = 10

    def __init__(self, screen, x, y, width, height):
        super().__init__(screen, x, y, width, height)
        self.stamina = self.max_stamina

    def draw(self):
        draw = pygame.draw.rect
        ratio = self.stamina / self.max_stamina
        draw(self.screen, 'grey', (self.x, self.y, self.width, self.height))
        draw(self.screen, 'blue',
             (self.x, self.y, self.width * ratio, self.height))
        draw(self.screen, 'black',
             (self.x, self.y, self.width * ratio, self.height), width=1)


class HealthBar(Bar):
    def __init__(self, screen, x, y, width, height):
        super().__init__(screen, x, y, width, height)

    def draw(self):
        draw = pygame.draw.rect
        player = player_group.sprites()[0]
        ratio = player.hp / player.max_hp
        draw(self.screen, 'red', (self.x, self.y, self.width, self.height))
        draw(self.screen, 'green',
             (self.x, self.y, self.width * ratio, self.height))
        draw(self.screen, 'black',
             (self.x, self.y, self.width * ratio, self.height), width=1)


class BulletsCounter:
    max_ammo = 30

    def __init__(self, screen, x, y):
        self.x, self.y, self.screen = x, y, screen
        self.ammo = self.max_ammo

    def draw(self):
        font = pygame.font.Font(None, 50)
        text = font.render(f'{self.ammo}/{self.max_ammo}', True, (0, 0, 0))
        self.screen.blit(text, (self.x, self.y))


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
    running_start_screen = True
    button = ScreenButton(10, 190, 100, 100, 'Играть',
                          'button.png', 'emptybutton_hover.png',
                          'data/click.mp3')
    fon = pygame.transform.scale(load_image_data('start_screen.png'),
                                 size_display)
    display.blit(fon, (0, 0))
    while running_start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_start_screen = False
                terminate()
            if event.type == ChooseLevelEvent:
                running_start_screen = False
                choose_level()

            button.handle_event(event, ChooseLevelEvent)
        button.check_hover(pygame.mouse.get_pos())
        button.draw(display)
        pygame.display.flip()
        clock.tick(FPS)


def choose_level():
    running_choose_level = True
    button = ScreenButton(10, 190, 130, 100, '1 уровень',
                          'button.png', 'emptybutton_hover.png',
                          'data/click.mp3')
    back_button = ScreenButton(0, 0, 100, 60, 'Назад',
                               'button.png', 'emptybutton_hover.png',
                               'data/click.mp3')
    fon = pygame.transform.scale(load_image_data('level_menu.png'),
                                 size_display)
    display.blit(fon, (0, 0))
    while running_choose_level:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_choose_level = False
                terminate()
            if event.type == StartLevel1:
                main()
            if event.type == BackEvent:
                running_choose_level = False
                start_screen()
                main()
            button.handle_event(event, StartLevel1)
            back_button.handle_event(event, BackEvent)
        back_button.draw(display)
        back_button.check_hover(pygame.mouse.get_pos())
        button.check_hover(pygame.mouse.get_pos())
        button.draw(display)

        pygame.display.flip()
        clock.tick(FPS)


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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(all_sprites_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


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
        tile_type = tile_type_translate(tile_type)
        self.add_group(tile_type, pos_x, pos_y)
        self.make_texture(tile_type, pos_x, pos_y)
        if self in decor_collision_group:
            rect = self.image.get_rect()
            self.rect = pygame.Rect(
                tile_width * (pos_x + 0.5) - rect.width * 0.5,
                tile_height * (pos_y + 0.5) - rect.height * 0.5, rect.width,
                rect.height)

    def add_group(self, tile_type, pos_x, pos_y):
        '''добавляет в необходимую групу'''
        if tile_type[:4] == 'void':
            void_spase_group.add(self)
        elif tile_type[:5] == 'decor':
            Spase_tile('floor', pos_x, pos_y)
            if tile_type[6:] == 'free':
                decor_free_group.add(self)
            elif tile_type[6:] == 'collision':
                decor_collision_group.add(self)
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
        self.image = image if not isinstance(image, list) else image[
            randint(0, len(image) - 1)]
        pygame.draw.line(self.image, pygame.Color('black'),
                         (tile_width, 0),
                         (tile_width, tile_height),
                         3)  # метка клеток, потом удалить
        pygame.draw.line(self.image, pygame.Color('black'),
                         (0, tile_height),
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
        'enemy_group1': [load_image('enemy11.png'),
                         load_image('enemy12.png'),
                         load_image('enemy13.png')],
        'enemy_group2': [load_image('enemy21.png'),
                         load_image('enemy22.png'),
                         load_image('enemy23.png')],
        'enemy_group3': [load_image('enemy31.png'),
                         load_image('enemy32.png'),
                         load_image('enemy33.png')],
        'enemy_group4': [load_image('enemy41.png'),
                         load_image('enemy42.png'),
                         load_image('enemy43.png')],
        'traps1': [load_image('trap11.png'), load_image('trap12.png'),
                   load_image('trap13.png')],
        'traps2': [load_image('trap21.png'), load_image('trap22.png'),
                   load_image('trap23.png')]
    }

    class Entity_image(pygame.sprite.Sprite):
        '''текстурка существа отдельная от модельки'''

        def __init__(self, tile_type, pos_x, pos_y, max_hp: int,
                     entity_type=None):
            super().__init__(entity_image_group, entity_group,
                             all_sprites_group)
            self.max_hp = max_hp
            self.hp = max_hp
            entity_image = Entity_tile.basic_entitys_textures[tile_type]
            entity_image = entity_image if not isinstance(entity_image,
                                                          list) else \
                entity_image[randint(0, len(entity_image) - 1)]
            self.image_group = AnimatedSprite(entity_image,
                                              *SIZE_SPRITE.get(entity_type,
                                                               (1, 1)))
            self.image = self.image_group.image
            self.rect = self.image.get_rect().move(int(tile_width * (
                    pos_x + 0.5) - self.image.get_rect().width * 0.5),
                                                   int(tile_height * (
                                                           pos_y + 1) - self.image.get_rect().height))

    def __init__(self, tile_type: str, size_collision: list, pos_x: str,
                 pos_y: str, max_hp: int):
        '''загрузка модельки и тектуры, отдельно'''
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y, max_hp,
                        entity_type)

    def make_model(self, tile_type, size_collision, pos_x, pos_y, max_hp,
                   entity_type):
        '''загружает текстуру и модельку объекта'''
        self.entity_image = self.Entity_image(tile_type, pos_x, pos_y, max_hp,
                                              entity_type)
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
    entity_type = 'player'

    def __init__(self, tile_type: str, size_collision: list, pos_x: str,
                 pos_y: str, max_hp: int):
        self.max_hp = max_hp
        self.hp = max_hp
        self.move = [0, 0]
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y, max_hp,
                        self.entity_type)
        player_group.add(self)
        player_image_group.add(self.entity_image)

    def update(self, tick, **kwargs):
        '''перемещение игрока'''
        keys = pygame.key.get_pressed()

        def move_def():
            move = [int(self.move[0]), int(self.move[1])]
            self.move = [self.move[0] - move[0], self.move[1] - move[1]]
            self.rect = self.rect.move(*move)
            self.entity_image.rect = self.entity_image.rect.move(*move)
            if pygame.sprite.spritecollideany(self,
                                              walls_group) or pygame.sprite.spritecollideany(
                self, decor_collision_group):
                move = (-move[0], -move[1])
                self.rect = self.rect.move(*move)
                self.entity_image.rect = self.entity_image.rect.move(*move)

        if kwargs.get('image_swap', False):
            self.entity_image.image_group.update()
            self.entity_image.image = self.entity_image.image_group.image
            return
        if keys[pygame.K_UP]:
            self.move[1] -= int(player_speed * tick + 1) / (
                    (sum(keys) + 1) % 2 + 1) ** 0.5
            move_def()
        if keys[pygame.K_DOWN]:
            self.move[1] += int(player_speed * tick + 1) / (
                    (sum(keys) + 1) % 2 + 1) ** 0.5
            move_def()
        if keys[pygame.K_LEFT]:
            self.move[0] -= int(player_speed * tick + 1) / (
                    (sum(keys) + 1) % 2 + 1) ** 0.5
            move_def()
        if keys[pygame.K_RIGHT]:
            self.move[0] += int(player_speed * tick + 1) / (
                    (sum(keys) + 1) % 2 + 1) ** 0.5
            move_def()
        if self.hp <= 0:
            self.kill()

    def attack(self, mouse_x, mouse_y, damage):
        pass


class Enemy_group1_tile(Entity_tile):
    '''класс реализующий 1 группу врагов'''
    entity_type = 'enemy_group1'

    def __init__(self, tile_type, size_collision, pos_x, pos_y, max_hp: int):

        self.move = (0, 0)
        tile_type = tile_type_translate(tile_type)
        self.make_model(tile_type, size_collision, pos_x, pos_y, max_hp,
                        self.entity_type)
        self.entity_image.hp = 30
        enemy_group.add(self.entity_image, self)
        enemy_image_group.add(self.entity_image)
        self.weapon = Mace(self, load_image_data('bulava.png', -1), 1)

    def update(self, tick):
        '''передвижение врагов, работает хреново'''
        try:
            player = player_group.sprites()[0]
        except:
            choose_level()
        pos_player_center = (player.rect.x + player.rect.width * 0.5,
                             player.rect.y + player.rect.height * 0.5)
        pos_enemy_center = (self.rect.x + self.rect.width * 0.5,
                            self.rect.y + self.rect.height * 0.5)
        pos_delta = (pos_player_center[0] - pos_enemy_center[0],
                     pos_player_center[1] - pos_enemy_center[1])
        distance = ((pos_delta[0]) ** 2 + (pos_delta[1]) ** 2) ** 0.5
        try:
            pos_delta = (pos_delta[0] / distance * tick * enemy_speed,
                         pos_delta[1] / distance * tick * enemy_speed)
            self.move = (
                self.move[0] + pos_delta[0], self.move[1] + pos_delta[1])
            move = (int(self.move[0]), int(self.move[1]))
            self.move = (self.move[0] - move[0], self.move[1] - move[1])
            self.rect = self.rect.move(*move)
            self.entity_image.rect = self.entity_image.rect.move(*move)
            if pygame.sprite.spritecollideany(self.entity_image,
                                              player_image_group): pass
        except ZeroDivisionError:
            pass
        except pygame.error as message:
            print('position error')
            raise SystemExit(message)

        if self.entity_image.hp <= 0:
            self.entity_image.kill()
            self.kill()
        r = self.rect
        weapon = self.weapon
        Check_player(r.x + r.w // 2 // 2, r.y + 32, 32, 32, weapon)
        Check_player(r.x + r.w // 2 // 2, r.y - 32, 32, 32, weapon)
        Check_player(r.x + r.w // 2 // 2 + 32, r.y, 32, 32, weapon)
        Check_player(r.x + r.w // 2 // 2 - 32, r.y, 32, 32, weapon)


def enemy_tile_group(tile_tipe: str, x: str, y: str) -> None:
    '''подберает нужний класс врага'''
    value = tile_type_translate(tile_tipe)
    size_collision = SIZE_COLLISION[value]
    if value == 'enemy_group1': Enemy_group1_tile(tile_tipe, size_collision, x,
                                                  y, 30)
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
        load = load_image_data
        self.now_weapon = Pistol(load('pistol.png', -1), 10)
        weapon_group.add(self.now_weapon)

    def attack(self, mouse_x, mouse_y):
        self.now_weapon.attack(mouse_x, mouse_y)

    def change_weapon(self):
        load = load_image_data
        if type(self.now_weapon) == Pistol:
            weapon_pic = load('sword.png', -1)
            self.now_weapon = Sword(weapon_pic, 10)
        else:
            weapon_pic = load('pistol.png', -1)
            self.now_weapon = Pistol(weapon_pic, 10)
        weapon_group.sprites()[0].kill()
        weapon_group.add(self.now_weapon)


class Effect(pygame.sprite.Sprite):
    def __init__(self, angle: float, image_name):
        super().__init__(all_sprites_group, effects_group)
        self.image = load_image_data(image_name, -1)
        sword = weapon_group.sprites()[0].rect
        s_x, s_y = sword.x, sword.y
        if 270 >= angle >= 90:
            self.image = pygame.transform.rotate(
                pygame.transform.flip(self.image, flip_x=1, flip_y=0),
                angle - 180)
        else:
            self.image = pygame.transform.rotate(self.image,
                                                 angle)
        if 230 <= angle <= 270:
            self.rect = pygame.Rect(s_x, s_y - 32, 32, 32)
        elif 90 <= angle <= 148:
            self.rect = pygame.Rect(s_x, s_y + 32, 32, 32)
        elif 90 <= angle <= 270:
            self.rect = pygame.Rect(s_x + 32, s_y, 32, 32)
        else:
            self.rect = pygame.Rect(s_x - 32, s_y, 32, 32)

    def update(self, *args, **kwargs):
        if len(effects_group.sprites()) > 1:
            self.kill()


class Slash(pygame.sprite.Sprite):
    def __init__(self, angle: float, damage: int):
        super().__init__(slash_group, all_sprites_group)
        self.damage = damage
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        sword = weapon_group.sprites()[0].rect
        s_x, s_y = sword.x, sword.y
        if 230 <= angle <= 270:
            self.rect = pygame.Rect(s_x, s_y - 32, 32, 32)
        elif 90 <= angle <= 148:
            self.rect = pygame.Rect(s_x, s_y + 32, 32, 32)
        elif 90 <= angle <= 270:
            self.rect = pygame.Rect(s_x + 32, s_y, 32, 32)
        else:
            self.rect = pygame.Rect(s_x - 32, s_y, 32, 32)

    def update(self, *args, **kwargs):
        collide = pygame.sprite.spritecollideany
        if collide(self, enemy_group):
            collide(self, enemy_image_group).hp -= self.damage
            self.kill()
        if collide(self, walls_group) or collide(self, decor_collision_group):
            self.kill()
        if len(slash_group.sprites()) > 1:
            self.kill()


class Check_player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int, weapon):
        super().__init__(checks_group, all_sprites_group)
        self.weapon = weapon
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        collide = pygame.sprite.spritecollideany
        if collide(self, player_group):
            self.weapon.attack()
        self.kill()


class Mace(pygame.sprite.Sprite):
    '''Класс булавы'''

    def __init__(self, owner: Enemy_group1_tile, image: pygame.Surface,
                 damage: int):
        super().__init__(all_sprites_group, enemy_weapon_group)
        self.original_image = self.image = pygame.transform.scale(image,
                                                                  (30, 30))
        self.can_attack = 300
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = owner.rect.x, owner.rect.y
        self.damage = damage
        self.angle = 0
        self.owner = owner

    def update(self, *args, **kwargs):
        if len(self.owner.groups()) == 0:
            self.kill()
        x, y = self.owner.rect.x, self.owner.rect.y
        self.rect.x = x
        self.rect.y = y
        player = player_group.sprites()[0].rect
        player_x, player_y = player.x, player.y

        self.angle = -1 * math.degrees(math.atan2(player_y - y,
                                                  player_x - x)) + 180
        if 270 >= self.angle >= 90:
            self.image = pygame.transform.rotate(
                pygame.transform.flip(self.original_image, flip_x=1, flip_y=0),
                self.angle - 180)
        else:
            self.image = pygame.transform.rotate(self.original_image,
                                                 self.angle)
        if self.can_attack < 300:
            self.can_attack += 1

    def attack(self):
        if self.can_attack >= 300:
            player_group.sprites()[0].hp -= self.damage
            Crush(self, self.angle)
            self.can_attack = 0
            pygame.time.set_timer(DeleteEnemyEffects, 100)


class Crush(pygame.sprite.Sprite):
    def __init__(self, weapon: Mace, angle):
        super().__init__(effects_group, all_sprites_group)
        self.angle = angle
        self.weapon = weapon
        self.image = load_image_data('bulava_effect.png', -1)
        self.rect = pygame.Rect(weapon.rect.x, weapon.rect.y,
                                self.image.get_width(),
                                self.image.get_height())
        w_x, w_y = self.weapon.rect.x,self.weapon.rect.y  
        if 230 <= angle <= 270:
            self.rect = pygame.Rect(w_x, w_y - 32, 32, 32)
        elif 90 <= angle <= 148:
            self.rect = pygame.Rect(w_x, w_y + 32, 32, 32)
        elif 90 <= angle <= 270:
            self.rect = pygame.Rect(w_x + 32, w_y, 32, 32)
        else:
            self.rect = pygame.Rect(w_x - 32, w_y, 32, 32)


class Weapon(pygame.sprite.Sprite):
    '''Класс оружия'''

    def __init__(self, image: pygame.Surface, damage: int):
        super().__init__(weapon_group)
        player = player_group.sprites()[0].rect
        x, y = player.x, player.y

        self.damage = damage
        self.rect = pygame.Rect(x, y, *image.get_size())
        self.image = image
        self.original_image = self.image = pygame.transform.scale(self.image,
                                                                  (30, 30))
        self.angle = 1

    def update(self, *args, **kwargs):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player = player_group.sprites()[0].rect
        x, y = player.x, player.y
        self.rect.x = x
        self.rect.y = y
        self.angle = -1 * math.degrees(math.atan2(mouse_y - self.rect.y,
                                                  mouse_x -
                                                  self.rect.x)) + 180
        if 270 >= self.angle >= 90:
            self.image = pygame.transform.rotate(
                pygame.transform.flip(self.original_image, flip_x=1, flip_y=0),
                self.angle - 180)
        else:
            self.image = pygame.transform.rotate(self.original_image,
                                                 self.angle)

    def attack(self):
        pass


class Sword(Weapon):
    def __init__(self, image, damage):
        super().__init__(image, damage)

    def attack(self, *args):
        Slash(self.angle, self.damage)
        Effect(self.angle, 'sword_effect.png')


class Pistol(Weapon):
    '''Класс пистолета'''

    def __init__(self, image, damage):
        super().__init__(image, damage)

    def attack(self, mouse_x, mouse_y):
        '''анимация атаки не реализована, я пытался'''
        Bullet(mouse_x, mouse_y, self.damage)


class Bullet(pygame.sprite.Sprite):
    '''Класс пули'''

    def __init__(self, mouse_x: int, mouse_y: int, damage: int):
        super().__init__(all_sprites_group, bullets_group)
        self.damage = damage
        weapon = player_group.sprites()[0].now_weapon.rect
        x, y = weapon.x + weapon.w // 2, weapon.y + weapon.h // 2
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
        if collide(self, enemy_group):
            collide(self, enemy_image_group).hp -= self.damage
            self.kill()
        if collide(self, walls_group) or collide(self, decor_collision_group):
            self.kill()


def main():
    global all_sprites_group, entity_group, entity_image_group, player_group, \
        player_image_group, enemy_group, enemy_image_group, spase_group, \
        decor_free_group, decor_collision_group, walls_group, walls_group_up, \
        walls_group_down, walls_group_left, walls_group_right, void_spase_group, \
        bullets_group, weapon_group, effects_group, slash_group, checks_group, \
        enemy_weapon_group

    tile_width = tile_height = 80

    health = HealthBar(display, 600, 600, 100, 30)
    stamina = StaminaBar(display, 600, 631, 100, 30)
    ammo = BulletsCounter(display, 600, 662)

    all_sprites_group = pygame.sprite.Group()
    entity_group = pygame.sprite.Group()
    entity_image_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player_image_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    enemy_image_group = pygame.sprite.Group()
    spase_group = pygame.sprite.Group()
    decor_free_group = pygame.sprite.Group()
    decor_collision_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    walls_group_up = pygame.sprite.Group()
    walls_group_down = pygame.sprite.Group()
    walls_group_left = pygame.sprite.Group()
    walls_group_right = pygame.sprite.Group()
    void_spase_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    weapon_group = pygame.sprite.Group()
    slash_group = pygame.sprite.Group()
    effects_group = pygame.sprite.Group()
    checks_group = pygame.sprite.Group()
    enemy_weapon_group = pygame.sprite.Group()
    loaded_level = load_level('level_test1.txt')

    size_screen = (
        tile_width * loaded_level[1][0], tile_height * loaded_level[1][1])
    screen = pygame.Surface(size_screen)
    screen2 = pygame.Surface(size_screen)
    map = pygame.Surface(size_screen)

    back_button = ScreenButton(0, 0, 100, 60, 'Назад',
                               'button.png', 'emptybutton_hover.png',
                               'data/click.mp3')

    level_render(loaded_level[0])
    spase_group.draw(map)
    decor_free_group.draw(map)
    decor_collision_group.draw(map)

    pygame.time.set_timer(ENTITYIMAGESWAP, int(1000 / FPS_entity_swap))
    running = True
    attack = True
    reload_in_progress = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(num_buttons=3)[0] and attack:
                    player = player_group.sprites()[0]
                    if type(player.now_weapon) is Sword:
                        if stamina.stamina > 0:
                            player.attack(*pygame.mouse.get_pos())
                            attack = False
                            pygame.time.set_timer(AcceptAttackEvent, 150)
                            pygame.time.set_timer(DeleteAllAfterSwordEvent, 50)
                            pygame.mixer.Sound('data/sword-punch.mp3').play()
                            stamina.stamina -= 1
                            pygame.time.set_timer(StaminaRecoveryEvent, 500)
                    else:
                        if ammo.ammo > 0:
                            player.attack(*pygame.mouse.get_pos())
                            attack = False
                            pygame.time.set_timer(AcceptAttackEvent, 150)
                            ammo.ammo -= 1
                            pygame.mixer.Sound('data/fire_pistol.mp3').play()
                        if ammo.ammo == 0:
                            pygame.mixer.Sound('data/empty_ammo.mp3').play()
                        if ammo.ammo <= 0 and not reload_in_progress:
                            pygame.time.set_timer(ReloadPistolEvent, 5000)
                            pygame.mixer.Sound('data/pistol_reload.mp3').play()
                            reload_in_progress = True
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    player_group.sprites()[0].change_weapon()
                    if type(player_group.sprites()[0].now_weapon) == Sword:
                        pygame.mixer.Sound('data/changing_to_sword.mp3').play()
            if event.type == BackEvent:
                choose_level()
            back_button.handle_event(event, BackEvent)
            if event.type == DeleteAllAfterSwordEvent:
                if len(slash_group.sprites()):
                    slash_group.sprites()[0].kill()
                if len(effects_group.sprites()):
                    effects_group.sprites()[0].kill()
                pygame.time.set_timer(DeleteAllAfterSwordEvent, 0)
            if event.type == AcceptAttackEvent:
                attack = True
                pygame.time.set_timer(AcceptAttackEvent, 0)
            if event.type == StaminaRecoveryEvent:
                stamina.stamina += 1
                if stamina.stamina >= stamina.max_stamina:
                    stamina.stamina = stamina.max_stamina
                    pygame.time.set_timer(StaminaRecoveryEvent, 0)
            if event.type == ReloadPistolEvent:
                ammo.ammo = ammo.max_ammo
                pygame.time.set_timer(ReloadPistolEvent, 0)
                reload_in_progress = False
            if event.type == DeleteEnemyEffects:
                effects_group.sprites()[0].kill()
                pygame.time.set_timer(DeleteEnemyEffects, 0)
        time = clock.get_time() / 1000
        player_group.update(time)
        enemy_group.update(time)

        display.fill(pygame.Color("black"))
        screen.blit(map, (0, 0))
        bullets_group.draw(screen)
        bullets_group.update()
        entity_group.draw(screen)
        back_button.draw(screen)
        back_button.check_hover(pygame.mouse.get_pos())
        weapon_group.draw(screen)
        weapon_group.update()
        slash_group.draw(screen)
        slash_group.update()
        effects_group.draw(screen)
        effects_group.update()
        checks_group.draw(screen)
        checks_group.update()
        walls_group.draw(screen)
        enemy_weapon_group.draw(screen)
        enemy_weapon_group.update()
        display.blit(screen, (0, 0))
        health.draw()
        stamina.draw()
        ammo.draw()
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


if __name__ == '__main__':
    clock = pygame.time.Clock()
    start_screen()
