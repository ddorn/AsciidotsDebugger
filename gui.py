import os
from functools import lru_cache
from typing import Dict, List

import pygame

from dots.vector import Pos

# fixing f****** dpi awareness of my computer
try:
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass

pygame.init()
pygame.key.set_repeat(200, 10)
os.environ['SDL_VIDEO_CENTERED'] = '1'

FONTNAME = 'assets/monaco.ttf'
DEFAULT_FONT_SIZE = 24

REGULAR = 0
DOT = 1
BACKGROUND = 2
OPERATOR = 3
BRACKETS = 4
CONTROL_FLOW = 5
CONTROL_DIR = 6
DIGIT = 7
WRAP = 8
LIBVRAP = 9
ESCAPE_SEQUANCES = 10
MODES = 11
MSG = 12
MSG_BG = 13

COLORS = {
    REGULAR: (248, 248, 242),
    DOT: (104, 113, 94),
    BACKGROUND: (39, 40, 34),
    OPERATOR: (253, 151, 31),
    BRACKETS: (104, 113, 94),
    CONTROL_FLOW: (248, 37, 92),
    CONTROL_DIR: (102, 217, 239),
    DIGIT: (174, 129, 255),
    WRAP: (230, 219, 93),
    LIBVRAP: (166, 226, 46),
    ESCAPE_SEQUANCES: (249, 38, 114),
    MODES: (166, 226, 46),
    MSG: (248, 248, 242),
    MSG_BG: (62, 61, 50)
}


class Message:
    FONT = pygame.font.Font(FONTNAME, 2 * DEFAULT_FONT_SIZE)

    def __init__(self, text, pos, anchor='topleft'):
        self.text = str(text).replace('\n', '')
        self.surf = self.get_surf()  # type: pygame.SurfaceType
        self.pos = tuple(pos)
        self.anchor = anchor

    def render(self, surf):
        rect = self.surf.get_rect()
        setattr(rect, self.anchor, self.pos)
        surf.blit(self.surf, rect)

    def new_font(self, size):
        self.FONT = pygame.font.Font(FONTNAME, size)
        self.surf = self.get_surf()

    def get_surf(self):
        return self.FONT.render(self.text, 1, COLORS[MSG], COLORS[MSG_BG])


class Dot:
    FONT = pygame.font.Font(FONTNAME, DEFAULT_FONT_SIZE)

    def __init__(self, dot):
        """
        :type dot: dots.dot.Dot
        """

        self.pos = dot.pos
        self.state = str(dot.state)
        self.id = dot.id
        self.value = dot.value

        self.tooltip = None  # type: pygame.SurfaceType
