from solvers.pipestructure.v1 import PipeStructure
import numpy as np
import math as m


# Test whether errors occur when getting and setting grid
def test_getsetgrid():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "e": 300000.0,
        "h": 0.001,
        "m": 100
    }  # Test case

    pipestructure = PipeStructure(parameters)
    xi = pipestructure.getinputgrid()
    assert len(xi) == parameters["m"]
    xo = pipestructure.getoutputgrid()
    assert len(xo) == parameters["m"]
    pipestructure.setinputgrid(xi)
    pass
    pipestructure.setoutputgrid(xi)
    pass


# Test whether constant area appears for constant pressure
def test_constantarea():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "e": 300000.0,
        "h": 0.001,
        "m": 100
    }  # Test case
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    n = 10  # Number of time steps
    p = np.zeros(parameters["m"])  # Zero load
    a0 = np.ones(parameters["m"]) * m.pi * parameters["d"] ** 2 / 4.0  # Undisturbed area of cross section

    pipestructure = PipeStructure(parameters)
    pipestructure.settimestep(dt)
    pipestructure.initialize()
    for i in range(1, n):
        pipestructure.initializestep()
        a = pipestructure.calculate(p)
        assert len(a) == parameters["m"]
        d = abs(a - a0)
        assert max(d) < tol
        pipestructure.finalizestep()
    pipestructure.finalize()


# Test whether repeating of pressure within same time step gives same area of cross section
def test_repeatarea():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "e": 300000.0,
        "h": 0.001,
        "m": 100
    }  # Test case
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    n = 10  # Number of time steps
    cmk2 = (parameters["e"] * parameters["h"]) / (parameters["rhof"] * parameters["d"])  # Wave speed squared
    p = np.ones(parameters["m"]) * 0.1 * cmk2
    q = p * 1.1

    pipestructure = PipeStructure(parameters)
    pipestructure.settimestep(dt)
    pipestructure.initialize()
    for i in range(1, n):
        pipestructure.initializestep()
        ap = pipestructure.calculate(p)
        aq = pipestructure.calculate(q)
        d = abs(ap - aq)
        assert min(d) > tol
        app = pipestructure.calculate(p)
        d = abs(ap - app)
        assert max(d) < tol
        appp = pipestructure.calculate(p)
        d = abs(ap - appp)
        assert max(d) < tol
        pipestructure.finalizestep()
    pipestructure.finalize()
