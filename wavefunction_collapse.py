from os import truncate
import random
from position import Position, Direction
from map import Map
from tileset import Tileset
import queue
import itertools
import threading
import multiprocessing
import multiprocessing.sharedctypes
import multiprocessing.shared_memory
import multiprocessing.managers


class MyManager(multiprocessing.managers.BaseManager):
    pass


MyManager.register("Map", Map)


def map_generation_chunked(tileset: Tileset, dimensions: tuple[int, int], chunk_dimensions: tuple[int, int], regen_entropy: bool = False, num_threads: int = 1, looping = False):
    manager = MyManager()
    manager.start()
    map_manager = manager.Map()
    chunk = Map()
    chunk.set_dimensions(chunk_dimensions)
    chunk.set_tileset(tileset)
    # map_manager = Map.new(chunk_dimensions, tileset, looping=True)
    if chunk_dimensions[0] >= dimensions[0] and chunk_dimensions[1] >= dimensions[1]:
        chunk.looping = looping
        chunk.tile_to_dimensions(dimensions)
        return map_generation(chunk, regen_entropy=regen_entropy)
    map_generation(chunk)
    chunk.looping = looping
    chunk.tile_to_dimensions(dimensions)
    
    regen_offset = (chunk_dimensions[0] // 2, chunk_dimensions[1] // 2)
    x_pos_list = [(x, chunk_dimensions[0]) for x in range(regen_offset[0], dimensions[0], chunk_dimensions[0])]
    y_pos_list = [(y, chunk_dimensions[1]) for y in range(regen_offset[1], dimensions[1], chunk_dimensions[1])]
    x_pos_list = map(lambda x: job_trimmer(x, dimensions[0], regen_offset[0], looping), x_pos_list)
    y_pos_list = map(lambda y: job_trimmer(y, dimensions[1], regen_offset[1], looping), y_pos_list)
    if not looping:
        x_pos_list = itertools.chain([(0, regen_offset[0])], x_pos_list)
        y_pos_list = itertools.chain([(0, regen_offset[1])], y_pos_list)

    jobs_list = itertools.product(x_pos_list, y_pos_list)
    jobs_list = list(map(job_zipper, jobs_list))
    # Avoid using too many threads
    # job_thread_factor = 1024 // (chunk_dimensions[0] * chunk_dimensions[1])
    # if len(jobs_list) < num_threads * job_thread_factor:
    #     num_threads = max(len(jobs_list) // job_thread_factor, 1)

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
    jobs = multiprocessing.Queue()
    for job in jobs_list_even:
        jobs.put(job)
    for job in jobs_list_odd:
        jobs.put(job)
    # print("printing jobs queue")
    # while not jobs.empty():
    #     print(jobs.get())
    # print("printed jobs queue")
    
    map_manager.self_from_map(chunk)
    processes = []
    for i in range(num_threads):
        processes.append(multiprocessing.Process(target=lambda: chunk_worker(map_manager, jobs), name=f"Thread-{i}"))
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    jobs.close()
    jobs.join_thread()
    return_map = map_manager.get_self_as_map()
    manager.shutdown()
    return return_map

def job_trimmer(job, dimension, offset, looping):
    pos = job[0]
    length = job[1]
    return (pos, min(length, dimension + (offset if looping else 0) - pos))

def job_zipper(job):
    return (Position(job[0][0], job[1][0]), (job[0][1], job[1][1]))

def chunk_worker(map, jobs):
    # label = multiprocessing.current_process().name
    map_dimensions = map.get_dimensions()
    while True:
        try:
            job = jobs.get(timeout=0.2)
        except (queue.Empty, OSError, EOFError):
            break
        # print(f"Thread {label} working job {job}")
        x_adjust = 0 if job[0].x == 0 else 1
        y_adjust = 0 if job[0].y == 0 else 1
        end_x_adjust = 1 if job[0].x + job[1][0] < map_dimensions[0] - 1 else 0
        end_y_adjust = 1 if job[0].y + job[1][1] < map_dimensions[1] - 1 else 0
        patch = map.get_patch(Position(job[0].x - x_adjust, job[0].y - y_adjust), (job[1][0] + x_adjust + end_x_adjust, job[1][1] + y_adjust + end_y_adjust))
        remove_section_and_repropagate(patch, Position(x_adjust, y_adjust), job[1])
        map_generation(patch, regen_entropy=True)
        patch_to_apply = patch.get_patch(Position(x_adjust, y_adjust), (patch.dimensions[0] - x_adjust - end_x_adjust, patch.dimensions[1] - y_adjust - end_y_adjust))
        map.apply_patch(Position(job[0].x, job[0].y), patch_to_apply)
        # print(f"Thread {label} finished job {job}")
    # print(f"No more jobs in queue. Killing thread {label}")


def remove_section_and_repropagate(map: Map, pos: Position, dimensions: tuple[int, int]):
    end_pos = pos + (dimensions[0] - 1, dimensions[1] - 1)
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            target = pos + (i, j)
            map.set_tile(target, map.get_tileset().tiles)
    if pos.y > 0 or map.looping:
        for i in range(dimensions[0]):
            target = pos + (i, -1)
            propagate_collapse(map, target, limit_directions={Direction.S})
    if end_pos.y < map.get_dimensions()[1] - 1 or map.looping:
        for i in range(dimensions[0]):
            target = end_pos + (-i, 1)
            propagate_collapse(map, target, limit_directions={Direction.N})
    if pos.x > 0 or map.looping:
        for i in range(dimensions[1]):
            target = pos + (-1, i)
            propagate_collapse(map, target, limit_directions={Direction.E})
    if end_pos.x < map.get_dimensions()[0] - 1 or map.looping:
        for i in range(dimensions[1]):
            target = end_pos + (1, -i)
            propagate_collapse(map, target, limit_directions={Direction.W})


def map_generation(map: Map, limits: tuple[Position, tuple[int, int]] | None = None, regen_entropy: bool = False):
    if limits is not None:
        offset = limits[0]
        dimensions = limits[1]
    else:
        offset = Position(0, 0)
        dimensions = map.get_dimensions()
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
    try:
        prop_source = map.get_tile(position)
    except:
        print(position)
        print(map.get_dimensions())
    iter_directions = map.get_valid_directions(position)
    iter_directions -= {direction}
    if limit_directions is not None:
        iter_directions = iter_directions.intersection(limit_directions)
    for dir in iter_directions:
        target = position.traverse(dir)
        target_options = map.get_tile(target)
        if isinstance(target_options, set):
            new_options = target_options.intersection(map.get_tileset().get_options(prop_source, dir))
            if len(new_options) == 0:
                print(f"Problem at position {target}. Tried to intersect with {map.get_tileset().get_options(prop_source, dir)}")
                map.print_debug()
                raise ValueError
            map.set_tile(target, new_options)
            if new_options != target_options:
                propagate_collapse(map, target, dir.opposite())
