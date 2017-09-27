import copy
import os
import queue
from time import sleep

import click

import gui
from dots.interpreter import AsciiDotsInterpreter
from dots.environement import Env
from dots.callbacks import IOCallbacksStorage


class CallbacksRelay(IOCallbacksStorage):
    """Stores the outputs of the interpreter untill processed."""

    def __init__(self, env):
        super().__init__(env)

        self.errors = queue.Queue()
        self._tick = None
        self.outputs = queue.Queue()
        self.inputs = queue.Queue()

        self.input_request = False
        self.finished = False

    def get_tick(self, wait=False):

        if wait:
            tick = None
            while tick is None and not self.finished:
                tick = self._tick
        else:
            tick = self._tick

        self._tick = None
        return tick

    def on_error(self, error_text):
        self.errors.put(error_text)

    def on_microtick(self, dot):
        dots = [copy.copy(d) for d in self.env.dots]
        self._tick = dots

        # we wait until somone got this tick
        while self._tick is not None and not self.finished:
            sleep(0.0001)  # could be pass but for profiler

    def on_output(self, value):
        self.outputs.put(value)
        print(value, end='')

    def on_finish(self):
        self.finished = True
        self.env.interpreter.terminate()

    def get_input(self):
        self.input_request = True
        input_ = self.inputs.get()
        self.input_request = False

        return input_


@click.command()
@click.argument('filename')
@click.argument('filename')
@click.option('--retina', default=False)
def main(filename, retina):
    try:
        env = Env()
        callbacks_relay = CallbacksRelay(env)

        with open(filename, encoding='utf-8') as f:
            prog = f.read()
        program_dir = os.path.dirname(os.path.abspath(filename))

        interpreter = AsciiDotsInterpreter(env, prog, program_dir, True)
        interpreter.run(run_in_separate_thread=True)

        debugger = gui.PygameDebugger(env, retina)
        debugger.run()
    except Exception as e:
        callbacks_relay.on_finish()
        interpreter.terminate()
        raise e


if __name__ == '__main__':
    main()
