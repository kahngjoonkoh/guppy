import logging
import sys
import time
from threading import *

import chess

import guppy
import argparse

# To disable buffering in inputs/outputs.
# 'python -u uci.py'
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def output(line):
    print(line, file=sys.stdout)
    logging.debug(line)


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('Move Overhead',
    #                     help='Assume a time delay of x ms due to network and GUI overheads. This is useful to avoid losses on time in those cases.',
    #                     type=int, default=0, nargs='?')
    # arg_dict = vars(parser.parse_args())
    # move_overhead = arg_dict['Move Overhead'] if 'Move Overhead' in arg_dict.keys() else 0

    # INIT
    logging.basicConfig(filename='guppy.log', level=logging.DEBUG)

    engine = guppy.Engine()
    show_thinking = True
    stack = []

    def threaded_search():
        engine.halt = False
        ponder = None
        depth_limit_present = True
        depth_limit = 100

        node_limit_present = False
        node_limit = 0

        time_limit_present = True
        time_limit = -1

        wtime, btime = 200000, 200000  # think for 5 seconds. 5000 * 40
        winc, binc = 0, 0
        movestogo = None

        params = cmd.split(' ')
        if 'searchmoves' in params:
            pass
        if 'ponder' in params:
            pass
        if 'wtime' in params:
            time_limit_present = True
            wtime = int(params[params.index('wtime') + 1])
        if 'btime' in params:
            time_limit_present = True
            btime = int(params[params.index('btime') + 1])
        if 'winc' in params:
            time_limit_present = True
            winc = int(params[params.index('winc') + 1])
        if 'binc' in params:
            time_limit_present = True
            binc = int(params[params.index('binc') + 1])
        if 'movestogo' in params:
            movestogo = int(params[params.index('movestogo') + 1])
        if 'depth' in params:
            depth_limit_present = True
            depth_limit = int(params[params.index('depth') + 1])
        if 'nodes' in params:
            node_limit_present = True
            node_limit = int(params[params.index('nodes') + 1])
        if 'movetime' in params:
            time_limit_present = True
            time_limit = int(params[params.index('movetime') + 1])

        # TODO: implement 'stop' feature
        if 'infinite' in params:
            depth_limit_present = False
            node_limit_present = False
            time_limit_present = False

        # statistical average of moves taken per game.
        av_ply = 40

        start_time = time.time()
        turn = engine.board.turn
        time_left, inc, moves_made = (wtime, winc, engine.w_moves) if turn == chess.WHITE else (
            btime, binc, engine.b_moves)


        time_control = int((time_left / (av_ply - moves_made + 1)) + inc)
        if movestogo != None:
            time_control = int((time_left / (movestogo + 1)) + inc)

        def check_for_halt():
            while not engine.halt:
                elapsed = int((time.time() - start_time) * 1000)
                if depth_limit_present:
                    if depth > depth_limit:
                        engine.halt = True
                        logging.debug('*depth_limit')
                        break
                if node_limit_present:
                    if nodes > node_limit:
                        engine.halt = True
                        logging.debug('*node_limit')
                        break
                if time_limit_present:
                    if 0 < time_limit < elapsed:
                        engine.halt = True
                        logging.debug(f"*time_limit {time_limit} elapsed {elapsed}")
                        break
                    # TODO Zero Error incident
                    if elapsed > time_control:
                        engine.halt = True
                        logging.debug(f"*time_limit {time_control} elapsed {elapsed}")
                        break

        for depth, qdepth, score, nodes, move in engine.think():
            elapsed = int((time.time() - start_time) * 1000)
            if show_thinking and not engine.halt:
                    output(f"info depth {depth} seldepth {qdepth} score cp {score} time {elapsed} nodes {nodes} pv {move}")
            if depth >= 2:
                t = Thread(target=check_for_halt)
                t.start()

        moves = engine.return_bestmove()
        if len(moves) > 1:
            output(f"bestmove {moves[0]} ponder {moves[1]}")
        else:
            output(f"bestmove {moves[0]}")

    while True:
        if stack:
            cmd = stack.pop()
        else:
            try:
                cmd = input()
            except Exception as e:
                logging.debug(e)
                break

        logging.debug(f">>>> {cmd}")

        if cmd == 'quit':
            engine.halt = True
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

        # TODO: when invoked, engine should reset chess.board
        elif cmd == 'ucinewgame':
            stack.append(f"position startpos")

        # TODO
        elif cmd.startswith('position'):
            params = cmd.split(' ')

            # Slightly different splitting because FEN has spaces.
            index = cmd.find('moves')

            # If 'moves' parameter exists.
            if index >= 0:
                moves = cmd[index:].split()[1:]
            else:
                moves = []

            # If FEN is given.
            if params[1] == 'fen':
                if index >= 0:
                    fen = cmd[:index].split(' ', 2)[2]
                else:
                    fen = cmd.split(' ', 2)[2]

            # To setup initial position.
            elif params[1] == 'startpos':
                fen = engine.INITIAL_FEN

            else:
                pass

            engine.set_position(fen, moves)

        # TODO: WORK HERE
        elif cmd.startswith('go'):
            thread = Thread(target=threaded_search)
            thread.start()

        # TODO
        elif cmd == 'stop':
            engine.halt = True
            break

        # TODO
        elif cmd == 'ponderhit':
            pass

        # Game has ended
        elif engine.board.outcome() != None:
            engine.halt = True
            break

        else:
            pass


if __name__ == "__main__":
    sys.stdout = Unbuffered(sys.stdout)
    main()
