import numpy as np


class PipeFlow:

    def __init__(self, parameters):
        l = parameters['l']  # Length
        d = parameters['d']  # Diameter
        self.rho = parameters['rho']  # Density
        self.m = parameters['m']  # Number of segments

        # Initialization
        self.u = np.zeros(self.m)  # Velocity
        self.un = np.zeros(self.m)  # Previous velocity
        self.p = np.zeros(self.m)  # Pressure
        self.a = np.ones(self.m)*np.pi*d**2/4.0  # Area of cross section
        self.an = np.ones(self.m)*np.pi*d**2/4.0  # Previous area of cross section

        # Data is stored in cell centers
        self.dx = l/self.m
        self.x = np.arange(self.dx/2, self.dx, l)

        self.dt = 0
        self.n = 0

        self.initialized = False
        self.initializedstep = False

    def getinputgrid(self):
        return self.x

    def setinputgrid(self, x):
        if np.linalg.norm(self.x-x)/np.linalg.norm(self.x) > np.finfo(float).eps:
            Exception('Mapper not implemented')

    def getoutputgrid(self):
        return self.x

    def setoutputgrid(self, x):
        if np.linalg.norm(self.x-x)/np.linalg.norm(self.x) > np.finfo(float).eps:
            Exception('Mapper not implemented')

    def gettimestep(self):
        return self.dt

    def settimestep(self, dt):
        if self.initializedstep:
            Exception('Step ongoing')
        else:
            self.dt = dt

    def initialize(self):
        if self.initialized:
            Exception('Already initialized')
        else:
            self.initialized = True

    def initializestep(self):
        if self.initialized:
            if self.initializedstep:
                Exception('Step ongoing')
            else:
                self.n += 1
                self.initializedstep = True
        else:
            Exception('Not initialized')

    def calculate(self, a):
        self.a = a
        return self.p

    def finalizestep(self):
        if self.initialized:
            if self.initializedstep:
                self.initializedstep = False
            else:
                Exception('No step ongoing')
        else:
            Exception('Not initialized')

    def finalize(self):
        if self.initialized:
            self.initialized = False
        else:
            Exception('Not initialized')
