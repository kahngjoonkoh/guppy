import random
import chess
import pygame


class App:
    def __init__(self, show_info):
        pygame.font.init()

        self.show_info = show_info

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
        self.done = False

        self.player_side = None
        self.tile_on_focus = None
        self.tile_start = None
        self.tile_end = None
        self.pieces = []

    def run(self):
        pygame.init()
        pygame.display.set_caption('GUI')
        program_icon = pygame.image.load("img/black_p.png")
        pygame.display.set_icon(program_icon)

        self.board = chess.Board()

        self.initialize_player_side()
        self.info("Player Side Initialized: White" if self.player_side else "Player Side Initialized: Black")

        self.initialize_chess_grid_surface()
        self.info("Chess Grid Initialized")

        self.initialize_piece_data()
        self.info(f"{len(self.pieces)} Pieces Initialised")

        self.refresh_chess_grid_surface()
        self.info("Main Loop Started")

        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

            self.refresh_chess_grid_surface()
            pygame.display.flip()

    def initialize_player_side(self):
        self.player_side = random.choice([chess.WHITE, chess.BLACK])

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


    def info(self, s):
        if self.show_info:
            print(s)


if __name__ == "__main__":
    app = App(show_info=True)
    app.run()
