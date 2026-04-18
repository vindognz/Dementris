class Shape():
    def __init__(self, shape_id, rotation, x, y, colour):
        self.shape_id = shape_id
        self.rotation = rotation
        self.x = x
        self.y = y
        self.colour = colour

    def get_tiles(self, dx = 0, dy = 0):
        match self.shape_id:
            # IJLOSTZ
            case 'I':
                return [
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                    (self.x + dx + 2, self.y + dy),
                    (self.x + dx + 3, self.y + dy),
                ]
            case 'J':
                return [
                    (self.x + dx,     self.y + dy - 1),
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                    (self.x + dx + 2, self.y + dy),
                ]
            case 'L':
                return [
                    (self.x + dx + 2, self.y + dy - 1),
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                    (self.x + dx + 2, self.y + dy),
                ]
            case 'O':
                return [
                    (self.x + dx,     self.y + dy - 1),
                    (self.x + dx + 1, self.y + dy - 1),
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                ]
            case 'S':
                return [
                    (self.x + dx + 1, self.y + dy - 1),
                    (self.x + dx + 2, self.y + dy - 1),
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                ]
            case 'T':
                return [
                    (self.x + dx,     self.y + dy),
                    (self.x + dx + 1, self.y + dy),
                    (self.x + dx + 2, self.y + dy),
                    (self.x + dx + 1, self.y + dy - 1),
                ]
            case 'Z':
                return [
                    (self.x + dx,     self.y + dy - 1),
                    (self.x + dx + 1, self.y + dy - 1),
                    (self.x + dx + 1, self.y + dy),
                    (self.x + dx + 2, self.y + dy),
                ]
