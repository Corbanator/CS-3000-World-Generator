from position import Direction
import json

class Tileset:
    def __init__(self, 
                 tiles: set[str] | None = None, 
                 rules: dict[str, dict[Direction, set[str]]] | None = None, 
                 colors: dict[str, str] | None = None,
                 walkability: dict[str, bool] | None = None):
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
        if walkability is not None:
            for tile in walkability:
                if tile not in self.tiles:
                    raise ValueError
            self.walkability = walkability
        else:
            self.walkability: dict[str, bool] = {}

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

    def set_walkable(self, tiles: set[str], is_walkable: bool):
        for tile in tiles:
            self.walkability[tile] = is_walkable

    def is_walkable(self, tile: str):
        return self.walkability.get(tile, True)

    def get_color(self, tile: str):
        return self.colors.get(tile, None)


    @staticmethod
    def parse_json(filename: str):
        with open(filename) as file:
            our_dict = json.load(file)
        tiles = set(our_dict.keys())
        new_tileset = Tileset(tiles)
        for tile in tiles:
            tile_rules = our_dict[tile]["rules"]
            for direction_key in tile_rules:
                directions = Direction.get_set_from_str(direction_key)
                new_tileset.add_rule({tile}, directions, set(our_dict[tile]["rules"][direction_key]))
            new_tileset.add_colors({tile: our_dict[tile]["color"]})
            new_tileset.set_walkable({tile}, (our_dict[tile]["isWalkable"] == "True"))
        return new_tileset


    def __eq__(self, o):
        if self.tiles != o.tiles:
            return False
        if self.colors != o.colors:
            return False
        for tile in self.rules:
            for direction in self.rules[tile]:
                if o.rules.get(tile).get(direction) != self.rules[tile][direction]:
                    return False
        return True


