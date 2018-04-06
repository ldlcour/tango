import numpy as np
from scipy.linalg import qr, solve_triangular


class IQNILS:
    def __init__(self, parameters):
        self.added = False
        self.rref = np.array([])
        self.xtref = np.array([])
        self.V = np.matrix([])
        self.W = np.matrix([])
        self.minsignificant = parameters["minsignificant"]

    def add(self, x, xt):
        r = xt - x
        if self.added:
            self.V = np.concatenate((r-self.rref, self.V), 1)
            self.W = np.concatenate((xt-self.xtref, self.W), 1)
        self.rref = r
        self.xtref = np.array(xt)
        self.added = True

    def predict(self, r):
        # Remove columns resulting in small diagonal elements in R
        singular = True
        while singular and self.V.shape[1]:
            R = qr(self.V, mode='r')
            diag = np.diagonal(R)
            v = min(diag)
            if v < self.minsignificant:
                i = np.argmin(diag)
                self.V[:,i] = []
                self.W[:,i] = []
            else:
                singular = False
        Q, R = qr(self.V)
        # Calculate return value if sufficient data available
        if self.V.shape[1]:
            # Interface Quasi-Newton with approximation for the inverse of the Jacobian from a least-squares model
            c = solve_triangular(R, np.transpose(Q) * (-r))
            dx = self.W * c + r
        else:
            if self.added:
                dx = np.zeros_like(self.xtref)
            else:
                raise RuntimeError("No information to predict")
        return dx

    def initializestep(self):
        self.rref = np.array([])
        self.xtref = np.array([])
        self.V = np.matrix([])
        self.W = np.matrix([])

    def finalizestep(self):
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
