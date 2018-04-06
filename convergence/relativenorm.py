import numpy as np
import os
import json


class RelativeNorm:
    def __init__(self, parameters):
        if not type(parameters) is dict:
            with open(os.path.join(parameters, "settings.txt")) as f:
                parameters = json.load(f)
        self.kmin = parameters["kmin"]
        self.mintol = parameters["mintol"]

        self.k = 0
        self.added = False
        self.r = 0
        self.r0 = 0

    def add(self, r):
        self.k += 1
        if self.added:
            self.r = np.linalg.norm(r)
        else:
            self.r0 = np.linalg.norm(r)
            self.added = True

    def issatisfied(self):
        return self.r < max(self.r0, self.mintol) and self.k >= self.kmin

    def initializestep(self):
        self.k = 0
        self.r = 0
        self.r0 = 0

    def finalizestep(self):
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
