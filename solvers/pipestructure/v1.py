import numpy as np
import math as m
import os
import json


class PipeStructure:
    def __init__(self, casepath, datapath):
        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "pipestructure/settings.txt")) as f:
                parameters = json.load(f)

        self.datapath = os.path.join(datapath, "pipestructure")
        os.makedirs(self.datapath, exist_ok=True)
        self.filepath = os.path.join(self.datapath, "output.dat")
        self.datafile = open(self.filepath, mode='w')

        l = parameters["l"]  # Length
        self.d = parameters["d"]  # Diameter
        self.rhof = parameters["rhof"]  # Density

        e = parameters["e"]  # Young"s modulus of structure
        h = parameters["h"]  # Thickness of structure
        self.cmk2 = (e * h) / (self.rhof * self.d)  # Wave speed squared

        self.m = parameters["m"]  # Number of segments
        self.dz = l / self.m  # Segment length
        self.z = np.arange(self.dz / 2.0, l, self.dz)  # Data is stored in cell centers

        self.n = 0  # Time step
        self.dt = 0  # Time step size

        # Initialization
        self.p = np.ones(self.m) * 2.0 * self.cmk2  # Pressure
        self.a = np.ones(self.m) * m.pi * self.d ** 2 / 4.0  # Area of cross section
        self.p0 = 0.0  # Reference pressure
        self.a0 = m.pi * self.d ** 2 / 4.0  # Reference area of cross section
        self.c02 = self.cmk2 - self.p0 / 2.0  # Wave speed squared with reference pressure

        self.initialized = False
        self.initializedstep = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.datafile.close()

    def getinputgrid(self):
        return self.z

    def setinputgrid(self, z):
        if np.linalg.norm(self.z - z) / np.linalg.norm(self.z) > np.finfo(float).eps:
            Exception("Mapper not implemented")

    def getoutputgrid(self):
        return self.z

    def setoutputgrid(self, z):
        if np.linalg.norm(self.z - z) / np.linalg.norm(self.z) > np.finfo(float).eps:
            Exception("Mapper not implemented")

    def getinputdata(self):
        return self.p

    def gettimestep(self):
        return self.dt

    def settimestep(self, dt):
        if self.initializedstep:
            Exception("Step ongoing")
        else:
            self.dt = dt

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
                self.n += 1
                self.initializedstep = True
        else:
            Exception("Not initialized")

    def calculate(self, p):
        # Independent rings model
        self.p = p
        for i in range(len(self.p)):
            if self.p[i] > 2.0 * self.c02 + self.p0:
                raise ValueError("Unphysical pressure")
        for i in range(len(self.a)):
            self.a[i] = self.a0 * (2.0 / (2.0 + (self.p0 - self.p[i]) / self.c02)) ** 2
        # Return copy of output
        return np.array(self.a)

    def finalizestep(self):
        if self.initialized:
            if self.initializedstep:
                self.initializedstep = False
            else:
                Exception("No step ongoing")
        else:
            Exception("Not initialized")
        np.savetxt(self.datafile, [self.p])
        np.savetxt(self.datafile, [self.a])

    def finalize(self):
        if self.initialized:
            self.initialized = False
        else:
            Exception("Not initialized")
