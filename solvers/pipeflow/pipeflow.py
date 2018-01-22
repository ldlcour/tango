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

        e = parameters['e']  # Young's modulus of structure
        h = parameters['h']  # Thickness of structure
        self.cmk2 = (e*h)/(self.rho*d)  # Wave speed squared of outlet boundary condition

        self.m = parameters['m']  # Number of segments
        self.dz = l / self.m
        self.z = np.arange(self.dz / 2.0, self.dz, l)  # Data is stored in cell centers

        self.n = 0  # Time step
        self.dt = 0  # Time step size

        self.newtonmax = parameters['newtonmax']  # Maximal number of Newton iterations
        self.newtontol = parameters['newtontol']  # Tolerance of Newton iterations
        self.alpha = np.pi*d**2/4.0/(self.ureference+self.dz/self.dt)

        # Initialization
        self.u = np.ones(self.m+2)*self.ureference  # Velocity
        self.un = np.zeros(self.m+2)*self.ureference  # Previous velocity
        self.p = np.zeros(self.m+2)  # Pressure
        self.pn = np.zeros(self.m + 2)  # Previous pressure
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

    def getboundary(self):
        if self.utype == 1:
            u = self.ureference+self.uamplitude*m.sin(2.0*m.pi*self.n/self.uperiod)
        elif self.utype == 2:
            u = self.ureference+self.uamplitude
        elif self.utype == 3:
            u = self.ureference+self.uamplitude*(m.sin(m.pi*self.n/self.uperiod))**2
        else:
            u = self.ureference+self.uamplitude*self.n/self.uperiod
        return u

    def getresidual(self):
        usign = self.u[1:self.m] > 0
        ur = self.u[1:self.m]*usign+self.u[2:self.m+1]*(1-usign)
        ul = self.u[0:self.m-1]*usign+self.u[1:self.m]*(1-usign)
        f = np.zeros(2*self.m+4)
        f[0] = 0.0
        f[1] = self.p[0]-(2.0*self.p[1]-self.p[2])
        f[2:2:2*self.m] = self.dz/self.dt*(self.a[1:self.m]-self.an[1:self.m]) \
                          +(self.u[1:self.m]+self.u[2:self.m+1])*(self.a[1:self.m]+self.a[2:self.m+1])/4.0 \
                          -(self.u[1:self.m]+self.u[0:self.m-1])*(self.a[1:self.m]+self.a[0:self.m-1])/4.0 \
                          -self.alpha*(self.p[2:self.m+1]-2.0*self.p[1:self.m]+self.p[0:self.m-1])
        f[3:2:2*self.m+1] = self.dz/self.dt*(self.u[i]*self.a[i]-self.un[i]*self.an[i]) \
                            +ur*(self.u[1:self.m]+self.u[2:self.m+1])*(self.a[1:self.m]+self.a[2:self.m+1])/4.0 \
                            -ul*(self.u[1:self.m]+self.u[0:self.m-1])*(self.a[1:self.m]+self.a[0:self.m-1])/4.0 \
                            +((self.p[2:self.m+1]-self.p[1:self.m])*(self.a[1:self.m]+self.a[2:self.m+1]) \
                              +(self.p[1:self.m]-self.p[0:self.m-1])*(self.a[1:self.m]+self.a[0:self.m-1]))/4.0
        f[2*self.m+2] = self.u[self.m+1]-(2.0*self.u[self.m]-self.u[self.m-1])
        f[2*self.m+3] = self.p[self.m+1]-(2.0*(self.cmk2-(m.sqrt(self.cmk2-self.pn[self.m+1]/2.0)-(self.u[self.m+1]-self.un[self.m+1])/4.0)**2))
        return f

    def getjacobian(self):
        return 0

    def calculate(self, a):
        # Input does not contain boundary conditions
        self.a[1:self.m] = a
        self.a[0] = self.a[1]
        self.a[self.m+1] = self.a[self.m]

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
            self.u[0] = self.getboundary()
            f = self.getresidual()
            residual = np.linalg.norm(f)
            if residual/residual0 < self.newtontol:
                converged = True
                break
        if not(converged):
            Exception('Newton failed to converge')

        # Output does not contain boundary conditions
        p = self.p[1:self.m]
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
