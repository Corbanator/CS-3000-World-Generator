from enum import IntEnum
from collections import namedtuple


class Direction(IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7

    def opposite(self):
        return Direction((self + 4) % 8)

    def clockwise_turn(self):
        return Direction((self + 2) % 8)

    def counter_clockwise_turn(self):
        return Direction((self + 6) % 8)

    def get_tuple(self):
        match self:
            case Direction.N: return (0, -1)
            case Direction.NE: return (1, -1)
            case Direction.E: return (1, 0)
            case Direction.SE: return (1, 1)
            case Direction.S: return (0, 1)
            case Direction.SW: return (-1, 1)
            case Direction.W: return (-1, 0)
            case Direction.NW: return (-1, -1)

    @staticmethod
    def all_cardinal():
        return {Direction.N, Direction.E, Direction.S, Direction.W}

    @staticmethod
    def get_set_from_str(input: str):
        match input:
            case "A":
                return Direction.all_cardinal()
            case "N":
                return {Direction.N}
            case "E":
                return {Direction.E}
            case "S":
                return {Direction.S}
            case "W":
                return {Direction.W}
            case default:
                return set()

class Position(namedtuple("Position", "x y")):
    def __add__(self, other: tuple):
        return Position(self[0] + other[0], self[1] + other[1])

    def traverse(self, direction: Direction):
        return self + direction.get_tuple()
