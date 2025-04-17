import random
from position import Position, Direction
from map import Map


def map_generation(map: Map):
    dimensions = map.dimensions
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
