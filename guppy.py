import os
import sys
from collections import OrderedDict
from ctypes import *

import chess
import chess.polyglot


class Node:
    def __init__(self, lower, upper):
        self.upper_bound = upper
        self.lower_bound = lower


# LRU (Least Recently Used)
class LRUCache:
    # initialising capacity
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


class Engine:
    def __init__(self):
        # BOARD INIT
        self.INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.board = chess.Board()

        # NNUE INIT
        nnue_net_SHA256 = ["vdv", "48ada89402c9", "686c406dde55", "48ada89402c9", "d7a33434b6cc", "371e294c6117",
                           "757def5fff5e", "a9f9e868162a", "0e698aa9eb8b", "04cf2b4ed1da"]

        PATH = os.path.relpath(os.path.dirname(sys.argv[0]), os.getcwd())
        nnue_location = os.path.join(PATH, 'nnue\\libnnueprobe.exe')
        net_location = os.path.join(PATH, f'nnue\\networks\\nn-{nnue_net_SHA256[1]}.nnue')

        self.nnue = cdll.LoadLibrary(nnue_location)
        self.nnue.nnue_init(bytes(net_location, 'UTF-8'))

        # TODO: Compare performance for each NNUE

        # NNUE networks from StockFish Neural Net Repository
        # 48ada89402c9 -> author: vdv 21-05-01 16:35:42 -> Makes frequent queen blunders.
        # 686c406dde55 -> author: Fisherman 21-04-01 18:09:20 -> Cannot force mate
        # 48ada89402c9 -> author: MichaelB7 21-03-30 21:05:03
        # d7a33434b6cc -> author: Fisherman 21-03-29 23:27:55
        # 371e294c6117 -> author: MichaelB7 21-03-27 05:52:36
        # 757def5fff5e -> author: Fisherman 21-03-22 02:31:17
        # a9f9e868162a -> author: Fisherman 21-03-20 23:34:03
        # 0e698aa9eb8b -> author: MiauiKatze 21-02-23 08:49:58
        # 04cf2b4ed1da -> author: vdv 20-10-12 05:22:36 -> knight blunders

        # CHESS VARIABLE/CONSTANTS INIT
        self.nodes = 0
        self.qdepth = 0
        self.w_moves = 0
        self.b_moves = 0

        self.CACHE_LIMIT = 20000
        self.INFINITY = 10000
        # Average game takes 40 moves to finish = 80 plies
        self.MAX_SEARCH_DEPTH = 100
        # Evaluation adjustment
        self.ADJUST = 0

        self.mate = False

        self.score_cache = LRUCache(10000)
        self.moves = {}
        self.best_move = None

        self.halt = False

    def set_position(self, fen, moves):
        self.board = chess.Board(fen)
        self.w_moves, self.b_moves = 0, 0
        for move in moves:
            self.add_move_counter()
            # TODO: check if any errors with promotion.
            self.board.push(chess.Move.from_uci(move))

    # TODO BOOK MOVES
    # distinguish time utilisation for early, mid, end games.
    # Transition from engine.halt in a separate thread to internal break.
    # add ponder
    # seldepth is greater than it should be.
    # near the end game it should have more depth not seldepth.
    # Create another counter for saving best moves so far. (without discarding all the ply)
    # Create UCI wrapper w/o threads
    # Move sort only when root.

    #TODO ENGINE MISSES MATE IN 1. BECAUSE THE EVALUATION FUNCTION DOES NOT GIVE MATE AS VALUE.
    # Implement mate score in evaluation function
    # Currently does not avoid mates as well.
    # FIX ISSUES WITH DETECTING MATE
    # BAD AT ENDGAMES
    # EVALUATION is different for each even and odd depth.
    # TODO: Needs to find the fastest mate path.
    def think(self):
        self.nodes = 0
        fg = 0
        alpha = -self.INFINITY
        beta = self.INFINITY
        self.mate = False

        for depth in range(1, self.MAX_SEARCH_DEPTH):
            self.qdepth = 0
            if self.mate:
                break
            fg = self.MTDF(True, fg, depth)
            if not self.halt:
                self.best_move = self.moves[self.board.fen()] # best move fallback
            else:
                break
            if abs(fg) >= 9900:
                score = fg if self.board.turn == chess.WHITE else -fg
            else:
                score = int(fg/2.56) if self.board.turn == chess.WHITE else -int(fg/2.56)
            yield depth, depth + self.qdepth, score, self.nodes, self.best_move
        self.halt = True

    def MTDF(self, root, fg, depth):
        g = fg
        upper_bound = self.INFINITY
        lower_bound = -self.INFINITY
        while lower_bound < upper_bound - self.ADJUST:
            beta = max(g, lower_bound + 1)
            maximise = True if self.board.turn == chess.WHITE else False
            g = self.alphabeta_with_memory(root, beta - 1, beta, depth, False, maximise, 0)
            if not self.halt:
                if g < beta:
                    upper_bound = g
                else:
                    lower_bound = g
            else:
                break
        return g

    # with quiesce
    def alphabeta_with_memory(self, root, alpha, beta, depth, quiet, maximise, i):
        self.nodes += 1

        if self.halt:
            return 0

        if self.board.is_checkmate():
            return -self.INFINITY if self.board.turn == chess.WHITE else self.INFINITY

        if self.board.is_stalemate() or self.board.is_repetition() or self.board.is_insufficient_material() or self.board.is_fifty_moves():
            return 0

        depth = max(depth, 0)

        # transposition lookup
        n = self.score_cache.get((root, self.board.fen(), depth, maximise))
        if n != None:  # Matching n value found.
            if n.lower_bound >= beta:
                return n.lower_bound
            if n.upper_bound <= alpha:
                return n.upper_bound
            alpha = max(alpha, n.lower_bound)
            beta = min(beta, n.upper_bound)
        else:
            n = Node(-self.INFINITY, self.INFINITY)

        if depth == 0:
            if quiet:  # Leaf node in quiet position
                self.qdepth = max(self.qdepth, i)
                return self.evaluate_board()
            else:
                i += 1
        legals = self.board.legal_moves
        # TODO: Make negamax approach.
        # TODO: WHite starts the blunders.
        if maximise:
            g = -self.INFINITY
            # sorting is less efficient than going through all the possible branches.
            if root:
                legals = sorted(legals, key=lambda legal_move: self.move_value(legal_move), reverse=True)
            for move in legals:
                q = self.is_quiet(move)
                a = alpha
                self.board.push(move)
                g = max(g, self.alphabeta_with_memory(False, a, beta, depth - 1, q, not maximise, i))
                a = max(a, g)
                self.board.pop()
                if g >= beta:
                    if not self.halt:
                        self.moves[self.board.fen()] = move
                        if g == self.INFINITY:
                            self.mate = True
                        break
        else:  # if minimise
            g = self.INFINITY
            b = beta
            if root:
                legals = sorted(legals, key=lambda legal_move: self.move_value(legal_move), reverse=False)
            for move in legals:
                q = self.is_quiet(move)
                self.board.push(move)
                g = min(g, self.alphabeta_with_memory(False, alpha, b, depth - 1, q, not maximise, i))
                b = min(b, g)
                self.board.pop()
                if g <= alpha:
                    if not self.halt:
                        self.moves[self.board.fen()] = move
                        if g == -self.INFINITY:
                            self.mate = True
                    break
        if not self.halt:
            # When fail-low.
            if g <= alpha:
                n.upper_bound = g

            elif g > alpha and g < beta:
                n.lower_bound = g
                n.upper_bound = g

            # When fail-high.
            elif g >= beta:
                n.lower_bound = g

            # Stores bounds.
            self.score_cache.put((root, self.board.fen(), depth, maximise), n)
        return g

    def is_quiet(self, move):
        return False if self.board.is_capture(move) or self.board.gives_check(move) else True

    def evaluate_board(self):
        fen = self.board.fen()
        score = self.nnue.nnue_evaluate_fen(fen.encode('UTF-8'))
        return score if self.board.turn == chess.WHITE else -score

    # # used when sorting legal moves in best possible move order.
    def move_value(self, move):
        self.board.push(move)
        val = self.evaluate_board()
        self.board.pop()
        return val

    # Also makes the move on the internal chess board.
    def return_bestmove(self):
        self.add_move_counter()
        # bestmove = self.moves[self.board.fen()]
        # self.board.push(bestmove)
        # TODO: Implement move pondering

        # self.board.push(bestmove)
        # ponder = self.moves.get(self.board.fen(), None)
        # return [bestmove, ponder] if ponder != None else [bestmove]
        self.board.push(self.best_move)

        print(self.board)
        print("White's turn to move" if self.board.turn == chess.WHITE else "Black's turn to move")
        return [self.best_move]

    def add_move_counter(self):
        # leave time for at least 10 moves
        if self.board.turn == chess.WHITE:
            self.w_moves = min(self.w_moves + 1, 30)
        else:
            self.b_moves = min(self.b_moves + 1, 30)
