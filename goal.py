import random

from position import Direction, Position

class GoalManager:
    def __init__(self, map, player):
        self.map = map
        self.player = player  # Store the player object
        self.keys = []
        self.goal_position = None
        self.place_keys()
        self.place_goal()

    def place_keys(self):
        num_keys = random.randint(1, 5)
        for _ in range(num_keys):
            while True:
                x = random.randint(0, self.map.dimensions[0] - 1)
                y = random.randint(0, self.map.dimensions[1] - 1)
                pos = Position(x, y)
                if self.map.get_tile(pos) not in {"O", "U"} and self.is_reachable(pos):
                    self.keys.append((pos))
                    self.map.set_tile(pos, "U")  # "U" represents a button
                    break

    def place_goal(self):
        while True:
            x = random.randint(0, self.map.dimensions[0] - 1)
            y = random.randint(0, self.map.dimensions[1] - 1)
            pos = Position(x, y)
            if self.map.get_tile(pos) not in {"O", "U"} and self.is_reachable(pos):
                self.goal_position = (pos)
                self.map.set_tile(pos, "R")  # "R" represents a red goal (locked)
                break

    def collect_key(self, pos: Position):
        if (pos) in self.keys:
            self.keys.remove(pos)
            self.map.set_tile(pos, "C")  # "C" represents a pressed button
            if not self.keys:  # All buttons pressed
                g_pos = self.goal_position
                self.map.set_tile(g_pos, "G")  # "G" represents a green goal (unlocked)

    def is_goal_reachable(self):
        return not self.keys  # Goal is reachable only when all keys are collected

    def is_reachable(self, target_pos: Position):
        visited = set()
        stack = [self.player.pos]

        while stack:
            pos = stack.pop()
            if pos == target_pos:
                return True

            if pos in visited:
                continue

            visited.add(pos)

            for direction in Direction.all_cardinal():
                new_pos = pos + direction.get_tuple()
                if 0 <= new_pos.x < self.map.dimensions[0] and 0 <= new_pos.y < self.map.dimensions[1]:
                    tile = self.map.get_tile(new_pos)
                    if tile not in {"U", "R"} and self.map.tileset.is_walkable(tile):
                        stack.append(new_pos)

        return False

    def restart_game(self, map, player):
        self.map = map
        self.player = player
        self.keys = []
        self.goal_position = None
        self.place_keys()
        self.place_goal()
        print("Game has been reset with new keys and goal.")
