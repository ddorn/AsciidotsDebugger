import os
from functools import lru_cache

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
    MODES: (166, 226, 46)
}

class PygameDebugger:
    FPS = 60

    def __init__(self, env):
        """
        Graphical degguer updating from callbacks_relay

        :param dots.environemt.Env env:
        """


        self.env = env

        self.current_tick = -1
        self.font_size = 16
        self.char_size = 0, 0   # set by self.set_font

        self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)  # type: pygame.SurfaceType
        self.font = self.new_font(self.font_size)  # type: pygame.font.FontType
        self.clock = pygame.time.Clock()

        self.ticks = []

    def run(self):
        """Start the debugger. stop it with io.on_finish()"""
        while not self.env.io.finished:
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(self.FPS)

    def update(self):

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.env.io.on_finish()
                    return
                elif e.key == pygame.K_RIGHT:
                    # move 5 steps if ctrl pressed
                    self.current_tick += 1 + 4*(e.mod & pygame.KMOD_CTRL != 0)
                elif e.key == pygame.K_LEFT:
                    self.current_tick = max(0, self.current_tick - 1 - 4*(e.mod & pygame.KMOD_CTRL != 0))
                elif e.key == pygame.K_EQUALS:  # I would like the + but apparently it doesn't work
                    self.font = self.new_font(self.font_size + 1)
                elif e.key == pygame.K_MINUS:
                    self.font = self.new_font(self.font_size - 1)

        while self.current_tick >= len(self.ticks) and not self.env.io.finished:
            tick = self._get_new_tick()
            self.ticks.append(tick)

    def render(self):
        self.screen.fill(COLORS[BACKGROUND])

        if self.current_tick == -1:
            dot_pos = []
        else:
            dot_pos = {dot.pos for dot in self.ticks[self.current_tick]}

        xstep = Pos(1, 0)

        for row, line in enumerate(self.env.world.map):
            for col, char in enumerate(line):
                c = char
                pos = Pos(col, row)

                if char.isOper():
                    color = OPERATOR
                elif c in '[{' and self.env.world.does_loc_exist(pos + xstep) and self.env.world.get_char_at(pos + xstep).isOper():
                    color = BRACKETS
                elif c in '}]' and self.env.world.does_loc_exist(pos - xstep) and self.env.world.get_char_at(pos - xstep).isOper():
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

                if pos in dot_pos:
                    surf = self._get_surface_for_char(c, color, DOT)
                else:
                    surf = self._get_surface_for_char(c, color, BACKGROUND)

                pos = 5 + self.char_size[0] * col, 5 + self.char_size[1] * row
                self.screen.blit(surf, pos)

    def new_font(self, size):
        size = min(60, max(2, size))  # clamp
        self.font_size = size
        self._get_surface_for_char.cache_clear()
        font = pygame.font.Font(FONTNAME, size)
        self.char_size = font.size(".")
        return font

    def _get_new_tick(self):
        """Get a new tick from the interpreter, it can be none if there is no new tick yet"""
        return self.env.io.get_tick(wait=True)

    @lru_cache(maxsize=None)
    def _get_surface_for_char(self, char, color, background):
        return self.font.render(char, True, COLORS[color], COLORS[background])
