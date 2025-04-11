import tkinter as tk
from player import Player

class MapVisualizer:
    def __init__(self, map, player):
        self.map = map
        self.player = player
        self.cell_size = 30  # Size of each cell in pixels
        self.colors = {
            "B": "tan",
            "L": "green",
            "O": "blue",
            "P": "orange"
        }
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=self.map.dimensions[0] * self.cell_size, height=self.map.dimensions[1] * self.cell_size)
        self.canvas.pack()

    def draw_map(self):
        self.canvas.delete("all")  # Clear the canvas
        for y in range(self.map.dimensions[1]):
            for x in range(self.map.dimensions[0]):
                tile = self.map.get_tile(x, y)
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
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close event
        self.root.mainloop()

    def on_close(self):
        self.root.quit()  # Quit the tkinter main loop
        self.root.destroy()  # Destroy the tkinter window

# Example usage
if __name__ == "__main__":
    player = Player.get_position
    visualizer = MapVisualizer(map, player)

    visualizer.run()