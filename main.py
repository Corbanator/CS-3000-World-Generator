from position import Direction
from map import Map
from player import Player  # Import the Player class
from pynput import keyboard  # Import keyboard listener
import colorama
from tileset import Tileset
from mapVisual import MapVisualizer
from wavefunction_collapse import map_generation


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
    dimensions = (10,10)
    map = Map(dimensions, tileset)
    map_generation(map)
    player = Player(dimensions)  # Initialize player with randomized position
    while map.get_tile(player.pos) == "O":
        player = Player(dimensions)  # Reinitialize player until not on 'O'
    player.update_map(map)  # Place player on the map

    print(
            "\nWelcome to the WFC World Generator Game!\n"
            "Navigate the player (Orange) using the arrow keys.\n"
            "Press buttons (Purple) to unlock the goal(Red -> Dark Green).\n"
            "Avoid obstacles like the ocean (Blue).\n"
            "Explore the land (Green) and beach (Tan).\n"
            "Good luck!\n"
        )

    visualizer = MapVisualizer(map, player)  # Initialize the visualizer

    def on_keypress(event):
        player.handle_keypress(event, map, visualizer)  # Delegate keypress handling to Player

    visualizer.root.bind("<Up>", lambda event: on_keypress(event))
    visualizer.root.bind("<Left>", lambda event: on_keypress(event))
    visualizer.root.bind("<Down>", lambda event: on_keypress(event))
    visualizer.root.bind("<Right>", lambda event: on_keypress(event))
    visualizer.root.bind("q", lambda event: on_keypress(event))  # Bind 'q' key to quit

    visualizer.run()  # Run the tkinter visualization


if __name__ == "__main__":
    main()
