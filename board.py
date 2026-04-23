class Board():
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def is_tile_free(self, x, y):
        return self.grid[y][x] is None
    
    def set_tile(self, x, y, colour):
        self.grid[y][x] = colour

    def is_shape_position_valid(self, shape_positions):
        return all(
            0 <= x < self.width
            and 0 <= y < self.height
            and self.is_tile_free(x, y)
            for x, y in shape_positions
    )

    def find_full_rows(self): # holy clean btw
        return [
            i
            for i, row in enumerate(self.grid)
            if all(row)
        ]
    
    def clear_full_rows(self):
        new_grid = [row for row in self.grid if not all(row)]
        cleared = self.height - len(new_grid)

        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(self.width)])

        self.grid = new_grid
        return cleared
