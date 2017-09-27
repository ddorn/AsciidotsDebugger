import os
from functools import lru_cache
from typing import Dict, List

import pygame
import pygame.gfxdraw

from dots.vector import Pos

from visual.font import Font

try:
    # fixing f****** dpi awareness of my computer
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except AttributeError:  # not windows
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


class Tooltip:
    def __init__(self, pos):
        self.tips = []  # type: List[pygame.SurfaceType]
        self.pos = pos  # type: Pos

    def add(self, object):
        """Add an object that as a get_tooltip method that returns a surface with the tip"""
        self.tips.append(object.get_tooltip())

    def insert(self, object, index):
        """Insert a tip at the given index."""
        self.tips.insert(object.get_tooltip(), index)

    def render(self, screen):
        """Show all the tips to the screen."""
        pos = self.pos

        # we just blit each surface given via add() with a darker background
        for tip in self.tips:

            rect = tip.get_rect()  # type: pygame.rect.RectType
            rect.topleft = pos

            # we draw a dark background to better see the tip
            points = rect.topleft, rect.topright, rect.bottomright, rect.bottomleft
            pygame.gfxdraw.filled_polygon(screen, points, COLORS[BACKGROUND] + (180,))
            # and blit the tip over it
            screen.blit(tip, rect)

            # we shift the bliting pos by the surfs height
            pos += 0, tip.get_rect().height


class Message:
    """Display a string in to the screen."""
    FONT = pygame.font.Font(FONTNAME, 2 * DEFAULT_FONT_SIZE)

    def __init__(self, text, pos, anchor='topleft'):
        self.text = str(text).replace('\n', '')
        self.surf = self.get_surf(self.text)  # type: pygame.SurfaceType
        self.pos = tuple(pos)
        self.anchor = anchor

    def render(self, surf):
        rect = self.surf.get_rect()
        setattr(rect, self.anchor, self.pos)
        surf.blit(self.surf, rect)

    def new_font(self, size):
        self.FONT = pygame.font.Font(FONTNAME, size)
        self.surf = self.get_surf(self.text)

    @staticmethod
    @lru_cache(maxsize=128)
    def get_surf(text):
        return Message.FONT.render(text, 1, COLORS[MSG], COLORS[MSG_BG]).convert()


# noinspection PyArgumentList
class Dot:
    """Same as a basic Asciidot dot but with only the nessecary atributes and methods to show it."""
    FONT = pygame.font.Font(FONTNAME, DEFAULT_FONT_SIZE)

    def __init__(self, dot):
        """
        :type dot: dots.dot.Dot
        """

        self.pos = dot.pos
        self.state = str(dot.state)
        self.id = dot.id
        self.value = dot.value

    def get_tooltip(self):
        """GEt a surface with Display information about the dot value, id and state to the screen."""
        return self._get_tooltip(self.value, self.id, self.state)

    @classmethod
    @lru_cache(32)
    def _get_tooltip(cls, value, id_, state):
        """Get the surface with dot's info."""
        text = "#{} @{} ~{}".format(value, id_, state)
        hashsurf = cls.render_text('#')
        value = cls.render_text(str(value))
        sep = cls.render_text(' ')
        atsurf = cls.render_text('@')
        idsurf = cls.render_text(str(id_))
        state_sep = cls.render_text('~')
        end = cls.render_text(state)

        pos = 0
        surf = pygame.Surface(cls.FONT.size(text))
        surf.set_colorkey((0, 0, 0))
        for s in (hashsurf, value, sep, atsurf, idsurf, sep, state_sep, end):
            surf.blit(s, (pos, 0))
            pos += s.get_width()

        return surf

    @classmethod
    @lru_cache(128)
    def render_text(cls, text):
        if text == '#':
            return cls.FONT.render(text, 1, COLORS[MODES])
        if text == '@':
            return cls.FONT.render(text, 1, COLORS[OPERATOR])
        if text == '~':
            return cls.FONT.render(text, 1, COLORS[CONTROL_FLOW])
        return cls.FONT.render(text, 1, COLORS[MSG])


