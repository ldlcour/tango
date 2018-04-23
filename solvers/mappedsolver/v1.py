import os
import json
import importlib
from itertools import count


def createinstance(name, settings, casepath, datapath):
    objectmodule = importlib.import_module(settings[name + "module"])
    objectclass = getattr(objectmodule, settings[name + "class"])
    return objectclass(casepath, datapath)


class MappedSolver:
    _ids = count(0)

    def __init__(self, casepath, datapath):
        self.id = next(self._ids)

        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "mappedsolver" + str(self.id) + "/settings.txt")) as f:
                parameters = json.load(f)

        self.solver = createinstance("solver", parameters, casepath, datapath)
        self.inputmapper = createinstance("inputmapper", parameters, casepath, datapath)
        self.outputmapper = createinstance("outputmapper", parameters, casepath, datapath)

        self.initialized = False
        self.initializedstep = False

    def getinputgrid(self):
        return 0

    def setinputgrid(self, z):
        print(0)

    def getoutputgrid(self):
        return 0

    def setoutputgrid(self, z):
        print(0)

    def getinputdata(self):
        return 0

    def gettimestep(self):
        return self.solver.gettimestep()

    def settimestep(self, dt):
        if self.initializedstep:
            Exception("Step ongoing")
        else:
            self.solver.settimestep(dt)

    def initialize(self):
        if self.initialized:
            Exception("Already initialized")
        else:
            self.initialized = True

    def initializestep(self):
        if self.initialized:
            if self.initializedstep:
                Exception("Step ongoing")
            else:
                self.initializedstep = True
        else:
            Exception("Not initialized")

    def calculate(self, a):
        return 0

    def finalizestep(self):
        if self.initialized:
            if self.initializedstep:
                self.initializedstep = False
            else:
                Exception("No step ongoing")
        else:
            Exception("Not initialized")

    def finalize(self):
        if self.initialized:
            self.initialized = False
        else:
            Exception("Not initialized")
