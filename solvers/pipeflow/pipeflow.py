import numpy as np
import math as m
from scipy.linalg import solve_banded


class PipeFlow:

    def __init__(self, parameters):
        l = parameters['l']  # Length
        d = parameters['d']  # Diameter
        self.rho = parameters['rho']  # Density

        self.ureference = parameters['ureference']  # Reference of inlet boundary condition
        self.uamplitude = parameters['uamplitude']  # Amplitude of inlet boundary condition
        self.uperiod = parameters['uperiod']  # Period of inlet boundary condition
        self.utype = parameters['utype']  # Type of inlet boundary condition

        self.m = parameters['m']  # Number of segments
        self.dz = l / self.m
        self.z = np.arange(self.dz / 2.0, self.dz, l)  # Data is stored in cell centers

        self.n = 0  # Time step
        self.dt = 0  # Time step size

        self.newtonmax = parameters['newtonmax']  # Maximal number of Newton iterations
        self.newtontol = parameters['newtontol']  # Tolerance of Newton iterations


        # Initialization
        self.u = np.zeros(self.m+2)  # Velocity
        self.un = np.zeros(self.m+2)  # Previous velocity
        self.p = np.zeros(self.m+2)  # Pressure
        self.a = np.ones(self.m+2)*np.pi*d**2/4.0  # Area of cross section
        self.an = np.ones(self.m+2)*np.pi*d**2/4.0  # Previous area of cross section

        self.initialized = False
        self.initializedstep = False

    def getinputgrid(self):
        return self.z

    def setinputgrid(self, z):
        if np.linalg.norm(self.z-z)/np.linalg.norm(self.z) > np.finfo(float).eps:
            Exception('Mapper not implemented')

    def getoutputgrid(self):
        return self.z

    def setoutputgrid(self, z):
        if np.linalg.norm(self.z-z)/np.linalg.norm(self.z) > np.finfo(float).eps:
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

    def setboundary(self):
        if self.utype == 1:
            self.u[0] = self.ureference+self.uamplitude*m.sin(2.0*m.pi*self.n/self.uperiod)
        elif self.utype == 2:
            self.u[0] = self.ureference+self.uamplitude
        elif self.utype == 3:
            self.u[0] = self.ureference+self.uamplitude*(m.sin(m.pi*self.n/self.uperiod))**2
        else:
            self.u[0] = self.ureference+self.uamplitude*self.n/self.uperiod

    def getresidual(self):
        return 0

    def getjacobian(self):
        return 0

    def calculate(self, a):
        # Input does not contain boundary conditions
        self.a[1:-2] = a
        self.a[0] = self.a[1]
        self.a[-1] = self.a[-2]

        # Newton iterations
        converged = False
        f = self.getresidual()
        residual0 = np.linalg.norm(f)
        for s in range(self.newtonmax):
            A = self.getjacobian()
            b = -f
            x = solve_banded(landu, A, b)
            self.u += x[0:2:-1]
            self.p += x[1:2:-1]
            self.setboundary()
            f = self.getresidual()
            residual = np.linalg.norm(f)
            if residual/residual0 < self.newtontol:
                converged = True
                break
        if not(converged):
            Exception('Newton failed to converge')
        p = self.p[1:-2]
        return p

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
