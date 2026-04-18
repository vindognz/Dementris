import pygame
import random
from board import Board
from shape import Shape


GRID_WIDTH, GRID_HEIGHT = 10, 20
WIDTH = 400
TILE_SIZE = WIDTH // GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60
TITLE = "Dementris v2 (i cant see this bc hyprland so boo hoo)"

# IJLOSTZ
SHAPES = [
    ('I', (255, 0,   0)),
    ('J', (0,   255, 0)),
    ('L', (0,   0,   255)),
    ('O', (255, 255, 0)),
    ('S', (255, 0,   255)),
    ('T', (0,   255, 255)),
    ('Z', (255,   255, 255))
]


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
        self.unused_shapes = SHAPES.copy()
        self.current_shape = None
        self.fall_timer = 0
        self.fall_delay = 0.5

    def get_new_shape(self):
        if len(self.unused_shapes) == 0:
            self.unused_shapes = SHAPES.copy()

        shape_id, colour = random.choice(self.unused_shapes)
        self.unused_shapes.remove((shape_id, colour))

        return Shape(shape_id, 0, 4, 4, colour)
    
    def init_new_shape(self):
        self.current_shape = self.get_new_shape()
        self.current_shape.x = GRID_WIDTH // 2 - 1
        self.current_shape.y = 1

    def new(self):
        # init/reset run stuff here
        self.playing = True
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)

        self.init_new_shape()

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
        self.fall_timer += self.dt
        if self.fall_timer >= self.fall_delay:
            self.fall_timer = 0

            new_tiles = self.current_shape.get_tiles(dy=1)
            if self.board.is_shape_position_valid(new_tiles):
                self.current_shape.y += 1
            else:
                self.stamp_shape(self.current_shape)
                self.init_new_shape()

    def stamp_shape(self, shape: Shape):
        shape_tiles = shape.get_tiles()

        for x, y in shape_tiles:
            self.board.grid[y][x] = shape.colour

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

        for tilex, tiley in self.current_shape.get_tiles():
            pygame.draw.rect(self.screen, self.current_shape.colour, (tilex * TILE_SIZE, tiley * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        pygame.display.flip()

    def try_move_shape(self, dx, dy):
      new_tiles = self.current_shape.get_tiles(dx, dy)
      if self.board.is_shape_position_valid(new_tiles):
          self.current_shape.x += dx
          self.current_shape.y += dy

    def try_rotate_shape(self, dr):
        new_rotation = self.current_shape.rotation + dr
        new_tiles = self.current_shape.get_tiles(rotation=new_rotation)
        if self.board.is_shape_position_valid(new_tiles):
            self.current_shape.rotation = new_rotation

    def events(self):
        # events and all that
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_LEFT:
                        self.try_move_shape(-1, 0)
                    case pygame.K_RIGHT:
                        self.try_move_shape(1, 0)
                    case pygame.K_UP:
                        self.try_move_shape(0, -1)
                    case pygame.K_DOWN:
                        self.try_move_shape(0, 1)

                    case pygame.K_z:
                        self.try_rotate_shape(-1)
                    case pygame.K_x:
                        self.try_rotate_shape(1)
                    
                    case pygame.K_SPACE:
                        self.stamp_shape(self.current_shape)
                        self.init_new_shape()                

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
