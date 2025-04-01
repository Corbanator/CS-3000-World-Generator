class Player:
    def __init__(self, start_x: int, start_y: int, map_dimensions: tuple[int, int]):
        self.x = start_x
        self.y = start_y
        self.map_width, self.map_height = map_dimensions

    def move(self, direction: str):
        if direction == "W" and self.y > 0:
            self.y -= 1
        elif direction == "A" and self.x > 0:
            self.x -= 1
        elif direction == "S" and self.y < self.map_height - 1:
            self.y += 1
        elif direction == "D" and self.x < self.map_width - 1:
            self.x += 1

    def get_position(self):
        return self.x, self.y

    def update_map(self, map):
        for i in range(map.dimensions[1]):
            for j in range(map.dimensions[0]):
                tile = map.get_tile(j, i)
                if tile == "P":
                    map.set_tile(j, i, map.original_tiles[j + i * map.dimensions[0]])  # Restore original tile
        map.set_tile(self.x, self.y, "P")  # Set new player position
