import random
from player import Player  # Import the Player class
from pynput import keyboard  # Import keyboard listener
import colorama
from position import Position, Direction

class Tileset:
    def __init__(self, 
                 tiles: set[str] | None = None, 
                 rules: dict[str, dict[Direction, set[str]]] | None = None, 
                 colors: dict[str, str] | None = None):
        if tiles is not None:
            self.tiles = tiles
        else:
            self.tiles = set()
        if rules is not None:
            for rule in rules:
                if rule not in self.tiles:
                    raise ValueError
                for dir in Direction.all_cardinal():
                    if rules[rule][dir].intersection(self.tiles) != rules[rule][dir]:
                        raise ValueError
            self.rules = rules
        else:
            self.rules: dict[str, dict[Direction, set[str]]] = {}
        if colors is not None:
            for color in colors:
                if color not in self.tiles:
                    raise ValueError
            self.colors = colors
        else:
            self.colors: dict[str, str] = {}

    def add_rule(self, init_tiles: set[str], directions: set[Direction], terminal_tiles: set[str]):
        if (init_tiles.intersection(self.tiles) != init_tiles 
                or terminal_tiles.intersection(self.tiles) != terminal_tiles):
            raise ValueError
        for dir in directions:
            for tile in init_tiles:
                if tile not in self.rules:
                    self.rules[tile] = {}
                if dir not in self.rules[tile]:
                    self.rules[tile][dir] = set()
                self.rules[tile][dir] = terminal_tiles.union(self.rules.get(tile, {}).get(dir, set()))
            for tile in terminal_tiles:
                if tile not in self.rules:
                    self.rules[tile] = {}
                if dir not in self.rules[tile]:
                    self.rules[tile][dir] = set()
                self.rules[tile][dir.opposite()] = init_tiles.union(self.rules.get(tile, {}).get(dir, set()))


    def add_tiles(self, tiles: set[str]):
        self.tiles = self.tiles.union(tiles)

    def get_options(self, init_tileset: set[str] | str, direction: Direction):
        options = set()
        if isinstance(init_tileset, set):
            for tile in init_tileset:
                options = options.union(self.rules[tile][direction])
        else:
            options = self.rules[init_tileset][direction]
        return options

    def add_colors(self, colors: dict[str, str]):
        for i in colors:
            if i not in self.tiles:
                raise ValueError
            self.colors[i] = colors[i]


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


def main():
    tiles = {"L", "B", "O"}
    tileset = Tileset(tiles,
                      colors={
                              "O": colorama.Fore.BLUE,
                              "B": colorama.Fore.YELLOW,
                              "L": colorama.Fore.GREEN,
                              })
    tileset.add_rule({"L"}, Direction.all_cardinal(), {"L", "B"})
    tileset.add_rule({"B", "O"}, Direction.all_cardinal(), {"B", "O"})
    dimensions = (1000,1000)
    map = map_generation(dimensions, tileset)
    player = Player(dimensions)  # Initialize player with randomized position
    while map.get_tile(Position(player.x, player.y)) == "O":
        player = Player(dimensions)  # Reinitialize player until not on 'O'
    player.update_map(map)  # Place player on the map

    def on_press(key):
        try:
            if key == keyboard.Key.up:
                player.move("W", map)
            elif key == keyboard.Key.left:
                player.move("A", map)
            elif key == keyboard.Key.down:
                player.move("S", map)
            elif key == keyboard.Key.right:
                player.move("D", map)
            elif key.char.upper() == "Q":  # Quit the game
                print("Exiting game.")
                return False

            player.update_map(map)  # Update map with new player position
            print(map)
            # print(f"Player position: {player.get_position()}")
        except AttributeError:
            pass

    print(map)
    # print(f"Player position: {player.get_position()}")
    print("Use arrow keys to move or Q to quit.")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def map_generation(dimensions: tuple[int, int], tileset: Tileset):
    map = Map(dimensions, tileset)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            tile_options = map.get_tile(Position(i, j))
            if isinstance(tile_options, set):
                choice = random.choice(list(tile_options))
                map.set_tile(Position(i, j), choice)
                propagate_collapse(map, Position(i, j), None)
    return map

def propagate_collapse(map: Map, position: Position, direction: Direction | None = None):
    prop_source = map.get_tile(position)
    iter_directions = map.get_valid_directions(position)
    iter_directions -= {direction}
    for dir in iter_directions:
        target = position.traverse(dir)
        target_options = map.get_tile(target)
        if isinstance(target_options, set):
            new_options = target_options.intersection(map.tileset.get_options(prop_source, dir))
            if len(new_options) == 0:
                raise ValueError
            map.set_tile(target, new_options)
            if new_options != target_options:
                propagate_collapse(map, target, dir.opposite())

if __name__ == "__main__":
    main()
