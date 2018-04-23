import numpy as np
from scipy.linalg import qr, solve_triangular
import os
import json
from itertools import count


class IQNILS:
    _ids = count(0)

    def __init__(self, casepath, datapath):
        self.id = next(self._ids)

        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "iqnils" + str(self.id) + "/settings.txt")) as f:
                parameters = json.load(f)

        self.datapath = os.path.join(datapath, "iqnils" + str(self.id))
        os.makedirs(self.datapath, exist_ok=True)

        self.added = False
        self.rref = np.array([])
        self.xtref = np.array([])
        self.v = np.matrix([])
        self.w = np.matrix([])
        self.minsignificant = parameters["minsignificant"]
        self.omega = parameters["omega"]

    def add(self, x, xt):
        r = xt - x
        if self.added:
            dr = r - self.rref
            dxt = xt-self.xtref
            dr = np.reshape(dr, (-1, 1))
            dxt = np.reshape(dxt, (-1, 1))
            if self.v.shape[1]:
                self.v = np.concatenate((dr, self.v), 1)
                self.w = np.concatenate((dxt, self.w), 1)
            else:
                self.v = np.matrix(dr)
                self.w = np.matrix(dxt)
        self.rref = r
        self.xtref = np.array(xt)
        self.added = True

    def predict(self, r):
        # Remove columns resulting in small diagonal elements in R
        singular = True
        while singular and self.v.shape[1]:
            rr = qr(self.v, mode='r')
            diag = np.diagonal(rr)
            m = min(diag)
            if abs(m) < self.minsignificant:
                i = np.argmin(diag)
                self.v = np.delete(self.v, i, 1)
                self.w = np.delete(self.w, i, 1)
                print("Removing columns " + str(i) + ": " + str(abs(m)) + " < minsignificant")
            else:
                singular = False
        # Calculate return value if sufficient data available
        if self.v.shape[1]:
            # Interface Quasi-Newton with approximation for the inverse of the Jacobian from a least-squares model
            qq, rr, *_ = qr(self.v, mode='economic')
            dr = np.reshape(-r, (-1, 1))
            b = qq.T @ dr
            c = solve_triangular(rr, b)
            dx = self.w @ c - dr
            dx = np.asarray(dx).reshape(-1)
        else:
            if self.added:
                dx = self.omega * r
            else:
                raise RuntimeError("No information to predict")
        return np.array(dx)

    def initializestep(self):
        self.rref = np.array([])
        self.xtref = np.array([])
        self.v = np.matrix([])
        self.w = np.matrix([])

    def finalizestep(self):
        if self.added:
            self.added = False
        else:
            raise RuntimeError("No information added during step")
