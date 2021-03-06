import numpy as np
import math as m
import os
import json
from scipy.linalg import solve_banded
from itertools import count


class PipeFlow:
    Al = 4  # Number of terms below diagonal in matrix
    Au = 4  # Number of terms above diagonal in matrix
    _ids = count(0)

    def __init__(self, casepath, datapath):
        self.id = next(self._ids)

        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "pipeflow" + str(self.id) + "/settings.txt")) as f:
                parameters = json.load(f)

        self.datapath = os.path.join(datapath, "pipeflow" + str(self.id))
        os.makedirs(self.datapath, exist_ok=True)
        self.filepath = os.path.join(self.datapath, "output.dat")
        self.datafile = open(self.filepath, mode='w')

        l = parameters["l"]  # Length
        self.d = parameters["d"]  # Diameter
        self.rhof = parameters["rhof"]  # Density

        self.ureference = parameters["ureference"]  # Reference of inlet boundary condition
        self.uamplitude = parameters["uamplitude"]  # Amplitude of inlet boundary condition
        self.uperiod = parameters["uperiod"]  # Period of inlet boundary condition
        self.utype = parameters["utype"]  # Type of inlet boundary condition

        e = parameters["e"]  # Young"s modulus of structure
        h = parameters["h"]  # Thickness of structure
        self.cmk2 = (e * h) / (self.rhof * self.d)  # Wave speed squared of outlet boundary condition

        self.m = parameters["m"]  # Number of segments
        self.dz = l / self.m  # Segment length
        self.z = np.arange(self.dz / 2.0, l, self.dz)  # Data is stored in cell centers

        self.n = 0  # Time step
        self.dt = 0.0  # Time step size
        self.alpha = 0.0  # Numerical damping parameter due to central discretization of pressure in momentum equation

        self.newtonmax = parameters["newtonmax"]  # Maximal number of Newton iterations
        self.newtontol = parameters["newtontol"]  # Tolerance of Newton iterations

        # Initialization
        self.u = np.ones(self.m + 2) * self.ureference  # Velocity
        self.un = np.ones(self.m + 2) * self.ureference  # Previous velocity
        self.p = np.zeros(self.m + 2)  # Pressure
        self.pn = np.zeros(self.m + 2)  # Previous pressure (only value at outlet is used)
        self.a = np.ones(self.m + 2) * m.pi * self.d ** 2 / 4.0  # Area of cross section
        self.an = np.ones(self.m + 2) * m.pi * self.d ** 2 / 4.0  # Previous area of cross section

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
        a = self.a[1:self.m + 1]
        return np.array(a)

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
                self.un = np.array(self.u)
                self.pn = np.array(self.p)
                self.an = np.array(self.a)
        else:
            Exception("Not initialized")

    def calculate(self, a):
        # Input does not contain boundary conditions
        self.a[1:self.m + 1] = a
        self.a[0] = self.a[1]
        self.a[self.m + 1] = self.a[self.m]

        # Newton iterations
        converged = False
        f = self.getresidual()
        residual0 = np.linalg.norm(f)
        if residual0:
            for s in range(self.newtonmax):
                j = self.getjacobian()
                b = -f
                x = solve_banded((PipeFlow.Al, PipeFlow.Au), j, b)
                self.u += x[0::2]
                self.p += x[1::2]
                self.u[0] = self.getboundary()
                f = self.getresidual()
                residual = np.linalg.norm(f)
                if residual / residual0 < self.newtontol:
                    converged = True
                    break
            if not converged:
                Exception("Newton failed to converge")

        # Output does not contain boundary conditions
        p = self.p[1:self.m + 1]
        # Return copy of output
        return np.array(p)

    def finalizestep(self):
        if self.initialized:
            if self.initializedstep:
                self.initializedstep = False
            else:
                Exception("No step ongoing")
        else:
            Exception("Not initialized")
        np.savetxt(self.datafile, [self.a])
        np.savetxt(self.datafile, [self.p])
        np.savetxt(self.datafile, [self.u])

    def finalize(self):
        if self.initialized:
            self.initialized = False
        else:
            Exception("Not initialized")

    def getboundary(self):
        if self.utype == 1:
            u = self.ureference + self.uamplitude * m.sin(2.0 * m.pi * (self.n * self.dt) / self.uperiod)
        elif self.utype == 2:
            u = self.ureference + self.uamplitude
        elif self.utype == 3:
            u = self.ureference + self.uamplitude * (m.sin(m.pi * (self.n * self.dt) / self.uperiod)) ** 2
        else:
            u = self.ureference + self.uamplitude * (self.n * self.dt) / self.uperiod
        return u

    def getresidual(self):
        usign = self.u[1:self.m + 1] > 0
        ur = self.u[1:self.m + 1] * usign + self.u[2:self.m + 2] * (1.0 - usign)
        ul = self.u[0:self.m] * usign + self.u[1:self.m + 1] * (1.0 - usign)
        self.alpha = m.pi * self.d ** 2 / 4.0 / (self.ureference + self.dz / self.dt)

        f = np.zeros(2 * self.m + 4)
        f[0] = self.u[0] - self.getboundary()
        f[1] = self.p[0] - (2.0 * self.p[1] - self.p[2])
        f[2:2 * self.m + 2:2] = (self.dz / self.dt * (self.a[1:self.m + 1] - self.an[1:self.m + 1])
                                 + (self.u[1:self.m + 1] + self.u[2:self.m + 2])
                                 * (self.a[1:self.m + 1] + self.a[2:self.m + 2]) / 4.0
                                 - (self.u[1:self.m + 1] + self.u[0:self.m])
                                 * (self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0
                                 - self.alpha * (self.p[2:self.m + 2] - 2.0 * self.p[1:self.m + 1] + self.p[0:self.m]))
        f[3:2 * self.m + 3:2] = (self.dz / self.dt * (self.u[1:self.m + 1] * self.a[1:self.m + 1]
                                                      - self.un[1:self.m + 1] * self.an[1:self.m + 1])
                                 + ur * (self.u[1:self.m + 1] + self.u[2:self.m + 2])
                                 * (self.a[1:self.m + 1] + self.a[2:self.m + 2]) / 4.0
                                 - ul * (self.u[1:self.m + 1] + self.u[0:self.m])
                                 * (self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0
                                 + ((self.p[2:self.m + 2] - self.p[1:self.m + 1])
                                    * (self.a[1:self.m + 1] + self.a[2:self.m + 2])
                                    + (self.p[1:self.m + 1] - self.p[0:self.m])
                                    * (self.a[1:self.m + 1] + self.a[0:self.m])) / 4.0)
        f[2 * self.m + 2] = self.u[self.m + 1] - (2.0 * self.u[self.m] - self.u[self.m - 1])
        f[2 * self.m + 3] = self.p[self.m + 1] - (2.0 * (self.cmk2 - (m.sqrt(self.cmk2 - self.pn[self.m + 1] / 2.0)
                                                                      - (self.u[self.m + 1] - self.un[self.m + 1])
                                                                      / 4.0) ** 2))
        return f

    def getjacobian(self):
        usign = self.u[1:self.m + 1] > 0
        j = np.zeros((PipeFlow.Al + PipeFlow.Au + 1, 2 * self.m + 4))
        j[PipeFlow.Au + 0 - 0, 0] = 1.0  # [0,0]
        j[PipeFlow.Au + 1 - 1, 1] = 1.0  # [1,1]
        j[PipeFlow.Au + 1 - 3, 3] = -2.0  # [1,3]
        j[PipeFlow.Au + 1 - 5, 5] = 1.0  # [1,5]

        j[PipeFlow.Au + 2, 0:2 * self.m + 0:2] = -(self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0  # [2*i, 2*(i-1)]
        j[PipeFlow.Au + 3, 0:2 * self.m + 0:2] = (-((self.u[1:self.m + 1] + 2.0 * self.u[0:self.m]) * usign
                                                    + self.u[1:self.m + 1] * (1.0 - usign))
                                                  * (self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0)  # [2*i+1, 2*(i-1)]
        j[PipeFlow.Au + 1, 1:2 * self.m + 1:2] = -self.alpha  # [2*i, 2*(i-1)+1]
        j[PipeFlow.Au + 2, 1:2 * self.m + 1:2] = -(self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0  # [2*i+1, 2*(i-1)+1]

        j[PipeFlow.Au + 0, 2:2 * self.m + 2:2] = ((self.a[1:self.m + 1] + self.a[2:self.m + 2]) / 4.0
                                                  - (self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0)  # [2*i, 2*i]
        j[PipeFlow.Au + 1, 2:2 * self.m + 2:2] = (self.dz / self.dt * self.a[1:self.m + 1]
                                                  + ((2.0 * self.u[1:self.m + 1] + self.u[2:self.m + 2]) * usign
                                                     + self.u[2:self.m + 2] * (1.0 - usign))
                                                  * (self.a[1:self.m + 1] + self.a[2:self.m + 2]) / 4.0
                                                  - (self.u[0:self.m] * usign
                                                     + (2.0 * self.u[1:self.m + 1] + self.u[0:self.m]) * (1.0 - usign))
                                                  * (self.a[1:self.m + 1] + self.a[0:self.m]) / 4.0)  # [2*i+1, 2*i]
        j[PipeFlow.Au - 1, 3:2 * self.m + 3:2] = 2.0 * self.alpha  # [2*i, 2*i+1]
        j[PipeFlow.Au + 0, 3:2 * self.m + 3:2] = (-(self.a[1:self.m + 1] + self.a[2:self.m + 2])
                                                  + (self.a[1:self.m + 1] + self.a[0:self.m])) / 4.0  # [2*i+1, 2*i+1]

        j[PipeFlow.Au - 2, 4:2 * self.m + 4:2] = (self.a[1:self.m + 1] + self.a[2:self.m + 2]) / 4.0  # [2*i, 2*(i+1)]
        j[PipeFlow.Au - 1, 4:2 * self.m + 4:2] = ((self.u[1:self.m + 1] * usign + (self.u[1:self.m + 1]
                                                                                   + 2.0 * self.u[2:self.m + 2])
                                                   * (1.0 - usign))
                                                  * (self.a[1:self.m + 1]
                                                     + self.a[2:self.m + 2]) / 4.0)  # [2*i+1, 2*(i+1)]
        j[PipeFlow.Au - 3, 5:2 * self.m + 5:2] = -self.alpha  # [2*i, 2*(i+1)+1]
        j[PipeFlow.Au - 2, 5:2 * self.m + 5:2] = (self.a[1:self.m + 1]
                                                  + self.a[2:self.m + 2]) / 4.0  # [2*i+1, 2*(i+1)+1]

        j[PipeFlow.Au + (2 * self.m + 2) - (2 * self.m + 2), 2 * self.m + 2] = 1.0  # [2*m+2, 2*m+2]
        j[PipeFlow.Au + (2 * self.m + 2) - (2 * self.m), 2 * self.m] = -2.0  # [2*m+2, 2*m]
        j[PipeFlow.Au + (2 * self.m + 2) - (2 * self.m - 2), 2 * self.m - 2] = 1.0  # [2*m+2, 2*m-2]
        j[PipeFlow.Au + (2 * self.m + 3) - (2 * self.m + 2), 2 * self.m + 2] = (-(m.sqrt(self.cmk2
                                                                                         - self.pn[self.m + 1] / 2.0)
                                                                                  - (self.u[self.m + 1]
                                                                                     - self.un[self.n + 1])
                                                                                  / 4.0))  # [2*m+3, 2*m+2]
        j[PipeFlow.Au + (2 * self.m + 3) - (2 * self.m + 3), 2 * self.m + 3] = 1.0  # [2*m+3, 2*m+3]

        return j
