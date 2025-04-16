import colorama
from position import Position, Direction
from tileset import Tileset

class Map:
    def __init__(self, dimensions: tuple[int, int], tileset: Tileset):
        self.dimensions = dimensions
        num_tiles = dimensions[0] * self.dimensions[1]
        self.tiles: list[set[str] | str] = [tileset.tiles for _ in range(num_tiles)]
        self.original_tiles: list[str] = ["e" for _ in range(num_tiles)]  # Store original tiles
        self.tileset = tileset

    def get_tile(self, pos: Position):
        return self.tiles[pos.y * self.dimensions[0] + pos.x]

    def get_tile_string(self, pos: Position):
        tile = self.tiles[pos.y * self.dimensions[0] + pos.x]
        if isinstance(tile, set):
            tile = "e"
        return self.tileset.colors.get(tile, colorama.Style.RESET_ALL) + tile

    def set_tile(self, pos: Position, value: str | set[str]):
        self.tiles[pos[1] * self.dimensions[0] + pos[0]] = value
        if value != "P":  # Update original tiles only if not setting the player
            self.original_tiles[pos.y * self.dimensions[0] + pos.x] = value

    def get_valid_directions(self, pos: Position):
        return_directions = set()
        for direction in Direction.all_cardinal():
            new_pos = pos + direction.get_tuple()
            if not (new_pos.x < 0
                    or new_pos.x >= self.dimensions[0]
                    or new_pos.y < 0
                    or new_pos.y >= self.dimensions[1]):
                return_directions.add(direction)
        return return_directions

    # sets tiles in grid
    def __str__(self):
        return_string = ""
        for i in range(self.dimensions[1]):
            for j in range(self.dimensions[0]):
                return_string += self.get_tile_string(Position(j, i))
            # Avoid trailing newline
            if i != self.dimensions[1] - 1:
                return_string += "\n"
        return_string += colorama.Style.RESET_ALL
        return return_string

    def print_debug(self):
        return_string = ""
        for i in range(self.dimensions[1]):
            for j in range(self.dimensions[0]):
                return_string += str(self.get_tile(Position(j, i)))
            # Avoid trailing newline
            if i != self.dimensions[1] - 1:
                return_string += "\n"
        print(return_string)
