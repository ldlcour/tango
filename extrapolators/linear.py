import numpy as np
from itertools import count


class Linear:
    _ids = count(0)

    def __init__(self, *_):
        self.id = next(self._ids)

        self.n = 0
        self.xp = np.array([])
        self.x = np.array([])
        self.xn = np.array([])
        self.added = False

    def initialize(self, x):
        self.xp = np.array(x)
        self.x = np.array(x)
        self.xn = np.zeros_like(x)

    def update(self, x):
        self.xp = np.array(x)
        self.added = True

    def predict(self):
        self.xp = 2.0 * self.x - self.xn
        return np.array(self.xp)

    def initializestep(self):
        self.n += 1
        self.xn = self.x
        self.x = self.xp

    def finalizestep(self):
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
