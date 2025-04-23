import random
from position import Direction, Position

class Player:
    def __init__(self, dimensions):
        x = random.randint(0, dimensions[0] - 1)
        y = random.randint(0, dimensions[1] - 1)
        self.pos = Position(x, y)

    @property
    def x(self):
        return self.pos.x

    @x.setter
    def x(self, x):
        self.pos = Position(x, self.pos.y)

    @property
    def y(self):
        return self.pos.x

    @y.setter
    def y(self, y):
        self.pos = Position(self.pos.x, y)

    def update_map(self, map):
        map.set_visual_tile(self.pos, "P")

    def handle_keypress(self, event, map, visualizer):
        key = event.keysym
        if key == "Up":
            self.move(Direction.N, map, visualizer)
        elif key == "Down":
            self.move(Direction.S, map, visualizer)
        elif key == "Left":
            self.move(Direction.W, map, visualizer)
        elif key == "Right":
            self.move(Direction.E, map, visualizer)
        elif key == "q":
            visualizer.root.destroy()

    def move(self, direction: Direction, map, visualizer):
        new_pos = self.pos + direction.get_tuple()

        if 0 <= new_pos.x < map.dimensions[0] and 0 <= new_pos.y < map.dimensions[1]:
            tile = map.get_tile(new_pos)
            if map.tileset.is_walkable(tile):
                if map.get_tile(new_pos) == "U":
                    visualizer.goal_manager.collect_key(new_pos)
                elif map.get_tile(new_pos) == "G":  # Check if the player touches the goal
                    from mapVisual import restart_game  # Import the standalone restart_game function
                    restart_game(visualizer)  # Call the standalone restart_game function
                    return
                map.clear_visual_tile(self.pos)
                self.pos = new_pos
                map.set_visual_tile(self.pos, "P")
                visualizer.update()