class PygameDebugger:
    FPS = 60

    def __init__(self, env):
        """
        Graphical degguer updating from callbacks_relay

        :param dots.environemt.Env env:
        """

        self.env = env

        self.current_tick = -1

        self.font_size = DEFAULT_FONT_SIZE
        self.char_size = None  # type: Pos

        self.offset = Pos(5, 5)
        self.start_drag_pos = None  # type: Pos
        self.start_drag_offset = None  # type: Pos

        self.font = self.new_font(self.font_size)  # type: pygame.font.FontType
        self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)  # type: pygame.SurfaceType
        self.clock = pygame.time.Clock()

        self.tooltip = None  # type: Dot

        self.ticks = []  # type: List[List[Dot]]
        self.prints = {}  # type: Dict[int, Message]

    def run(self):
        """Start the debugger. stop it with io.on_finish()"""
        while not self.env.io.finished:
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(self.FPS)

    def update(self):
        mouse = Pos(pygame.mouse.get_pos())

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.env.io.on_finish()
                    return
                elif e.key == pygame.K_RIGHT:
                    # move 5 steps if ctrl pressed
                    self.current_tick += 1 + 4 * (e.mod & pygame.KMOD_CTRL != 0)
                elif e.key == pygame.K_LEFT:
                    self.current_tick = max(-1, self.current_tick - 1 - 4 * (e.mod & pygame.KMOD_CTRL != 0))
                elif e.key == pygame.K_EQUALS:  # I would like the + but apparently it doesn't work
                    self.font = self.new_font(self.font_size + 1)
                elif e.key == pygame.K_MINUS:
                    self.font = self.new_font(self.font_size - 1)
                elif e.key == pygame.K_r and e.mod & pygame.KMOD_CTRL:
                    self.start_drag_pos = None
                    self.start_drag_offset = None
                    self.offset = Pos(5, 5)
                    self.font = self.new_font(DEFAULT_FONT_SIZE)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.start_drag_pos = mouse
                self.start_drag_offset = self.offset
            elif e.type == pygame.MOUSEBUTTONUP:
                self.start_drag_pos = None
                self.start_drag_offset = None

            # get new ticks if needed
            while self.current_tick >= len(self.ticks) and not self.env.io.finished:
                tick = self._get_new_tick()
                self.ticks.append([Dot(dot) for dot in tick])

        # drag the code if needed
        if self.start_drag_pos is not None:
            actual_pos = mouse
            dx, dy = actual_pos - self.start_drag_pos
            if abs(dx) < 20:
                dx = 0
            if abs(dy) < 20:
                dy = 0

            self.offset = self.start_drag_offset + (dx, dy)

        # collect the output
        if not self.io.outputs.empty():
            x, _ = Pos(self.screen.get_size())
            self.prints[self.current_tick] = Message(self.io.outputs.get(), (x, 0), 'topright')

    def map_to_screen_pos(self, pos):
        return self.offset.x + self.char_size.x * pos.col, self.offset.y + self.char_size.y * pos.row

    def render(self):
        self.screen.fill(COLORS[BACKGROUND])

        if self.current_tick == -1:
            dot_pos = []
        else:
            dot_pos = {dot.pos for dot in self.ticks[self.current_tick]}

        mouse = pygame.mouse.get_pos()
        xstep = Pos(1, 0)

        for row, line in enumerate(self.env.world.map):
            for col, char in enumerate(line):
                c = char
                pos = Pos(col, row)

                if char.isOper():
                    color = OPERATOR
                elif c in '[{' and self.env.world.does_loc_exist(pos + xstep) and self.env.world.get_char_at(
                                pos + xstep).isOper():
                    color = BRACKETS
                elif c in '}]' and self.env.world.does_loc_exist(pos - xstep) and self.env.world.get_char_at(
                                pos - xstep).isOper():
                    color = BRACKETS
                elif c in '~*':
                    color = CONTROL_FLOW
                elif c in '<>v^':
                    color = CONTROL_DIR
                elif c.isdigit():
                    color = DIGIT
                elif char.isWarp():
                    color = WRAP
                elif char.isLibWarp():
                    color = LIBVRAP
                elif char in '@#$&':
                    color = MODES
                else:
                    color = REGULAR

                # color depends if there is a dot or not
                if pos in dot_pos:
                    surf = self._get_surface_for_char(c, color, DOT)
                else:
                    surf = self._get_surface_for_char(c, color, BACKGROUND)
                self.screen.blit(surf, self.map_to_screen_pos(pos))

        current_msg = self.get_current_message()
        if current_msg:
            current_msg.render(self.screen)


    def new_font(self, size):
        size = min(80, max(2, size))  # clamp
        self.font_size = size
        self._get_surface_for_char.cache_clear()
        font = pygame.font.Font(FONTNAME, size)
        self.char_size = Pos(font.size("."))
        return font

    def get_current_message(self):
        ticks = list(filter(lambda x: x <= self.current_tick, self.prints.keys()))
        if ticks:
            return self.prints[sorted(ticks)[-1]]

    @property
    def current_dots(self):
        """Return a list of the dots in this tick"""
        if self.current_tick == -1:
            return []
        return self.ticks[self.current_tick]

    def _get_new_tick(self):
        """Get a new tick from the interpreter, it can be none if there is no new tick yet"""
        return self.env.io.get_tick(wait=True)

    @lru_cache(maxsize=None)
    def _get_surface_for_char(self, char, color, background):
        return self.font.render(char, True, COLORS[color], COLORS[background])

    @property
    def io(self):
        """
        :rtype: debugger.CallbacksRelay
        """
        return self.env.io
