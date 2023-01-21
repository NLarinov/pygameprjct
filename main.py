import math
import os
from random import randint
from collections import deque
import pygame
from pygame.locals import *
import pygame_menu


# Добро пожаловать в игру Cool Flappy Bird!
# Игра состоит из нескольких уровней,
# которые можно найти переключив
# уровень сложности
# смысл игры заключается в том,
# чтобы набрать максимальное
# количество очков и вписать свой
# результат в историю.
#
# Вы будете управлять маленькой птичкой
# которой предстоит преодолеть
# невероятный путь, чтобы достичь
# умопомрачительного господства
# в текущем жесточайшем мире.
#
# Чтобы набирать очки, вам нужно
# пролетать птицей между трубами и при этом
# не выходить за границы мира.
#
# Для управления вы можете использовать
# стрелку вверх или левую кнопку мыши.
#
# Также в меню вы можете переключаться с
# помощью стрелок, выбирать с помощью
# enter и возвращаться с помощью
# backspace (<-)
#
# В начале вы можете выбрать уровень
# сложности, который влияет на частоту
# появления труб и разные
# физические константы в игре.


# функция setimage загружает все
# требуемые изображения
def setimage(dif):
    def load_image(img_file_name):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img
    if dif == 'Hard':
        return {'background': load_image('back2.jpg'),
                'pipe-end': load_image('pip.png'),
                'pipe-body': load_image('pipeban.jpg'),
                'bird-wingup': load_image('kir.png'),
                'bird-wingdown': load_image('kir.png')}
    return {'background': load_image('background.png'),
            'pipe-end': load_image('pipie.png'),
            'pipe-body': load_image('pipib.png'),
            'bird-wingup': load_image('upp.png'),
            'bird-wingdown': load_image('down.png')}


# инициализируем класс, который
# создает трубы
# WIDTH - ширина трубы
# PIECE_HEIGHT - длина
# класс принимает изображения трубы


class Pipe(pygame.sprite.Sprite):
    WIDTH = 80
    PIECE_HEIGHT = 32

    def __init__(self, pipe_end_img, pipe_body_img, *groups):
        super().__init__(*groups)
        self.x = float(WWIDTH - 1)
        self.score_counted = False
        self.interval = GADDRVAL

        self.image = pygame.Surface((Pipe.WIDTH, WHEIGHT), SRCALPHA)
        self.image.convert()
        self.image.fill((0, 0, 0, 0))
        # инициализация поверхности экрана
        # и заполнение
        total = int((WHEIGHT - 3 * Brd.HEIGHT - 3 * Pipe.PIECE_HEIGHT) / Pipe.PIECE_HEIGHT)
        self.bottom = randint(1, total)
        self.top_pieces = total - self.bottom
        # рассчеты для правильной
        # установки требуемых труб

        for i in range(1, self.bottom + 1):
            item = (0, WHEIGHT - i * Pipe.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, item)
        conclude = WHEIGHT - self.bottom_height_px
        botpos = (0, conclude - Pipe.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, botpos)
        # рассчет и установка
        # вывод на экран труб

        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, i * Pipe.PIECE_HEIGHT))
        top_pipe_end_y = self.top_height_px
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))
        # добавляем к созданным
        # трубам их концы
        # потом создаем маску поверхности

        self.top_pieces += 1
        self.bottom += 1

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_frames=1):
        self.x -= ANSPEED * frm(delta_frames)
    # обновить позицию

    @property
    def top_height_px(self):
        return self.top_pieces * Pipe.PIECE_HEIGHT

    # берем углы трубы чтобы
    # в дальнейшем рассчитывать
    # возможное столкновение
    # property используется для
    # использования функции как
    # свойства класса, а не метода

    def collides_with(self, bird):
        return pygame.sprite.collide_mask(self, bird)

    # маска столкновения

    @property
    def visible(self):
        return -Pipe.WIDTH < self.x < WWIDTH

    # если текущая точка
    # не выходит за пределы экрана

    @property
    def rect(self):
        return Rect(self.x, 0, Pipe.WIDTH, Pipe.PIECE_HEIGHT)

    @property
    def bottom_height_px(self):
        return self.bottom * Pipe.PIECE_HEIGHT


