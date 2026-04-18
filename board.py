class Board():
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def is_tile_free(self, x, y):
        return self.grid[y][x] is None
    
    def set_tile(self, x, y, colour):
        self.grid[y][x] = colour