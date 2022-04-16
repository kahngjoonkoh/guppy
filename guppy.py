import random
from ctypes import *

import chess
import chess.polyglot

nnue = cdll.LoadLibrary("./nnue/libnnueprobe.exe")
nnue.nnue_init(b"nnue/networks/nn-vdv.nnue")


def evaluate_score(board, to_centipawn=True):
    fen = board.fen()
    score = nnue.nnue_evaluate_fen(fen.encode('UTF-8'))
    score = score / 100 if to_centipawn else score

    return score if board.turn == chess.WHITE else -score


def move_value(board, move):
    board.push(move)
    val = evaluate_score(board)
    board.pop()
    return val


def generate_move(board, depth, maximize):
    legals = board.legal_moves
    bestMove = None
    bestValue = -99999 if maximize else 99999
    book_moves = generate_book_moves(board)
    if book_moves != []:
        random_book_move = random.choice(book_moves)
        if random_book_move in legals:
            board.push(random_book_move)
            book_val = evaluate_score(board)
            board.pop()
            return (random_book_move, book_val)
    else:
        for move in legals:
            board.push(move)
            value = alphaBeta(board, depth - 1, -99999, 99999, not maximize)
            board.pop()
            if maximize:
                if value > bestValue:
                    bestValue = value
                    bestMove = move
            else:
                if value < bestValue:
                    bestValue = value
                    bestMove = move
        return (bestMove, bestValue)


def generate_book_moves(board):
    book_moves = []
    bin_file = "datatables/book_moves/Balsa_v110221.bin"
    with chess.polyglot.open_reader(bin_file) as reader:
        for entry in reader.find_all(board):
            book_moves.append(entry.move)
    return book_moves


def alphaBeta(board, depth, alpha, beta, maximize):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -10000
        else:
            return 10000
    if board.is_stalemate():
        return 0

    if depth == 0:
        return evaluate_score(board)

    legals = board.legal_moves

    if maximize:
        bestVal = -99999
        # legals = sorted(legals, key=lambda legal_move: move_value(board, legal_move), reverse=True)
        for move in legals:
            board.push(move)
            bestVal = max(bestVal, alphaBeta(board, depth - 1, alpha, beta, not maximize))
            board.pop()
            alpha = max(alpha, bestVal)
            if alpha >= beta:
                return bestVal
        return bestVal
    else:
        # legals = sorted(legals, key=lambda legal_move: move_value(board, legal_move), reverse=True)
        bestVal = 99999
        for move in legals:
            board.push(move)
            bestVal = min(bestVal, alphaBeta(board, depth - 1, alpha, beta, not maximize))
            board.pop()
            beta = min(beta, bestVal)
            if beta <= alpha:
                return bestVal
        return bestVal


