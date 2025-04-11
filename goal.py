import random

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
                if self.map.get_tile(x, y) not in {"O", "U"} and self.is_reachable(x, y):
                    self.keys.append((x, y))
                    self.map.set_tile(x, y, "U")  # "U" represents a button
                    break

    def place_goal(self):
        while True:
            x = random.randint(0, self.map.dimensions[0] - 1)
            y = random.randint(0, self.map.dimensions[1] - 1)
            if self.map.get_tile(x, y) not in {"O", "U"} and self.is_reachable(x, y):
                self.goal_position = (x, y)
                self.map.set_tile(x, y, "R")  # "R" represents a red goal (locked)
                break

    def collect_key(self, x, y):
        if (x, y) in self.keys:
            self.keys.remove((x, y))
            self.map.set_tile(x, y, "C")  # "C" represents a pressed button
            self.map.original_tiles[y * self.map.dimensions[0] + x] = "C"  # Update state to pressed button
            if not self.keys:  # All buttons pressed
                gx, gy = self.goal_position
                self.map.set_tile(gx, gy, "G")  # "G" represents a green goal (unlocked)

    def is_goal_reachable(self):
        return not self.keys  # Goal is reachable only when all keys are collected

    def is_reachable(self, x, y):
        visited = set()
        stack = [(self.player.x, self.player.y)]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) == (x, y):
                return True

            if (cx, cy) in visited:
                continue

            visited.add((cx, cy))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.map.dimensions[0] and 0 <= ny < self.map.dimensions[1]:
                    if self.map.get_tile(nx, ny) not in {"O", "U", "R"}:
                        stack.append((nx, ny))

        return False

    def restart_game(self, map, player):
        self.map = map
        self.player = player
        self.keys = []
        self.goal_position = None
        self.place_keys()
        self.place_goal()
        print("Game has been reset with new keys and goal.")