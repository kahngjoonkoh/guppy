import random

import chess
import pygame


class App:
    def __init__(self, debug):
        pygame.font.init()

        self.debug = debug

    def run(self):
        pygame.init()
        pygame.display.set_caption('GUI')
        program_icon = pygame.image.load("img/black_p.png")
        pygame.display.set_icon(program_icon)

        self.board = chess.Board()

    def initialize_player_side(self):
        pass

    def initialize_chess_grid_surface(self):
        pass

    def refresh_chess_grid_surface(self):
        pass

    class Piece:
        def __init__(self):
            pass

    def initialize_piece_data(self):
        pass

    def blit_pieces(self):
        pass


    def debug_msg(self, s):
        if self.debug:
            print(s)

if __name__ == "__main__":
    app = App(debug=True)
    app.run()
