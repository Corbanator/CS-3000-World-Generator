import colorama
from position import Position, Direction
from tileset import Tileset
import copy

class Map:
    def __init__(self):
        self.tileset: Tileset
        self.dimensions: tuple[int, int]
        self.visual_tiles: list[str] = []
        self.original_tiles: list[set[str] | str] = []
        self.looping: bool = False

    @staticmethod
    def new(dimensions: tuple[int, int], tileset: Tileset, looping: bool = False):
        new_map = Map()
        new_map.dimensions = dimensions
        num_tiles = dimensions[0] * dimensions[1]
        new_map.visual_tiles = ["e" for _ in range(num_tiles)]
        new_map.original_tiles = [tileset.tiles for _ in range(num_tiles)]   # Store original tiles
        new_map.tileset = tileset
        new_map.looping = looping
        return new_map

    def set_tileset(self, tileset: Tileset):
        num_tiles = self.dimensions[0] * self.dimensions[1]
        self.visual_tiles = ["e" for _ in range(num_tiles)]
        self.original_tiles = [tileset.tiles for _ in range(num_tiles)]   # Store original tiles
        self.tileset = tileset

    def self_from_map(self, map):
        self.dimensions = map.dimensions
        self.set_tileset(map.tileset)
        self.original_tiles = map.original_tiles
        self.visual_tiles = map.visual_tiles

    def get_tile(self, pos: Position):
        x = pos.x
        y = pos.y
        if self.looping:
            x = x % self.dimensions[0]
            y = y % self.dimensions[1]
        return self.original_tiles[y * self.dimensions[0] + x]

    def get_patch(self, pos: Position, dimensions: tuple[int, int]):
        map = Map()
        map.dimensions = dimensions
        map.set_tileset(self.tileset)
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                get_tile = pos + (i, j)
                map.set_tile(Position(i, j), self.get_tile(get_tile))
        return map

    def get_self_as_map(self):
        return self.get_patch(Position(0, 0), self.dimensions)

    def apply_patch(self, pos: Position, patch_map):
        for i in range(patch_map.dimensions[0]):
            for j in range(patch_map.dimensions[1]):
                target = pos + (i, j)
                self.set_tile(target, patch_map.get_tile(Position(i, j)))


    def get_dimensions(self):
        return self.dimensions

    def set_dimensions(self, dimensions: tuple[int, int]):
        self.dimensions = dimensions

    def get_tileset(self):
        return self.tileset

    def get_visual_tile(self, pos: Position):
        x = pos.x
        y = pos.y
        if self.looping:
            x = x % self.dimensions[0]
            y = y % self.dimensions[1]
        return self.visual_tiles[y * self.dimensions[0] + x]

    def get_tile_string(self, pos: Position):
        tile = self.get_visual_tile(pos)
        if isinstance(tile, set):
            tile = "e"
        return self.tileset.colors.get(tile, colorama.Style.RESET_ALL) + tile

    def set_tile(self, pos: Position, value: str | set[str]):
        x = pos.x
        y = pos.y
        if self.looping:
            x = x % self.dimensions[0]
            y = y % self.dimensions[1]
        self.original_tiles[y * self.dimensions[0] + x] = value
        self.visual_tiles[y * self.dimensions[0] + x] = value

    def set_visual_tile(self, pos, value: str):
        x = pos.x
        y = pos.y
        if self.looping:
            x = x % self.dimensions[0]
            y = y % self.dimensions[1]
        self.visual_tiles[y * self.dimensions[0] + x] = value

    def clear_visual_tile(self, pos):
        x = pos.x
        y = pos.y
        if self.looping:
            x = x % self.dimensions[0]
            y = y % self.dimensions[1]
        self.visual_tiles[y * self.dimensions[0] + x] = self.original_tiles[y * self.dimensions[0] + x]

    def get_valid_directions(self, pos: Position):
        return_directions = set()
        if self.looping:
            return Direction.all_cardinal()
        for direction in Direction.all_cardinal():
            new_pos = pos + direction.get_tuple()
            if not (new_pos.x < 0
                    or new_pos.x >= self.dimensions[0]
                    or new_pos.y < 0
                    or new_pos.y >= self.dimensions[1]):
                return_directions.add(direction)
        return return_directions

    def tile_to_dimensions(self, new_dimensions: tuple[int, int]):
        """
            Resizes map to a new size.
            If the new dimensions are large, tesselate.
            Note: due to implementation, this clears all visual tiles
        """
        was_looping = self.looping
        self.looping = True
        new_tiles = []
        for i in range(new_dimensions[0]):
            for j in range(new_dimensions[1]):
                target = Position(i, j)
                new_tiles.append(self.get_tile(target))
        # Deeply copy the new tiles, to avoid accidentally
        # Setting original and visual tiles to the same object
        # By reference, syncing them
        self.original_tiles = copy.deepcopy(new_tiles)
        self.visual_tiles = copy.deepcopy(new_tiles)
        self.dimensions = new_dimensions
        self.looping = was_looping

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
