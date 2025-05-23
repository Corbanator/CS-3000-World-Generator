import itertools
import random
import time
from map import Map
from position import Direction, Position
from tileset import Tileset
from wavefunction_collapse import map_generation, map_generation_chunked
import csv


def test_threaded(tileset, dimensions, chunk_dimensions, num_threads):
    now = time.time()
    # new_map = map_generation(map, multithread=True, seed=seed)
    new_map = map_generation_chunked(tileset, dimensions, chunk_dimensions, num_threads=num_threads)
    later = time.time()
    # check_map(new_map)
    return later - now


def test_unthreaded(map, seed):
    now = time.time()
    new_map = map_generation(map)
    later = time.time()
    return later - now


def setup_map(dimensions):
    tileset = Tileset.parse_json("default_tileset.json")
    return Map.new(dimensions, tileset)


def check_map(map: Map):
    print("Checking map for inconsistencies...")
    for i in range(map.dimensions[0]):
        for j in range(map.dimensions[1]):
            pos = Position(i, j)
            tile = map.get_tile(pos)
            for dir in map.get_valid_directions(pos):
                target = pos + dir.get_tuple()
                target_tile = map.get_tile(target)
                if target_tile not in map.tileset.get_options({tile}, dir):
                    print(f"Failure at {target}: expected member of {map.tileset.get_options({tile}, dir)}, found {map.get_tile(pos + dir.get_tuple())}")
                    print("neighborhood of target:")
                    neighborhood = map.get_patch(target + (-1, -1), (3, 3))
                    neighborhood.print_debug()
                    alternatives = map.tileset.tiles
                    for dir in map.get_valid_directions(target):
                        secondary = target + dir.get_tuple()
                        alternatives = alternatives.intersection(map.tileset.get_options({map.get_tile(secondary)}, dir.opposite()))
                    selection = None
                    if len(alternatives) > 0:
                        selection = random.choice(list(alternatives))
                        map.set_tile(target, selection)
                    print(f"Found functional alternatives: {alternatives}. Selecting {selection}.")
    print("Map checked.")


def test_performance():
    tileset = Tileset.parse_json("default_tileset.json")
    with open("test_output.csv", "w") as output_file:
        output_csv = csv.writer(output_file)
        output_csv.writerow(("n", "chunk_size", "threads", "time"))
        for n in map(lambda x: pow(2, x), range(6, 1000)):
            # for chunk_size in map(lambda x: pow(2, x), range(2, 6)):
            for chunk_size in [32]:
                for num_threads in range(1, 17):
                    result_time = test_threaded(tileset, (n, n), (chunk_size, chunk_size), num_threads)
                    output_csv.writerow((n, chunk_size, num_threads, result_time))
                    print((n, chunk_size, num_threads, result_time))

def test_single():
    tileset = Tileset.parse_json("default_tileset.json")
    print(test_threaded(tileset, (64, 64), (8, 8), 16))


def main():
    test_performance()
    # test_single()


if __name__ == "__main__":
    main()
