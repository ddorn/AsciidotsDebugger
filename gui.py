import copy
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

Map = List[List["VisualChar"]]

pygame.init()
pygame.key.set_repeat(200, 10)
os.environ['SDL_VIDEO_CENTERED'] = '1'

FONTNAME = 'assets/monaco.ttf'
DEFAULT_FONT_SIZE = 24
MAINFONT = Font(FONTNAME, DEFAULT_FONT_SIZE)
SMALLFONT = Font(FONTNAME, DEFAULT_FONT_SIZE * 0.75)
BIGFONT = Font(FONTNAME, DEFAULT_FONT_SIZE * 2)
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
MOREDEBUG_MSG = 14

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
    MSG_BG: (62, 61, 50),
    MOREDEBUG_MSG: (253, 151, 31),
}


class Tooltip:
    """Display a list of infos about objects."""

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
        if not self.tips:
            return

        pos = self.pos
        width = max([s.get_width() for s in self.tips])

        # we just blit each surface given via add() with a darker background
        for tip in self.tips:

            rect = tip.get_rect()  # type: pygame.rect.RectType
            rect.topleft = pos
            rect.width = width

            # we draw a dark background to better see the tip
            points = rect.topleft, rect.topright, rect.bottomright, rect.bottomleft
            pygame.gfxdraw.filled_polygon(screen, points, COLORS[BACKGROUND] + (180,))
            # and blit the tip over it
            screen.blit(tip, rect)

            # we shift the bliting pos by the surfs height
            pos += 0, tip.get_rect().height + 1


# this will be removed one day
class Message:
    """Display a string in to the screen."""

    def __init__(self, text, pos, anchor='topleft'):
        self.text = str(text).replace('\n', '')
        self.pos = tuple(pos)
        self.anchor = anchor

    def render(self, screen):
        surf = self.get_surf()
        rect = surf.get_rect()
        setattr(rect, self.anchor, self.pos)
        screen.blit(surf, rect)

    def get_surf(self):
        if len(self.text) == 1:
            render = BIGFONT.render_char
        else:
            render = BIGFONT.render_text
        return render(self.text, COLORS[MSG], COLORS[MSG_BG]).convert()


class VisualChar:
    def __init__(self, char, color):
        self.char = char
        self.color = color

    def get_tooltip(self):
        return MAINFONT.render_text(type(self.char).__name__, COLORS[MOREDEBUG_MSG])

    def render(self, screen, pos, dot_here=False):
        # background depends if there is a dot or not
        if dot_here:
            surf = MAINFONT.render_char(self.char, COLORS[self.color], COLORS[DOT])
        else:
            surf = MAINFONT.render_char(self.char, COLORS[self.color], COLORS[BACKGROUND])
        screen.blit(surf, pos)

# noinspection PyArgumentList
class Dot:
    """Same as a basic Asciidot dot but with only the nessecary atributes and methods to show it."""

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
    @MAINFONT.clear_when_size_change
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
        surf = pygame.Surface(MAINFONT.size(text))
        surf.set_colorkey((0, 0, 0))
        for s in (hashsurf, value, sep, atsurf, idsurf, sep, state_sep, end):
            surf.blit(s, (pos, 0))
            pos += s.get_width()

        return surf

    @classmethod
    @MAINFONT.clear_when_size_change
    @lru_cache(128)
    def render_text(cls, text):
        if text == '#':
            return MAINFONT.render_char(text, COLORS[MODES])
        if text == '@':
            return MAINFONT.render_char(text, COLORS[OPERATOR])
        if text == '~':
            return MAINFONT.render_char(text, COLORS[CONTROL_FLOW])
        return MAINFONT.render_text(text, COLORS[MSG])


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

        self.offset = Pos(5, 5)
        self.start_drag_pos = None  # type: Pos
        self.start_drag_offset = None  # type: Pos

        self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)  # type: pygame.SurfaceType
        self.clock = pygame.time.Clock()

        self.tooltip = None  # type: Dot

        self.ticks = []  # type: List[List[Dot]]
        self.prints = {}  # type: Dict[int, Message]
        self.map = self.get_map(self.env)  # type: Map

        self.more_debug = False

    def get_map(self, env):
        map = copy.deepcopy(env.world.map)
        for row, line in enumerate(map):
            for col, char in enumerate(line):
                color = self.char_to_color(char, Pos(col, row))
                map[row][col] = VisualChar(char, color)

        return map

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
                    MAINFONT.change_size(1)
                    BIGFONT.set_size(MAINFONT.font_size * 2)
                    SMALLFONT.set_size(MAINFONT.font_size * 0.75)
                elif e.key == pygame.K_MINUS:
                    MAINFONT.change_size(-1)
                    BIGFONT.set_size(MAINFONT.font_size * 2)
                    SMALLFONT.set_size(MAINFONT.font_size * 0.75)
                elif e.mod & pygame.KMOD_CTRL:
                    if e.key == pygame.K_r:  # reset position and size
                        self.start_drag_pos = None
                        self.start_drag_offset = None
                        self.offset = Pos(5, 5)
                        MAINFONT.set_size(DEFAULT_FONT_SIZE)
                        BIGFONT.set_size(MAINFONT.font_size * 2)
                        SMALLFONT.set_size(MAINFONT.font_size * 0.75)
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
        return self.offset.x + MAINFONT.char_size.x * pos.col, self.offset.y + MAINFONT.char_size.y * pos.row

    def render(self):
        self.screen.fill(COLORS[BACKGROUND])

        if self.current_tick == -1:
            dot_pos = []
        else:
            dot_pos = {dot.pos for dot in self.ticks[self.current_tick]}

        mouse = pygame.mouse.get_pos()
        tooltip = Tooltip(mouse + Pos(10, 10))
        screen_rect = self.screen.get_rect()

        # show every char of the map + dots via the background
        for row, line in enumerate(self.map):
            for col, char in enumerate(line):
                pos = Pos(col, row)
                pos_on_screen = self.map_to_screen_pos(pos)
                rect = pygame.Rect(pos_on_screen, MAINFONT.char_size)

                # we don't want to render the char that are outside the screen
                if not rect.colliderect(screen_rect):
                    continue

                char.render(self.screen, pos_on_screen, pos in dot_pos)

                if self.more_debug:
                    if rect.collidepoint(*mouse):
                        tooltip.add(char)

        # Show output
        current_msg = self.get_current_message()
        if current_msg:
            current_msg.render(self.screen)

        # Tooltips
        if self.more_debug:
            pass
        for dot in self.current_dots:
            # if there is more than one dot at this place, we want to show only one
            # the first dot that has this pos
            if pygame.Rect(self.map_to_screen_pos(dot.pos), MAINFONT.char_size).collidepoint(*mouse):
                tooltip.add(dot)
        tooltip.render(self.screen)

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

    @property
    def io(self):
        """
        :rtype: debugger.CallbacksRelay
        """
        return self.env.io
