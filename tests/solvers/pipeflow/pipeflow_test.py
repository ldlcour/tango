from solvers.pipeflow.pipeflow import PipeFlow
from matplotlib.pyplot import plot
import numpy as np
import math as m
import pytest

def test_getsetgrid():
    parameters = {
        'l':  0.05,
        'd':  0.005,
        'rhof': 1000.0,
        'ureference': 1.0,
        'uamplitude': 0.0,
        'uperiod': 1.0,
        'utype': 1,
        'e': 300000.0,
        'h': 0.001,
        'm': 100,
        'newtonmax': 10,
        'newtontol': 1e-6
    }  # Test case with constant inlet velocity

    pipeflow = PipeFlow(parameters)
    xi = pipeflow.getinputgrid()
    xo = pipeflow.getoutputgrid()
    pipeflow.setinputgrid(xi)
    pipeflow.setoutputgrid(xi)
    pass


# Test constant pressure if constant inlet velocity and area of cross section
def test_constantpressure():
    parameters = {
        'l':  0.05,
        'd':  0.005,
        'rhof': 1000.0,
        'ureference': 1.0,
        'uamplitude': 0.0,
        'uperiod': 1.0,
        'utype': 1,
        'e': 300000.0,
        'h': 0.001,
        'm': 100,
        'newtonmax': 10,
        'newtontol': 1e-6
    }  # Test case with constant inlet velocity
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    N = 10  # Number of time steps
    a = m.pi*parameters['d']**2/4.0*np.ones(parameters['m'])  # Undisturbed area of cross section
    cmk2 = (parameters['e'] * parameters['h']) / (parameters['rhof'] * parameters['d'])  # Wave speed squared

    pipeflow = PipeFlow(parameters)
    pipeflow.settimestep(dt)
    pipeflow.initialize()
    for n in range(1, N):
        pipeflow.initializestep()
        p = pipeflow.calculate(a)
        d = abs(p - 2.0 * cmk2)
        assert min(d) < tol
        pipeflow.finalizestep()
    pipeflow.finalize()

    plot(pipeflow.z, p)
