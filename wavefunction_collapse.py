from os import truncate
import random
from position import Position, Direction
from map import Map
from tileset import Tileset
import queue
import itertools
import threading
import multiprocessing


def map_generation_chunked(tileset: Tileset, dimensions: tuple[int, int], chunk_dimensions: tuple[int, int], regen_entropy: bool = False, num_threads: int = 1, looping = False):
    chunk = Map(chunk_dimensions, tileset, looping=True)
    if chunk_dimensions[0] >= dimensions[0] and chunk_dimensions[1] >= dimensions[1]:
        chunk.looping = looping
        chunk.tile_to_dimensions(dimensions)
        return map_generation(chunk, regen_entropy=regen_entropy)
    map_generation(chunk)
    chunk.looping = looping
    chunk.tile_to_dimensions(dimensions)
    return_map = chunk
    
    regen_offset = (chunk_dimensions[0] // 2, chunk_dimensions[1] // 2)
    jobs = multiprocessing.Queue()
    x_pos_list = [(x, chunk_dimensions[0]) for x in range(regen_offset[0], dimensions[0] + regen_offset[0], chunk_dimensions[0])]
    y_pos_list = [(y, chunk_dimensions[1]) for y in range(regen_offset[1], dimensions[1] + regen_offset[1], chunk_dimensions[1])]
    x_pos_list = map(lambda x: job_trimmer(x, dimensions[0], regen_offset[0], looping), x_pos_list)
    y_pos_list = map(lambda y: job_trimmer(y, dimensions[1], regen_offset[1], looping), y_pos_list)
    if not looping:
        x_pos_list = itertools.chain([(0, regen_offset[0])], x_pos_list)
        y_pos_list = itertools.chain([(0, regen_offset[1])], y_pos_list)

    jobs_list = itertools.product(x_pos_list, y_pos_list)
    jobs_list = list(map(job_zipper, jobs_list))

    # This is required to ensure threads are less likely to work
    # on neighboring chunks, which could lead to conflicts.
    # I wish there was an easier way to checkerboard it like this.
    jobs_list_even = []
    jobs_list_odd = []
    old_y = -1
    last_even = False
    last_row_even = False
    
    for job in jobs_list:
        if job[0].y != old_y:
            old_y = job[0].y
            last_even = last_row_even
            last_row_even = not last_row_even
        if last_even:
            jobs_list_odd.append(job)
        else:
            jobs_list_even.append(job)
    for job in jobs_list_even:
        jobs.put(job)
    for job in jobs_list_odd:
        jobs.put(job)
    jobs.close()

    processes = []
    for i in range(num_threads):
        processes.append(multiprocessing.Process(target=lambda: chunk_worker(return_map, jobs), name=f"Thread-{i}"))
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    jobs.join_thread()
    return return_map

def job_trimmer(job, dimension, offset, looping):
    pos = job[0]
    length = job[1]
    return (pos, min(length, dimension + (offset if looping else 0) - pos))

def job_zipper(job):
    return (Position(job[0][0], job[1][0]), (job[0][1], job[1][1]))

def chunk_worker(map, jobs):
    label = multiprocessing.current_process().name
    print(f"Starting thread {label}")
    while True:
        try:
            job = jobs.get(timeout=0.2)
        except (queue.Empty, OSError):
            break
        # print(f"Thread {label} working job {job}")
        remove_section_and_repropagate(map, job[0], job[1])
        map_generation(map, job, True)
        # print(f"Thread {label} finished job {job}")
    print(f"No more jobs in queue. Killing thread {label}")


def remove_section_and_repropagate(map: Map, pos: Position, dimensions: tuple[int, int]):
    end_pos = pos + (dimensions[0] - 1, dimensions[1] - 1)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            target = pos + (i, j)
            map.set_tile(target, map.tileset.tiles)
    if pos.y > 0 or map.looping:
        for i in range(dimensions[0]):
            target = pos + (i, -1)
            propagate_collapse(map, target, limit_directions={Direction.S})
    if end_pos.y < map.dimensions[1] - 1 or map.looping:
        for i in range(dimensions[0]):
            target = end_pos + (-i, 1)
            propagate_collapse(map, target, limit_directions={Direction.N})
    if pos.x > 0 or map.looping:
        for i in range(dimensions[1]):
            target = pos + (-1, i)
            propagate_collapse(map, target, limit_directions={Direction.E})
    if end_pos.x < map.dimensions[0] - 1 or map.looping:
        for i in range(dimensions[1]):
            target = end_pos + (1, -i)
            propagate_collapse(map, target, limit_directions={Direction.W})


def map_generation(map: Map, limits: tuple[Position, tuple[int, int]] | None = None, regen_entropy: bool = False):
    if limits is not None:
        offset = limits[0]
        dimensions = limits[1]
    else:
        offset = Position(0, 0)
        dimensions = map.dimensions
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            target = Position(i, j) + offset
            tile_options = map.get_tile(target)
            if isinstance(tile_options, set):
                choice = random.choice(list(tile_options))
                map.set_tile(target, choice)
                propagate_collapse(map, target, None)
    return map


def propagate_collapse(map: Map, position: Position, direction: Direction | None = None, limit_directions: set[Direction] | None = None):
    prop_source = map.get_tile(position)
    iter_directions = map.get_valid_directions(position)
    iter_directions -= {direction}
    if limit_directions is not None:
        iter_directions = iter_directions.intersection(limit_directions)
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
