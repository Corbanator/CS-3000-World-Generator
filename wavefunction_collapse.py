import random
from player import Player  # Import the Player class
from pynput import keyboard  # Import keyboard listener
import colorama
from position import Position, Direction
from tileset import Tileset
from map import Map


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
    map = Map(dimensions, tileset)
    map_generation(map)
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

if __name__ == "__main__":
    main()
