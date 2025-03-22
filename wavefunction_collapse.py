"""
This module is the core of our wavefunction collapse map generation, as it
contains the main algorithmic implementation.

Usage:
- create a tileset, and put in tiles and rules (this is the hard part)
- pass into wf_collapse with dimensions, and perhaps a starting map configuration
- render result
"""

from enum import IntEnum
from typing import Callable
import random


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


class Tileset:
    def __init__(self):
        self.tiles: list[str] = []
        self.simple_rules: list[tuple[str, Direction, str]] = []
        self.complex_rules: list[tuple[tuple[int, int], Callable[[list[tuple[tuple[int, int], str]]], bool]]] = []

    def add_tile(self, tile: str):
        if tile not in self.tiles:
            self.tiles.append(tile)

    def add_simple_rule(self, tile1: str, direction: Direction, tile2: str):
        rule = (tile1, direction, tile2)
        if rule in self.simple_rules:
            return
        inverse = (tile2, direction.opposite(), tile1)
        self.simple_rules.append(rule)
        self.simple_rules.append(inverse)


def _pop_rand(unordered: list):
    choice = random.choice(unordered)
    # since we don't actually care about the order.
    unordered[-1], unordered[choice] = unordered[choice], unordered[-1]
    return unordered.pop()


def wf_collapse(tileset: Tileset,
                dimensions: tuple[int, int],
                init_map: list[list[str] | str | None] | None = None):
    """This is the core function of the module. Note the type hinting."""

    # Initialize the uncollapsed map
    return_map: list[list[str] | str]
    if init_map is not None:
        if len(init_map) != dimensions[0] * dimensions[1]:
            raise ValueError(
                    f"""init_map length does not match dimensions given.
                     Expected length of {dimensions[0] * dimensions[1]}""")
        # Replace None types with uncollapsed map spaces.
        # This is simply for ease of use, so the user can simply pass None
        # where they have no specified initial conditions.
        return_map = list(map(lambda x:
                              x if x is not None
                              else [*tileset.tiles],
                          init_map))
    else:
        return_map = [[*tileset.tiles]
                      for _ in range(dimensions[0] * dimensions[1])]
    print(return_map)

    uncollapsed_spaces = [i for i, e in enumerate(return_map) if isinstance(e, list)]
    while len(uncollapsed_spaces) != 0:
        target_index = _pop_rand(uncollapsed_spaces)
        return_map[target_index] = random.choice(return_map[target_index])

    return return_map


def main():
    tileset = Tileset()
    tileset.add_tile("-")
    tileset.add_tile("/")
    tileset.add_simple_rule("-", Direction.W, "/")
    wf_collapse(tileset, (4, 4))
    wf_collapse(tileset, (5, 5), [
        ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"],
        ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"],
        ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"],
        ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"], ["-", "/"],
        ["-", "/"], ["-", "/"], ["-", "/"], None, ["-", "/"],
        ])


if __name__ == "__main__":
    main()
