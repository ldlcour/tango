import os
import json
from itertools import count
from scipy.interpolate import interp1d


class Linear:
    _ids = count(0)

    def __init__(self, casepath, datapath):
        self.id = next(self._ids)

        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "linear" + str(self.id) + "/settings.txt")) as f:
                parameters = json.load(f)

        self.initializedinputgrid = False
        self.initializedoutputgrid = False
        self.inputgrid = []
        self.outputgrid = []
        self.f = []

    def setinputgrid(self, z):
        self.initializedinputgrid = True
        self.inputgrid = z

    def setoutputgrid(self, z):
        self.initializedoutputgrid = True
        self.outputgrid = z

    def initialize(self):
        if not self.initializedinputgrid or not self.initializedoutputgrid:
            Exception("Input or output grid not set")

    def initializestep(self):
        pass

    def map(self, a):
        f = interp1d(self.inputgrid, a, bounds_error=False, fill_value="extrapolate")
        return f(self.outputgrid)

    def finalizestep(self):
        pass

    def finalize(self):
        pass