class PygameDebugger:
    FPS = 60

    def __init__(self, env):
        """
        Graphical degguer updating from callbacks_relay

        :param dots.environemt.Env env:
        """

        self.env = env

        self.current_tick = -1
        self.auto_tick = False

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

        self.more_debug = False

    def run(self):
        """Start the debugger. stop it with io.on_finish()"""
        while not self.env.io.finished:
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(self.FPS)

    def update(self):
        mouse = Pos(pygame.mouse.get_pos())

        if self.auto_tick:
            self.current_tick += 1
            self.sync_ticks()

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
                elif e.mod & pygame.KMOD_CTRL:
                    if e.key == pygame.K_r:  # reset position and size
                        self.start_drag_pos = None
                        self.start_drag_offset = None
                        self.offset = Pos(5, 5)
                        self.font = self.new_font(DEFAULT_FONT_SIZE)
                    elif e.key == pygame.K_b:  # go back to the beginning
                        self.current_tick = -1
                    elif e.key == pygame.K_a:  # toggle autotick
                        self.auto_tick = not self.auto_tick
                    elif e.key == pygame.K_m:  # toggle more_debug
                        self.more_debug = not self.more_debug
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.start_drag_pos = mouse
                self.start_drag_offset = self.offset
            elif e.type == pygame.MOUSEBUTTONUP:
                self.start_drag_pos = None
                self.start_drag_offset = None

            # get new ticks if needed
            self.sync_ticks()

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

    def sync_ticks(self):
        """Get new ticks untill current_tick."""
        while self.current_tick >= len(self.ticks) and not self.env.io.finished:
            tick = self._get_new_tick()
            self.ticks.append([Dot(dot) for dot in tick])

    def map_to_screen_pos(self, pos):
        """Convert the position of char/dot in the map to its coordinates in the screen."""
        return self.offset.x + self.char_size.x * pos.col, self.offset.y + self.char_size.y * pos.row

    def render(self):
        self.screen.fill(COLORS[BACKGROUND])

        if self.current_tick == -1:
            dot_pos = []
        else:
            dot_pos = {dot.pos for dot in self.ticks[self.current_tick]}

        mouse = pygame.mouse.get_pos()

        # show every char of the map + dots via the background
        for row, line in enumerate(self.env.world.map):
            for col, char in enumerate(line):
                c = char
                pos = Pos(col, row)
                screen_pos = self.map_to_screen_pos(pos)

                # we don't want to render the char that are outside the screen
                if not pygame.Rect(screen_pos, self.char_size).colliderect(self.screen.get_rect()):
                    continue

                color = self.char_to_color(char, pos)

                # background depends if there is a dot or not
                if pos in dot_pos:
                    surf = self._get_surface_for_char(c, color, DOT)
                else:
                    surf = self._get_surface_for_char(c, color, BACKGROUND)
                self.screen.blit(surf, screen_pos)

        # Show output
        current_msg = self.get_current_message()
        if current_msg:
            current_msg.render(self.screen)

        # Tooltips
        tooltip = Tooltip(mouse + Pos(10, 10))
        if self.more_debug:
            pass
        for dot in self.current_dots:
            # if there is more than one dot at this place, we want to show only one
            # the first dot that has this pos
            if pygame.Rect(self.map_to_screen_pos(dot.pos), self.char_size).collidepoint(*mouse):
                tooltip.add(dot)
        tooltip.render(self.screen)

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

    def char_to_color(self, char, pos):
        """Get the colorcode to render a given char."""
        if char.isOper():
            return OPERATOR
        if char in '[{' and self.env.world.does_loc_exist(pos + Pos(1, 0)) and self.env.world.get_char_at(
                        pos + Pos(1, 0)).isOper():
            return BRACKETS
        if char in '}]' and self.env.world.does_loc_exist(pos - Pos(1, 0)) and self.env.world.get_char_at(
                        pos - Pos(1, 0)).isOper():
            return BRACKETS
        if char in '~*':
            return CONTROL_FLOW
        if char in '<>v^':
            return CONTROL_DIR
        if char.isdigit():
            return DIGIT
        if char.isWarp():
            return WRAP
        if char.isLibWarp():
            return LIBVRAP
        if char in '@#$&':
            return MODES

        return REGULAR

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
        return self.font.render(char, True, COLORS[color], COLORS[background]).convert()

    @property
    def io(self):
        """
        :rtype: debugger.CallbacksRelay
        """
        return self.env.io
