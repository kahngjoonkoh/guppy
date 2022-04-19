import ctypes
import random
import time
from tkinter import *

import chess
import pygame

import guppy
import guppy as engine


class App:
    def __init__(self, show_info, play_as=None):
        pygame.font.init()

        self.show_info = show_info
        self.play_as = play_as

        # CONSTANTS
        self.FONT_SIZE = 12
        self.FONT = pygame.font.Font(pygame.font.get_default_font(), self.FONT_SIZE)
        self.WHITE = (238, 238, 210)
        self.BLACK = (118, 150, 86)
        self.TILE_SIZE = 60
        self.TEXT_MARGIN = 1

        # SCREENS
        self.screen = pygame.display.set_mode((8 * self.TILE_SIZE, 8 * self.TILE_SIZE))
        self.chess_grid_surface = pygame.Surface((8 * self.TILE_SIZE, 8 * self.TILE_SIZE))

        # CHESS VARIABLES
        self.board = None
        self.done = False

        self.player_side = None
        self.tile_on_focus = None
        self.pieces = []
        self.hist = []
        self.time_start = 0
        self.promotion_piece = None

    def run(self):
        pygame.init()
        pygame.display.set_caption('GUI')
        program_icon = pygame.image.load("img/black_p.png")
        pygame.display.set_icon(program_icon)

        self.board = chess.Board()

        self.initialize_player_side()

        self.initialize_chess_grid_surface()

        self.set_piece_data()

        self.blit_pieces()

        self.refresh_chess_grid_surface()

        self.info("Main Loop Started")

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN and self.board.turn == self.player_side:
                    self.tile_on_focus = self.get_tile_under_mouse(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and self.board.turn == self.player_side:
                    self.make_move(f"{self.tile_on_focus}{self.get_tile_under_mouse(event.pos)}", 'string')
                    self.tile_on_focus = None

            if self.board.turn != self.player_side:
                self.make_engine_move()
            if self.board.outcome() == None:
                self.refresh_chess_grid_surface()
            else:
                self.blit_pieces()
                self.refresh_chess_grid_surface()
                self.display_outcome_message()

            pygame.display.flip()

    def initialize_player_side(self):
        self.player_side = random.choice([chess.WHITE, chess.BLACK])
        if self.play_as != None:
            self.player_side = self.play_as
        self.info("Player Side Initialized: White" if self.player_side else "Player Side Initialized: Black")

    def initialize_chess_grid_surface(self):
        text_margin = 1
        self.chess_grid_surface.fill(self.WHITE)
        for x in range(1, 9, 2):
            for y in range(0, 8, 2):
                pygame.draw.rect(self.chess_grid_surface, self.BLACK,
                                 (x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
        for x in range(0, 8, 2):
            for y in range(1, 9, 2):
                pygame.draw.rect(self.chess_grid_surface, self.BLACK,
                                 (x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))

        if self.player_side == chess.WHITE:
            for x, file in enumerate("abcdefgh"):
                if x % 2 == 0:
                    temp_text = self.FONT.render(file, True, self.WHITE)
                else:
                    temp_text = self.FONT.render(file, True, self.BLACK)
                self.chess_grid_surface.blit(temp_text,
                                             ((x + 1) * self.TILE_SIZE - self.FONT_SIZE - self.TEXT_MARGIN,
                                              8 * self.TILE_SIZE - self.FONT_SIZE - self.TEXT_MARGIN))
            for y in [8, 7, 6, 5, 4, 3, 2, 1]:
                if y % 2 == 1:
                    temp_text = self.FONT.render(str(y), True, self.WHITE)
                else:
                    temp_text = self.FONT.render(str(y), True, self.BLACK)
                self.chess_grid_surface.blit(temp_text, (self.TEXT_MARGIN, (8 - y) * self.TILE_SIZE + self.TEXT_MARGIN))
        elif self.player_side == chess.BLACK:
            for x, file in enumerate("hgfedcba"):
                if x % 2 == 0:
                    temp_text = self.FONT.render(file, True, self.WHITE)
                else:
                    temp_text = self.FONT.render(file, True, self.BLACK)
                self.chess_grid_surface.blit(temp_text,
                                             ((x + 1) * self.TILE_SIZE - self.FONT_SIZE - self.TEXT_MARGIN,
                                              8 * self.TILE_SIZE - self.FONT_SIZE - self.TEXT_MARGIN))
            for y in range(0, 8):
                if y % 2 == 1:
                    temp_text = self.FONT.render(str(y + 1), True, self.WHITE)
                else:
                    temp_text = self.FONT.render(str(y + 1), True, self.BLACK)
                self.chess_grid_surface.blit(temp_text, (self.TEXT_MARGIN, y * self.TILE_SIZE + self.TEXT_MARGIN))

        self.info("Chess Grid Initialized")

    def set_piece_data(self):
        self.pieces = []
        fen = self.board.fen()
        temp = fen.split(" ")
        position = temp.pop(0)
        for y, row in enumerate(position.split("/")):
            rank = 8 - y
            new_position_string = ""
            for char in row:
                try:
                    new_position_string += "." * int(char)
                except ValueError:
                    new_position_string += char

            for x, type in enumerate(new_position_string):
                file = 'abcdefgh'[x]
                if type != ".":
                    if type.isupper():
                        type = f"white_{type}"
                    else:
                        type = f"black_{type}"
                    pos = f"{file}{rank}"

                    self.pieces.append(self.Piece(self, type, pos))

    def refresh_chess_grid_surface(self):
        self.screen.blit(self.chess_grid_surface, self.chess_grid_surface.get_rect())
        self.blit_pieces()

    class Piece:
        def __init__(self, parent, type, filerank):
            self.parent = parent
            self.type = type
            self.colour = self.get_colour()
            self.filerank = filerank
            self.file = filerank[0]
            self.rank = int(filerank[1])
            self.image = pygame.image.load(f"img/{self.type}.png")
            self.xy = self.get_xy()

        def get_xy(self):
            files = "abcdefgh"
            if self.parent.player_side == chess.BLACK:
                return ((7 - files.index(self.file)) * self.parent.TILE_SIZE, (self.rank - 1) * self.parent.TILE_SIZE)
            elif self.parent.player_side == chess.WHITE:
                return (files.index(self.file) * self.parent.TILE_SIZE, (8 - self.rank) * self.parent.TILE_SIZE)

        def get_colour(self):
            if str(self.type).isupper():
                return chess.WHITE
            else:
                return chess.BLACK

    def make_engine_move(self):
        self.time_start = time.time()
        depth = 2
        qsearch = True
        if not self.player_side == chess.WHITE:
            move_val = engine.generate_move(self.board, depth, True, qsearch)
        elif not self.player_side == chess.BLACK:
            move_val = engine.generate_move(self.board, depth, False, qsearch)
        if self.board.outcome() == None:
            # random_move = random.choice([move for move in self.board.legal_moves])
            # self.make_move(random_move, "move")
            self.make_move(move_val[0], "move")

        # searcher = engine.Searcher()
        # start = time.time()
        # for _depth, move, score in searcher.search(hist[-1], hist):
        #     if time.time() - start > 1:
        #         break
        # make_move(move, "move")
        # hist.append(hist[-1].move(move))

    def blit_pieces(self):
        for piece in self.pieces:
            if self.tile_on_focus == piece.filerank:
                mouse_pos = pygame.mouse.get_pos()
                center = (mouse_pos[0] - self.TILE_SIZE / 2, mouse_pos[1] - self.TILE_SIZE / 2)
                self.screen.blit(piece.image, center)
            else:
                self.screen.blit(piece.image, piece.xy)

    def get_tile_under_mouse(self, pos):
        x = pos[0] // self.TILE_SIZE
        y = pos[1] // self.TILE_SIZE
        if self.player_side == chess.WHITE:
            file_order = "abcdefgh"
            rank_order = "87654321"
        elif self.player_side == chess.BLACK:
            file_order = "hgfedcba"
            rank_order = "12345678"
        return f"{file_order[x]}{rank_order[y]}"

    def make_move(self, s, format):
        try:
            if format == "move":
                move = s
            elif format == "string":
                move = chess.Move.from_uci(s)
                if self.player_side == chess.WHITE:
                    if chess.square_rank(move.to_square) == 7 and self.board.piece_type_at(move.from_square) == 1:
                        self.promote(chess.WHITE)
                        move.promotion = self.promotion_piece
                if self.player_side == chess.BLACK:
                    if chess.square_rank(move.to_square) == 0 and self.board.piece_type_at(
                            move.from_square) == chess.PAWN:
                        self.promote(chess.BLACK)
                        move.promotion = self.promotion_piece

            if move in self.board.legal_moves:
                if (self.board.turn == chess.WHITE) and (self.player_side == chess.WHITE):
                    self.info(f"\n{move}: {guppy.move_value(self.board, move)}")
                elif (self.board.turn == chess.WHITE) and (self.player_side == chess.BLACK):
                    self.info(
                        f"\n{move}: {guppy.move_value(self.board, move)} (elapsed: {time.time() - self.time_start:.2f}s)")
                elif (self.board.turn == chess.BLACK) and (self.player_side == chess.WHITE):
                    self.info(
                        f"{move}: {guppy.move_value(self.board, move)} (elapsed: {time.time() - self.time_start:.2f}s)")
                elif (self.board.turn == chess.BLACK) and (self.player_side == chess.BLACK):
                    self.info(f"{move}: {guppy.move_value(self.board, move)}")
                else:
                    print(self.board.turn, self.player_side)
                self.board.push(move)
                self.set_piece_data()
                self.hist.append(self.board.fen())

        except ValueError:
            pass

    def promote(self, c):
        global promotion_window
        small_font = ("helvetica", 20)
        promotion_window = Tk()
        promotion_window.title("Select")
        promotion_window.geometry("207x55")
        promotion_window.resizable(False, False)
        promotion_piece = chess.QUEEN
        if c == chess.WHITE:
            Button(promotion_window, text="♘", font=small_font,
                   command=lambda p=chess.KNIGHT, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=1)
            Button(promotion_window, text="♗", font=small_font,
                   command=lambda p=chess.BISHOP, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=2)
            Button(promotion_window, text="♖", font=small_font,
                   command=lambda p=chess.ROOK, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=3)
            Button(promotion_window, text="♕", font=small_font,
                   command=lambda p=chess.QUEEN, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=4)

        elif c == chess.BLACK:
            Button(promotion_window, text="♞", font=small_font,
                   command=lambda p=chess.KNIGHT, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=1)
            Button(promotion_window, text="♝", font=small_font,
                   command=lambda p=chess.BISHOP, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=2)
            Button(promotion_window, text="♜", font=small_font,
                   command=lambda p=chess.ROOK, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=3)
            Button(promotion_window, text="♛", font=small_font,
                   command=lambda p=chess.QUEEN, root=promotion_window: self.promote_to(p, root)).grid(row=0, column=4)

        promotion_window.mainloop()

    def promote_to(self, p, root):
        self.promotion_piece = p
        root.destroy()

    def display_outcome_message(self):
        outcome = self.board.outcome()
        termination = str(outcome.termination)[12:].capitalize()
        prompt = None
        title = None
        if outcome.winner == None:
            prompt = f"Draw by {termination}\n Rematch?"
            title = "Draw!"
        elif outcome.winner:
            prompt = f"White wins by {termination}\n Rematch?"
            title = "White wins!"
        elif not outcome.winner:
            prompt = f"Black wins by {termination}\n Rematch?"
            title = "Black wins!"

        user_choice = ctypes.windll.user32.MessageBoxW(0, prompt, title, 4)
        if user_choice == 6:  # ID YES
            self.board = chess.Board()
            self.tile_on_focus = None
            self.pieces = []
            self.hist = []
            self.promotion_piece = None

            self.initialize_player_side()
            self.set_piece_data()
            self.blit_pieces()
            self.refresh_chess_grid_surface()

        elif user_choice == 7:  # ID NO
            quit()

    def info(self, s):
        if self.show_info:
            print(s)


if __name__ == "__main__":
    app = App(show_info=True, play_as=chess.BLACK)
    app.run()
