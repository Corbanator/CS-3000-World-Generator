import time
from map import Map
import performance_testing
from position import Position
from tileset import Tileset
from wavefunction_collapse import map_generation, map_generation_chunked

def test():
    for _ in range(30):
        tileset = Tileset.parse_json("default_tileset.json")
        start_time = time.time()
        map = map_generation_chunked(tileset, (2048, 2048), (32,32), num_threads=16)
        # map = Map((2048, 2048), tileset)
        # map_generation(map)
        mid_time = time.time()
        performance_testing.check_map(map)
        end_time = time.time()
        performance_testing.check_map(map)
        # map.print_debug()
        print(f"Finished in {end_time - start_time}s. {mid_time - start_time}s for generation, {end_time - mid_time}s for checking.")
    

test()
