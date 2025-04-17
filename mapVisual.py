import tkinter as tk
from position import Direction, Position
from map import Map
from player import Player
from goal import GoalManager
from tileset import Tileset

class MapVisualizer:
    def __init__(self, map, player):
        self.map = map
        self.player = player
        self.goal_manager = GoalManager(map, player)  # Pass the player object to GoalManager
        self.cell_size = 30  # Size of each cell in pixels
        self.colors = {
            "B": "#D2B48C",  # Tan (beach color)
            "L": "#556B2F",  # Dark Olive Green (land color)
            "O": "#4682B4",  # Steel Blue (ocean color)
            "P": "#FF4500",  # Orange Red (Player color)
            "U": "#4B0082",  # Indigo (Button color)
            "C": "#2E8B57",  # Sea Green (Pressed button color)
            "R": "#8B0000",  # Dark Red (Locked goal color)
            "G": "#228B22"   # Forest Green (Unlocked goal color)
        }
        self.root = tk.Tk()
        self.root.focus_force()  # Ensure the new window is the active window
        self.canvas = tk.Canvas(self.root, width=self.map.dimensions[0] * self.cell_size, height=self.map.dimensions[1] * self.cell_size)
        self.canvas.pack()

    def draw_map(self):
        self.canvas.delete("all")  # Clear the canvas
        for y in range(self.map.dimensions[1]):
            for x in range(self.map.dimensions[0]):
                tile = self.map.get_visual_tile(Position(x, y))
                if isinstance(tile, set):
                    tile = next(iter(tile)) if len(tile) == 1 else "e"  # Extract single element or default to 'e'
                color = self.colors.get(tile, "white")  # Default to white if no color is defined
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline="black"
                )

    def update(self):
        self.draw_map()
        self.root.update_idletasks()  # Ensure the canvas updates properly
        self.root.update()

    def run(self):
        self.draw_map()
        self.root.mainloop()

def restart_game(map_visualizer):
    from wavefunction_collapse import map_generation
    from player import Player
    from goal import GoalManager  # Ensure GoalManager is reinitialized
    import random

    # Close the current window
    map_visualizer.root.destroy()

    # Increase dimensions
    map_visualizer.map.dimensions = (
        min(map_visualizer.map.dimensions[0] + random.randint(1, 5), 32),
        min(map_visualizer.map.dimensions[1] + random.randint(1, 5), 32)
    )

    # Regenerate the map
    tile_options = {"L", "B", "O"}
    rules = {
        "L": {
            Direction.N: {"L", "B"},
            Direction.E: {"L", "B"},
            Direction.S: {"L", "B"},
            Direction.W: {"L", "B"},
        },
        "B": {
            Direction.N: {"L", "B", "O"},
            Direction.E: {"L", "B", "O"},
            Direction.S: {"L", "B", "O"},
            Direction.W: {"L", "B", "O"},
        },
        "O": {
            Direction.N: {"B", "O"},
            Direction.E: {"B", "O"},
            Direction.S: {"B", "O"},
            Direction.W: {"B", "O"},
        },
    }
    tileset = Tileset(tile_options, rules)
    map_visualizer.map = Map(map_visualizer.map.dimensions, tileset)
    map_generation(map_visualizer.map)

    # Reinitialize the player
    map_visualizer.player = Player(map_visualizer.map.dimensions)
    while map_visualizer.map.get_visual_tile(map_visualizer.player.pos) == "O":
        map_visualizer.player = Player(map_visualizer.map.dimensions)
    map_visualizer.player.update_map(map_visualizer.map)

    # Reinitialize the MapVisualizer
    new_visualizer = MapVisualizer(map_visualizer.map, map_visualizer.player)

    # Rebind key listeners
    def on_keypress(event):
        map_visualizer.player.handle_keypress(event, map_visualizer.map, new_visualizer)

    new_visualizer.root.bind("<Up>", lambda event: on_keypress(event))
    new_visualizer.root.bind("<Left>", lambda event: on_keypress(event))
    new_visualizer.root.bind("<Down>", lambda event: on_keypress(event))
    new_visualizer.root.bind("<Right>", lambda event: on_keypress(event))
    new_visualizer.root.bind("q", lambda event: new_visualizer.root.destroy())  # Bind 'q' key to quit

    # Run the new visualizer
    new_visualizer.run()
