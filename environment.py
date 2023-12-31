import numpy as np
from .util import liang_barsky

class GridEnvironment:
    def __init__(self, grid):
        self.grid = grid

    def cartesian_to_grid(self, y):
        h, _ = np.shape(self.grid)
        return h - 1 - y

    def grid_to_cartesian(self, y_index):
        h, _ = np.shape(self.grid)
        return h - 1 - y_index

    def is_obstacle(self, pos):
        h, w = np.shape(self.grid)
        x = pos[0]
        y = self.cartesian_to_grid(pos[1])

        return not self.grid[y, x]

    def is_valid(self, pos):
        h, w = np.shape(self.grid)
        return pos[0] < w and pos[1] < h and pos[0] >= 0 and pos[1] >= 0

    def is_free(self, pos, pos_next):
        if pos == pos_next:
            return True

        by, bx = np.nonzero(self.grid == 0)
        by = self.grid_to_cartesian(by)
        for k in range(by.shape[0]):
            if liang_barsky(bx[k] - 0.5, bx[k] + 0.5, by[k] + 0.5, by[k] - 0.5, pos[0], pos[1], pos_next[0], pos_next[1]):
                return False

        return True