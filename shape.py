SHAPE_OFFSETS = {
    'I': [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, -1), (0, 0), (0, 1), (0, 2)],
    ],
    'J': [
        [(0, -1), (0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, -1), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(0, -1), (0, 0), (0, 1), (1, -1)],
    ],
    'L': [
        [(2, -1), (0, 0), (1, 0), (2, 0)],
        [(0, -1), (0, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, -1), (1, -1), (1, 0), (1, 1)],
    ],
    'O': [
        [(0, -1), (1, -1), (0, 0), (1, 0)],
    ],
    'S': [
        [(1, -1), (2, -1), (0, 0), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    'T': [
        [(0, 0), (1, 0), (2, 0), (1, -1)],
        [(0, -1), (0, 0), (0, 1), (1, 0)],
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, -1), (0, 0), (1, 0), (1, 1)],
    ],
    'Z': [
        [(0, -1), (1, -1), (1, 0), (2, 0)],
        [(1, -1), (0, 0), (1, 0), (0, 1)],
    ],
}


class Shape():
    def __init__(self, shape_id, rotation, x, y, colour):
        self.shape_id = shape_id
        self.rotation = rotation
        self.x = x
        self.y = y
        self.colour = colour

    def get_tiles(self, dx = 0, dy = 0, rotation = None):
        offsets = SHAPE_OFFSETS[self.shape_id]
        
        if rotation is None:
            rotation_index = self.rotation % len(offsets)
        else:
            rotation_index = rotation % len(offsets)

        return [
            (self.x + dx + offset_x, self.y + dy + offset_y)
            for offset_x, offset_y in offsets[rotation_index]
        ]
