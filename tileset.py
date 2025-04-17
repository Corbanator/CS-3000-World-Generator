from position import Direction
import json

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


    @staticmethod
    def parse_json(filename: str):
        with open(filename) as file:
            our_dict = json.load(file)
        tiles = our_dict.keys
        rules = {}
        for tile in tiles:
            rules[tile] = our_dict[tile]["rules"]
        print(tiles)
        print(rules)