# создание констант
# для дальнейшего исползования
# FPS
# кадры в секундах
# ANSPEED
# скорость анимации в пикселях
# WWIDTH
# ширина окна
# WHEIGH
# высота окна
# GSISPD
# скорость притяжения к земле
# GCLSPD
# дальность прыжка птички
# GCLIMBDUR
# длительность прыжка птички
# GADDRVAL
# интервал между трубами

FPS = 60
ANSPEED = 0.30
WWIDTH = 400 * 2
WHEIGHT = 480
GSISPD = 0.15
GCLSPD = 1.0
GCLIMBDUR = 80.3
GADDRVAL = 2000


def frm(frames, fps=FPS):
    return 1000.0 * frames / fps


def msc(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0


# инициализация класса
# объекта птицы
# принимает аргументы констант
# дальность прыжка, длительность
# и скорость притяжения к земле


class Brd(pygame.sprite.Sprite):
    WIDTH = HEIGHT = 32

    def __init__(self, x, y, msec_to_climb, images):
        super(Brd, self).__init__()
        self.climb = GCLSPD
        self.sink = GSISPD
        self.duration = GCLIMBDUR
        self.x, self.y = x, y
        self.msc = msec_to_climb
        self.wup, self.wdown = images
        self.mwup = pygame.mask.from_surface(self.wup)
        self.mwdown = pygame.mask.from_surface(self.wdown)

    @property
    def image(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self.wup
        else:
            return self.wdown
    # каждый период времени меняем
    # картинку с птичкой
    # имитируем движение крыльев

    @property
    def mask(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self.mwup
        else:
            return self.mwdown
    # каждый период времени меняем
    # картинку с птичкой
    # имитируем движение крыльев

    @property
    def rect(self):
        return Rect(self.x, self.y, Brd.WIDTH, Brd.HEIGHT)

    def update(self, delta_frames=1):
        if self.msc > 0:
            flag = 1 - self.msc / self.duration
            self.y -= (self.climb * frm(delta_frames) *
                       (1 - math.cos(flag * math.pi)))
            self.msc -= frm(delta_frames)
        else:
            self.y += self.sink * frm(delta_frames)
    # обновляем положение птицы:
    # функция делает плавный
    # прыжок с помощью
    # рассчета по косинусу
    # (взяли милисекунды на прыжок,
    # поделили их на длительность прыжка,
    # длину прыжка посекундно увеличиваем
    # сначала медленно в середине быстрее
    # и в конце опять медленно
    # имитация реального полета птицы)


# функция конечного загрузочного экрана,
# которая выводит надпись
# с результатом и троллит игрока
# загружая картинку лузера
# выводим последний результат
# игры

def end_screen(score):
    disp = pygame.display.set_mode((341, 246))
    score_font = pygame.font.SysFont('Times New Roman', 32, bold=True)
    scrsrf = score_font.render(f'Your score is: {score}', True, (0, 0, 0))
    file_name = os.path.join(os.path.dirname(__file__),
                             'images', 'loser.png')
    img = pygame.image.load(file_name)
    img.convert()
    score_x = 341 / 2 - scrsrf.get_width() / 2
    while True:
        ev = pygame.event.get()
        for et in ev:
            if et.type == pygame.QUIT:
                exit()
        disp.blit(img, (0, 0))
        disp.blit(scrsrf, (score_x, 0))
        pygame.display.update()


# основная функция
# инициализирующая
# все процессы

def main(diff):
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont('Times New Roman', 32, bold=True)
    images = setimage(diff)

    bird = Brd(50, int(WHEIGHT / 2 - Brd.HEIGHT / 2), 2,
               (images['bird-wingup'], images['bird-wingdown']))
    pipes = deque()

    # настраиваем стили и
    # вызываем класс инициализации
    # птицы вместе с двумя картинками
    # крылья вверх и вниз

    frame_clock = 0
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)

        if not (paused or frame_clock % msc(GADDRVAL)):
            pp = Pipe(images['pipe-end'], images['pipe-body'])
            pipes.append(pp)
            # каждый раз, через интервал появления
            # новой трубы, добавляем ее к другим

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and e.key in (K_UP, K_RETURN, K_SPACE)):
                bird.msc = GCLIMBDUR
        if paused:
            continue
        # заставляем птичку ждать
        # вначале и когда игру
        # ставят на паузу

        pipe_collision = any(p.collides_with(bird) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= WHEIGHT - Brd.HEIGHT:
            done = True
        # каждый раз проверяем столкнулась
        # ли птица с трубой

        for x in (0, WWIDTH):
            display_surface.blit(images['background'], (x, 0))
        # обновляем задний фон

        while pipes and not pipes[0].visible:
            pipes.popleft()
        # если труба уже вышла из поля видимости

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)
        # выводим все на экран и блитим

        for p in pipes:
            if p.x + Pipe.WIDTH < bird.x and not p.score_counted:
                score += 1
                p.score_counted = True

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WWIDTH / 2 - score_surface.get_width() / 2
        display_surface.blit(score_surface, (score_x, Pipe.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
        # загружаем все и рендерим
        # блитим и меняем очки результатов
        # меняем кадр

    # открываем файл записи
    # результатов, записываем новый
    with open('file.txt', 'r+') as lne:
        a = lne.readlines()[-1]
        lne.truncate()
        lne.write(a + ' ' + str(score) + '\n')
    end_screen(score)
    pygame.quit()


# инициализируем пайгейм
if __name__ == '__main__':
    pygame.init()

    display_surface = pygame.display.set_mode((WWIDTH, WHEIGHT))
    pygame.display.set_caption('Cool Flappy Brd')
    difficulty = 'Normal'

    # устанавливаем все уровни сложности
    # проверяем какой текущий
    # уровень сложности и
    # в зависимости от этого
    # меняем значения
    # констант, а точнее
    # значение притяжения
    # значение скорости прыжка
    # значение длительности прыжка
    # значение интервала между
    # трубами
    def set_difficulty(value, diff):
        global difficulty
        difficulty = value[0][0]
        global GADDRVAL, GCLIMBDUR, GCLSPD, GSISPD
        if diff:
            if difficulty == 'Normal':
                GSISPD = 0.15
                GCLSPD = 1.0
                GCLIMBDUR = 80.3
                GADDRVAL = 2000
            elif difficulty == 'Easy' or difficulty == 'Hard':
                GSISPD = 0.1
                GCLSPD = 0.5
                GCLIMBDUR = 80.3
                GADDRVAL = 3000
            elif difficulty == 'GODMODE':
                GSISPD = 0.4
                GCLSPD = 1.3
                GCLIMBDUR = 80.3
                GADDRVAL = 1000


    def start_the_game():
        main(difficulty)
    # отсюда запускается основная
    # функция со значением сложности


    def level_menu():
        mainmenu._open(level)
    # меню выбора сложности


    def files(name):
        with open('file.txt', 'r+') as ln:
            ln.truncate()
            ln.write(name)
    # открываем файл и
    # записываем имя
    # которое было введено
    # пользователем

    with open('file.txt') as line:
        mainmenu = pygame_menu.Menu(f'Hi, {line.readlines()[-1]}', 800, 480, theme=pygame_menu.themes.THEME_SOLARIZED)
    # выводим последнее
    # имя пользователя
    # при запуске

    mainmenu.add.text_input('Name: ', default='username', maxchar=20, onchange=files)
    mainmenu.add.button('Play', start_the_game)
    mainmenu.add.button('Levels', level_menu)
    mainmenu.add.button('Quit', pygame_menu.events.EXIT)

    level = pygame_menu.Menu('Select a Difficulty', 800, 480, theme=pygame_menu.themes.THEME_BLUE)
    level.add.selector('Difficulty :', [('Normal', 1), ('Hard', 2), ('GODMODE', 3), ('Easy', 4)],
                       onchange=set_difficulty)
    # инициализация всех кнопок
    # и селекторов выбора
    # сложности и т.д.

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        if mainmenu.is_enabled():
            mainmenu.update(events)
            mainmenu.draw(display_surface)

        pygame.display.update()
    # пока окно не закроют
