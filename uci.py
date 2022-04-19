import sys
import logging
import argparse

# To disable buffering in inputs/outputs.
# 'python -u uci.py'
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        sys.stderr.write(data)
        sys.stderr.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def main():
    # Logging initialised
    logging.basicConfig(filename='guppy.log', level=logging.DEBUG)
    sys.stdout = Unbuffered(sys.stdout)

    def output(line):
        print(line, file=sys.stdout)
        logging.debug(line)

    # input stack initialised
    stack = []
    # take stdinputs until 'quit'
    while True:
        if stack:
            cmd = stack.pop()
        else:
            cmd = input()

        logging.debug(f">>>> {cmd}")

        if cmd == 'quit':
            break

        elif cmd == 'uci':
            output("id name Guppy")
            output("id author Kahngjoon Koh")
            output("uciok")

        # TODO
        elif cmd == 'debug':
            pass

        # TODO
        elif cmd == 'isready':
            output("readyok")

        # TODO
        elif cmd == 'setoption':
            pass

        # TODO
        elif cmd == 'register':
            pass

        # TODO
        elif cmd == 'ucinewgame':
            stack.append(f"position fen {guppy.board.fen()}")

        #TODO
        elif cmd.startswith('position'):
            pass

        # TODO
        elif cmd.startswith('go'):
            pass

        #TODO
        elif cmd == 'stop':
            pass

        #TODO
        elif cmd == 'ponderhit':
            pass

        else:
            pass

if __name__ == "__main__":
    main()
