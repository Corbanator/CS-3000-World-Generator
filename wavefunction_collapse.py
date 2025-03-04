"""
This module is the core of our wavefunction collapse map generation, as it
contains the main algorithmic implementation.

Usage:
- create a tileset, and put in tiles and rules (this is the hard part)
- pass into wf_collapse with dimensions, and perhaps a starting map configuration
- render result
"""

from typing import Callable


class Tileset:
    def __init__(self):
        self.tiles: dict[str, tuple[str, dict[str, float], list[Callable[[list[str]], bool]]]] = {}

    def add_tile(self,
                 tile: str,
                 display_tile: str,
                 neighbor_rules: dict[str, float] = {},
                 function_rules: list[Callable[[list[str]], bool]] = []):

        self.tiles[tile] = (display_tile, neighbor_rules, function_rules)


def wf_collapse(tileset: Tileset,
                dimensions: tuple[int, int],
                init_map: list[set[str] | str | None] | None = None):
    """This is the core function of the module. Note the type hinting."""

    # Initialize the uncollapsed map
    return_map: list[set[str] | str]
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
                              else {*tileset.tiles},
                          init_map))
    else:
        return_map = [{*tileset.tiles}
                      for _ in range(dimensions[0] * dimensions[1])]
    print(return_map)

    return return_map


def main():
    tileset = Tileset()
    tileset.add_tile("-", "---", {"/l": 0.5})
    tileset.add_tile("/", "///", {"-r": 0.5})
    wf_collapse(tileset, (4, 4))
    wf_collapse(tileset, (5, 5), [
        {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"},
        {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"},
        {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"},
        {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"}, {"-", "/"},
        {"-", "/"}, {"-", "/"}, {"-", "/"}, None, {"-", "/"},
        ])


if __name__ == "__main__":
    main()
