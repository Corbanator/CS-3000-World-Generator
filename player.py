import random
from position import Position

class Player:
    def __init__(self, dimensions):
        x = random.randint(0, dimensions[0] - 1)
        y = random.randint(0, dimensions[1] - 1)
        self.pos = Position(x, y)

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.x

    def update_map(self, map):
        map.set_tile(self.x, self.y, "P")

    def handle_keypress(self, event, map, visualizer):
        key = event.keysym
        if key == "Up":
            self.move(0, -1, map, visualizer)
        elif key == "Down":
            self.move(0, 1, map, visualizer)
        elif key == "Left":
            self.move(-1, 0, map, visualizer)
        elif key == "Right":
            self.move(1, 0, map, visualizer)
        elif key == "q":
            visualizer.root.destroy()

    def move(self, dx, dy, map, visualizer):
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < map.dimensions[0] and 0 <= new_y < map.dimensions[1]:
            if map.get_tile(new_x, new_y) != "O":
                if map.get_tile(new_x, new_y) == "U":
                    visualizer.goal_manager.collect_key(new_x, new_y)
                elif map.get_tile(new_x, new_y) == "G":  # Check if the player touches the goal
                    from mapVisual import restart_game  # Import the standalone restart_game function
                    restart_game(visualizer)  # Call the standalone restart_game function
                    return
                map.set_tile(self.x, self.y, map.original_tiles[self.y * map.dimensions[0] + self.x])
                self.x = new_x
                self.y = new_y
                map.set_tile(self.x, self.y, "P")
                visualizer.update()
