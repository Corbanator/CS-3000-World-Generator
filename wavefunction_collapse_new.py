import random
from enum import IntEnum
from player import Player  # Import the Player class
from pynput import keyboard  # Import keyboard listener
from mapVisual import MapVisualizer  # Import MapVisualizer from mapVisual

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


class Map:
    def __init__(self, dimensions: tuple[int, int], tileset: set[str]):
        self.dimensions = dimensions
        num_tiles = dimensions[0] * self.dimensions[1]
        self.tiles: list[set[str] | str] = [tileset for _ in range(num_tiles)]
        self.original_tiles: list[str] = ["e" for _ in range(num_tiles)]  # Store original tiles

    def get_tile(self, x: int, y: int):
        return self.tiles[y * self.dimensions[0] + x]

    def get_tile_string(self, x: int, y: int):
        tile = self.tiles[y * self.dimensions[0] + x]
        if isinstance(tile, set):
            tile = "e"
        return tile

    def set_tile(self, x: int, y: int, value: str | set[str]):
        self.tiles[y * self.dimensions[0] + x] = value
        if value != "P":  # Update original tiles only if not setting the player
            self.original_tiles[y * self.dimensions[0] + x] = value

    def __str__(self):
        return_string = ""
        for i in range(self.dimensions[1]):
            for j in range(self.dimensions[0]):
                return_string += self.get_tile_string(j, i)
            if i != self.dimensions[1] - 1:
                return_string += "\n"
        return return_string

    def print_debug(self):
        return_string = ""
        for i in range(self.dimensions[1]):
            for j in range(self.dimensions[0]):
                return_string += str(self.get_tile(j, i))
            if i != self.dimensions[1] - 1:
                return_string += "\n"
        print(return_string)


def main():
    dimensions = [15, 15]  # Change dimensions to a mutable list
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
    map = map_generation(tuple(dimensions), tileset, rules)
    player = Player(dimensions)  # Initialize player with randomized position
    while map.get_tile(player.x, player.y) == "O":
        player = Player(dimensions)  # Reinitialize player until not on 'O'
    player.update_map(map)  # Place player on the map

    print(
            "\nWelcome to the WFC World Generator Game!\n"
            "Navigate the player (Orange) using the arrow keys.\n"
            "Press buttons (Purple) to unlock the goal(Red -> Dark Green).\n"
            "Avoid obstacles like the ocean (Blue).\n"
            "Explore the land (Green) and beach (Tan).\n"
            "Good luck!\n"
        )

    visualizer = MapVisualizer(map, player)  # Initialize the visualizer

    def on_keypress(event):
        player.handle_keypress(event, map, visualizer)  # Delegate keypress handling to Player

    visualizer.root.bind("<Up>", lambda event: on_keypress(event))
    visualizer.root.bind("<Left>", lambda event: on_keypress(event))
    visualizer.root.bind("<Down>", lambda event: on_keypress(event))
    visualizer.root.bind("<Right>", lambda event: on_keypress(event))
    visualizer.root.bind("q", lambda event: on_keypress(event))  # Bind 'q' key to quit

    visualizer.run()  # Run the tkinter visualization


def map_generation(dimensions: tuple[int, int], tileset: set[str], rules: dict[str, dict[Direction, set[str]]]):
    map = Map(dimensions, tileset)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            tile_options = map.get_tile(i, j)
            if isinstance(tile_options, set):
                choice = random.choice(list(tile_options))
                map.set_tile(i, j, choice)
                propagate_collapse(map, tileset, rules, (i, j), None)
    return map

def propagate_collapse(map: Map, tileset: set[str], rules: dict[str, dict[Direction, set[str]]], position: tuple[int, int], direction: Direction | None = None):
    prop_source = map.get_tile(position[0], position[1])
    for dir in [Direction.N, Direction.E, Direction.S, Direction.W]:
        if dir != direction:
            target = (position[0] + dir.get_tuple()[0], position[1] + dir.get_tuple()[1])
            if not (target[0] < 0
                    or target[0] >= map.dimensions[0]
                    or target[1] < 0
                    or target[1] >= map.dimensions[1]):
                target_options = map.get_tile(target[0], target[1])
                if isinstance(target_options, set):
                    if isinstance(prop_source, set):
                        allowable_tiles = set()
                        for i in prop_source:
                            allowable_tiles = allowable_tiles.union(rules[i][dir])
                        new_options = target_options.intersection(allowable_tiles)
                    else:
                        new_options = rules[prop_source][dir].intersection(target_options)
                    if len(new_options) == 0:
                        raise ValueError
                    map.set_tile(target[0], target[1], new_options)
                    if new_options != target_options:
                        propagate_collapse(map, tileset, rules, target, dir.opposite())

if __name__ == "__main__":
    main()
