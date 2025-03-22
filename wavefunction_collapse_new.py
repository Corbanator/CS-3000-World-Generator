import random
from enum import IntEnum


class Direction(IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7

    def opposite(self):
        return Direction((self + 4) % 8)

    def clockwise_turn(self):
        return Direction((self + 2) % 8)

    def counter_clockwise_turn(self):
        return Direction((self + 6) % 8)

    def get_tuple(self):
        match self:
            case Direction.N: return (0, -1)
            case Direction.NE: return (1, -1)
            case Direction.E: return (1, 0)
            case Direction.SE: return (1, 1)
            case Direction.S: return (0, 1)
            case Direction.SW: return (-1, 1)
            case Direction.W: return (-1, 0)
            case Direction.NW: return (-1, -1)


def main():
    tileset = {"L", "B", "O"}
    rules: dict[str, dict[Direction, set[str]]] = {
        "L": {
            Direction.N: {"L", "B"},
            Direction.E: {"L", "B"},
            Direction.S: {"L", "B"},
            Direction.W: {"L", "B"},
        },
        "B": {
            Direction.N: {"L", "B", "O"},
            Direction.E: {"L", "B", "O"},
            Direction.S: {"L", "B", "O"},
            Direction.W: {"L", "B", "O"},
        },
        "O": {
            Direction.N: {"B", "O"},
            Direction.E: {"B", "O"},
            Direction.S: {"B", "O"},
            Direction.W: {"B", "O"},
        },
    }
    dimensions = (3, 3)
    map = map_generation(dimensions, tileset, rules)
    print(map)


def map_generation(dimensions: tuple[int, int], tileset: set[str], rules: dict[str, dict[Direction, set[str]]]):
    map = Map(dimensions, tileset)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            tile_options = map.get_tile(i, j)
            if isinstance(tile_options, set):
                choice = random.choice(list(tile_options))
                map.set_tile(i, j, random.choice(list(tileset)))
                for dir in Direction:
                    target = (i, j) + dir.get_tuple()
                    if not (target[0] < 0
                            or target[0] >= dimensions[0]
                            or target[1] < 0
                            or target[1] >= dimensions[1]):
                        target_options = map.get_tile(i, j)
                        if isinstance(target_options, set):
                            new_options = rules[choice][dir].intersection(target_options)
                            if len(new_options) == 0:
                                raise ValueError
                            if len(new_options) == 1:
                                new_options = new_options.pop()
                            map.set_tile(i, j, new_options)
    return map


class Map:
    def __init__(self, dimensions: tuple[int, int], tileset: set[str]):
        self.dimensions = dimensions
        num_tiles = dimensions[0] * dimensions[1]
        self.tiles: list[set[str] | str] = [tileset for _ in range(num_tiles)]

    def get_tile(self, x: int, y: int):
        return self.tiles[y * self.dimensions[0] + x]

    def get_tile_string(self, x: int, y: int):
        tile = self.tiles[y * self.dimensions[0] + x]
        if isinstance(tile, set):
            tile = "e"
        return tile

    def set_tile(self, x: int, y: int, value: str | set[str]):
        self.tiles[y * self.dimensions[0] + x] = value

    # sets tiles in grid
    def __str__(self):
        return_string = ""
        for i in range(self.dimensions[1]):
            for j in range(self.dimensions[0]):
                return_string += self.get_tile_string(j, i)
            # Avoid trailing newline
            if i != self.dimensions[1] - 1:
                return_string += "\n"
        return return_string




if __name__ == "__main__":
    main()