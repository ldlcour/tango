import numpy as np
import os
import json


class RelativeNorm:
    def __init__(self, casepath, datapath):
        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "settings.txt")) as f:
                parameters = json.load(f)

        self.datapath = os.path.join(datapath, "relativenorm")
        os.makedirs(self.datapath, exist_ok=True)
        self.filepath = os.path.join(self.datapath, "output.dat")
        self.datafile = open(self.filepath, mode='w')

        self.kmin = parameters["kmin"]
        self.mintol = parameters["mintol"]
        self.reltol = parameters["reltol"]

        self.n = 0
        self.k = 0
        self.added = False
        self.r = 0
        self.r0 = 0

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.datafile.close()

    def add(self, r):
        self.k += 1
        if self.added:
            self.r = np.linalg.norm(r)
        else:
            self.r0 = np.linalg.norm(r)
            self.added = True
        self.datafile.write(self.status() + "\n")

    def status(self):
        return "{:d} {:d} {:e}".format(self.n, self.k, self.r)

    def issatisfied(self):
        return self.r < max(self.reltol * self.r0, self.mintol) and self.k >= self.kmin

    def initializestep(self):
        self.n += 1
        self.k = 0
        self.r = 0
        self.r0 = 0

    def finalizestep(self):
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
