import os
from functools import lru_cache

import pygame

from dots.interpreter import AsciiDotsInterpreter

pygame.init()
pygame.key.set_repeat(100, 50)
WHITE = (255, 255, 255)

REGULAR = 0
DOT = 1
BACKGROUND = 2

COLORS = {
    REGULAR: (248, 248, 242),
    DOT: (249, 38, 114),
    BACKGROUND: (39, 40, 34)
}

class PygameDebugger:
    FPS = 60

    def __init__(self, env):
        """
        Graphical degguer updating from callbacks_relay

        :param dots.environemt.Env env:
        """

        self.env = env

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((800, 500), pygame.NOFRAME)
        self.font = pygame.font.Font('assets/monaco.ttf', 16)
        self.clock = pygame.time.Clock()

        self.ticks = []
        self.current_tick = -1

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
                    self.current_tick += 1
                elif e.key == pygame.K_LEFT:
                    self.current_tick = max(0, self.current_tick - 1)

        while self.current_tick >= len(self.ticks) and not self.env.io.finished:
            tick = self._get_new_tick()
            self.ticks.append(tick)

    def render(self):
        self.screen.fill(COLORS[BACKGROUND])

        if self.current_tick == -1:
            dot_pos = []
        else:
            dot_pos = {dot.pos for dot in self.ticks[self.current_tick]}

        for row, line in enumerate(self.env.world.map):
            for col, char in enumerate(line):
                c = str(char)

                if (col, row) in dot_pos:
                    surf = self._get_surface_for_char(c, DOT)
                else:
                    surf = self._get_surface_for_char(c, REGULAR)

                pos = 5 + 11 * col, 5 + 22 * row
                self.screen.blit(surf, pos)

    def _get_new_tick(self):
        """Get a new tick from the interpreter, it can be none if there is no new tick yet"""
        return self.env.io.get_tick(wait=True)

    @lru_cache(maxsize=None)
    def _get_surface_for_char(self, char, color):
        return self.font.render(char, True, COLORS[color], COLORS[BACKGROUND])
