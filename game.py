import pygame
from board import Board

GRID_WIDTH, GRID_HEIGHT = 10, 20
WIDTH = 400
TILE_SIZE = WIDTH // GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60
TITLE = "Dementris"


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()
        self.load_assets()
        self.running = True
        self.playing = False
        self.dt = 0

    def new(self):
        # init/reset run stuff here
        self.playing = True
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.board.set_tile(3, 5, (255, 0, 0))
        self.board.set_tile(4, 5, (255, 0, 0))
        self.board.set_tile(5, 5, (255, 0, 0))
        self.board.set_tile(4, 4, (255, 0, 0))

    def load_assets(self):
        # load all assets (sounds, images, etc.)
        self.font = pygame.font.SysFont(None, 32)
        # self.font = pygame.font.Font('path', size)

    def run(self):
        # main game loop
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        # update game stuff
        pass

    def draw(self):
        # draw everything
        self.screen.fill((0, 0, 0))

        for row in range(self.board.height):
            for col in range(self.board.width):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                tile = self.board.grid[row][col]

                if tile is not None:
                    pygame.draw.rect(self.screen, tile, (x, y, TILE_SIZE, TILE_SIZE))
                
                pygame.draw.rect(self.screen, (80, 80, 80), (x, y, TILE_SIZE, TILE_SIZE), 1)


        pygame.display.flip()

    def events(self):
        # events and all that
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False


    def wait_for_key_screen(self, title: pygame.Surface, subtitle: pygame.Surface):
        waiting = True
        title_rect = None
        subtitle_rect = None

        if title:
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        if subtitle:
            subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + HEIGHT // 20))

        while waiting and self.running:
            self.dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
            
            self.screen.fill((50, 50, 50))
            if title:
                self.screen.blit(title, title_rect)
            if subtitle:
                self.screen.blit(subtitle, subtitle_rect)
            pygame.display.flip()


    def show_start_screen(self):
        # title screen
        prompt = self.font.render("Press any key to start!", True, (255, 255, 255))
        self.wait_for_key_screen(prompt, None)

    def show_go_screen(self):
        # game over screen or restart or smth

        pass

if __name__ == "__main__":
    print("doofus. run main.py.")
