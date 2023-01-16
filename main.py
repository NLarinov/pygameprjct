import math
import os
import time
from random import randint
from collections import deque
import pygame
from pygame.locals import *
import pygame_menu


def setimage(dif):
    def load_image(img_file_name):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img
    if dif == 'Easy':
        return {'background': load_image('back2.jpg'),
                'pipe-end': load_image('pip.png'),
                'pipe-body': load_image('pipib.png'),
                'bird-wingup': load_image('kir.png'),
                'bird-wingdown': load_image('kir.png')}
    return {'background': load_image('background.png'),
            'pipe-end': load_image('pipie.png'),
            'pipe-body': load_image('pipib.png'),
            'bird-wingup': load_image('upp.png'),
            'bird-wingdown': load_image('down.png')}


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
        total_pipe_body_pieces = int((WHEIGHT - 3 * Brd.HEIGHT - 3 * Pipe.PIECE_HEIGHT) / Pipe.PIECE_HEIGHT)
        self.bottom_pieces = randint(1, total_pipe_body_pieces)
        self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

        for i in range(1, self.bottom_pieces + 1):
            piece_pos = (0, WHEIGHT - i * Pipe.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_pos)
        bottom_pipe_end_y = WHEIGHT - self.bottom_height_px
        bottom_end_piece_pos = (0, bottom_pipe_end_y - Pipe.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_pos)

        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, i * Pipe.PIECE_HEIGHT))
        top_pipe_end_y = self.top_height_px
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        self.top_pieces += 1
        self.bottom_pieces += 1

        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):
        return self.top_pieces * Pipe.PIECE_HEIGHT

    @property
    def bottom_height_px(self):
        return self.bottom_pieces * Pipe.PIECE_HEIGHT

    @property
    def visible(self):
        return -Pipe.WIDTH < self.x < WWIDTH

    @property
    def rect(self):
        return Rect(self.x, 0, Pipe.WIDTH, Pipe.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        self.x -= ANSPEED * frm(delta_frames)

    def collides_with(self, bird):
        return pygame.sprite.collide_mask(self, bird)


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


class Brd(pygame.sprite.Sprite):
    WIDTH = HEIGHT = 32

    def __init__(self, x, y, msec_to_climb, images):
        super(Brd, self).__init__()
        self.x, self.y = x, y
        self.msec_to_climb = msec_to_climb
        self._img_wingup, self._img_wingdown = images
        self._mask_wingup = pygame.mask.from_surface(self._img_wingup)
        self._mask_wingdown = pygame.mask.from_surface(self._img_wingdown)
        self.climb = GCLSPD
        self.sink = GSISPD
        self.duration = GCLIMBDUR

    def update(self, delta_frames=1):
        if self.msec_to_climb > 0:
            frac_climb_done = 1 - self.msec_to_climb/self.duration
            self.y -= (self.climb * frm(delta_frames) *
                       (1 - math.cos(frac_climb_done * math.pi)))
            self.msec_to_climb -= frm(delta_frames)
        else:
            self.y += self.sink * frm(delta_frames)

    @property
    def image(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_wingup
        else:
            return self._img_wingdown

    @property
    def mask(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wingup
        else:
            return self._mask_wingdown

    @property
    def rect(self):
        return Rect(self.x, self.y, Brd.WIDTH, Brd.HEIGHT)


def end_screen(score):
    disp = pygame.display.set_mode((341, 246))
    score_font = pygame.font.SysFont('Times New Roman', 32, bold=True)
    score_surface = score_font.render(f'Your score is: {score}', True, (0, 0, 0))
    file_name = os.path.join(os.path.dirname(__file__),
                             'images', 'loser.png')
    img = pygame.image.load(file_name)
    img.convert()
    score_x = 341 / 2 - score_surface.get_width() / 2
    while True:
        ev = pygame.event.get()
        for et in ev:
            if et.type == pygame.QUIT:
                exit()
        disp.blit(img, (0, 0))
        disp.blit(score_surface, (score_x, 0))
        pygame.display.update()


def main(diff):
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont('Times New Roman', 32, bold=True)
    images = setimage(diff)

    bird = Brd(50, int(WHEIGHT / 2 - Brd.HEIGHT / 2), 2,
               (images['bird-wingup'], images['bird-wingdown']))
    pipes = deque()

    frame_clock = 0
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)

        if not (paused or frame_clock % msc(GADDRVAL)):
            pp = Pipe(images['pipe-end'], images['pipe-body'])
            pipes.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and e.key in (K_UP, K_RETURN, K_SPACE)):
                bird.msec_to_climb = GCLIMBDUR
        if paused:
            continue

        pipe_collision = any(p.collides_with(bird) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= WHEIGHT - Brd.HEIGHT:
            done = True

        for x in (0, WWIDTH / 2):
            display_surface.blit(images['background'], (x, 0))

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        for p in pipes:
            if p.x + Pipe.WIDTH < bird.x and not p.score_counted:
                score += 1
                p.score_counted = True

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WWIDTH / 2 - score_surface.get_width() / 2
        display_surface.blit(score_surface, (score_x, Pipe.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
    with open('file.txt', 'r+') as lne:
        a = lne.readlines()[-1]
        lne.truncate()
        lne.write(a + ' ' + str(score) + '\n')
    end_screen(score)
    pygame.quit()


if __name__ == '__main__':
    pygame.init()

    display_surface = pygame.display.set_mode((WWIDTH, WHEIGHT))
    pygame.display.set_caption('Pygame Flappy Brd')
    difficulty = 'Normal'


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
            elif difficulty == 'Easy':
                GSISPD = 0.1
                GCLSPD = 0.8
                GCLIMBDUR = 80.3
                GADDRVAL = 3000
            elif difficulty == 'Hard':
                GSISPD = 0.2
                GCLSPD = 1.3
                GCLIMBDUR = 80.3
                GADDRVAL = 1500
            elif difficulty == 'GODMODE':
                GSISPD = 0.4
                GCLSPD = 1.3
                GCLIMBDUR = 80.3
                GADDRVAL = 1000


    def start_the_game():
        main(difficulty)


    def level_menu():
        mainmenu._open(level)


    def files(name):
        with open('file.txt', 'r+') as ln:
            ln.truncate()
            ln.write(name)


    with open('file.txt') as line:
        mainmenu = pygame_menu.Menu(f'Hi, {line.readlines()[-1]}', 800, 480, theme=pygame_menu.themes.THEME_SOLARIZED)
    mainmenu.add.text_input('Name: ', default='username', maxchar=20, onchange=files)
    mainmenu.add.button('Play', start_the_game)
    mainmenu.add.button('Levels', level_menu)
    mainmenu.add.button('Quit', pygame_menu.events.EXIT)

    level = pygame_menu.Menu('Select a Difficulty', 800, 480, theme=pygame_menu.themes.THEME_BLUE)
    level.add.selector('Difficulty :', [('Normal', 1), ('Hard', 2), ('GODMODE', 3), ('Easy', 4)],
                       onchange=set_difficulty)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        if mainmenu.is_enabled():
            mainmenu.update(events)
            mainmenu.draw(display_surface)

        pygame.display.update()
