import random
from position import Position

class Player:
    def __init__(self, map_dimensions: tuple[int, int]):
        self.map_width, self.map_height = map_dimensions
        self.x = random.randint(0, self.map_width - 1)
        self.y = random.randint(0, self.map_height - 1)

    def move(self, direction: str, map):
        target_x, target_y = self.x, self.y
        if direction == "W" and self.y > 0:
            target_y -= 1
        elif direction == "A" and self.x > 0:
            target_x -= 1
        elif direction == "S" and self.y < self.map_height - 1:
            target_y += 1
        elif direction == "D" and self.x < self.map_width - 1:
            target_x += 1

        # Check if the target tile is not "O"
        if map.get_tile(Position(target_x, target_y)) != "O":
            self.x, self.y = target_x, target_y

    def get_position(self):
        return self.x, self.y

    def update_map(self, map):
        for i in range(map.dimensions[1]):
            for j in range(map.dimensions[0]):
                tile = map.get_tile(Position(j, i))
                if tile == "P":
                    map.set_tile(Position(j, i), map.original_tiles[j + i * map.dimensions[0]])  # Restore original tile
        map.set_tile(Position(self.x, self.y), "P")  # Set new player position
