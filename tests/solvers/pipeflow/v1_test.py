from solvers.pipeflow.v1 import PipeFlow
import numpy as np
import math as m


# Test whether errors occur when getting and setting grid
def test_getsetgrid():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "ureference": 1.0,
        "uamplitude": 0.0,
        "uperiod": 1.0,
        "utype": 1,
        "e": 300000.0,
        "h": 0.001,
        "m": 100,
        "newtonmax": 10,
        "newtontol": 1e-12
    }  # Test case with constant inlet velocity

    pipeflow = PipeFlow(parameters)
    xi = pipeflow.getinputgrid()
    assert len(xi) == parameters["m"]
    xo = pipeflow.getoutputgrid()
    assert len(xo) == parameters["m"]
    pipeflow.setinputgrid(xi)
    pass
    pipeflow.setoutputgrid(xi)
    pass


# Test whether constant pressure appears for constant inlet velocity and constant area of cross section
def test_constantpressure():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "ureference": 1.0,
        "uamplitude": 0.0,
        "uperiod": 1.0,
        "utype": 1,
        "e": 300000.0,
        "h": 0.001,
        "m": 100,
        "newtonmax": 10,
        "newtontol": 1e-12
    }  # Test case with constant inlet velocity
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    n = 10  # Number of time steps
    a = m.pi * parameters["d"] ** 2 / 4.0 * np.ones(parameters["m"])  # Undisturbed area of cross section

    pipeflow = PipeFlow(parameters)
    pipeflow.settimestep(dt)
    pipeflow.initialize()
    for i in range(1, n):
        pipeflow.initializestep()
        p = pipeflow.calculate(a)
        assert len(p) == parameters["m"]
        d = abs(p - 0.0)
        assert max(d) < tol
        pipeflow.finalizestep()
    pipeflow.finalize()


# Test whether repeating of area of cross section within same time step gives same pressure
def test_repeatpressure():
    parameters = {
        "l":  0.05,
        "d":  0.005,
        "rhof": 1000.0,
        "ureference": 1.0,
        "uamplitude": 0.0,
        "uperiod": 1.0,
        "utype": 1,
        "e": 300000.0,
        "h": 0.001,
        "m": 100,
        "newtonmax": 10,
        "newtontol": 1e-12
    }  # Test case with constant inlet velocity
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    n = 10  # Number of time steps
    a = m.pi*parameters["d"] ** 2 / 4.0 * np.ones(parameters["m"])  # Undisturbed area of cross section
    b = 1.1 * a  # Disturbed area of cross section

    pipeflow = PipeFlow(parameters)
    pipeflow.settimestep(dt)
    pipeflow.initialize()
    for i in range(1, n):
        pipeflow.initializestep()
        pa = pipeflow.calculate(a)
        pb = pipeflow.calculate(b)
        d = abs(pa - pb)
        assert min(d) > tol
        paa = pipeflow.calculate(a)
        d = abs(pa - paa)
        assert max(d) < tol
        paaa = pipeflow.calculate(a)
        d = abs(pa - paaa)
        assert max(d) < tol
        pipeflow.finalizestep()
    pipeflow.finalize()


# Test whether linear pressure appears for constant area of cross section and changing inlet velocity
def test_linearpressure():
    parameters = {
        "l": 0.05,
        "d": 0.005,
        "rhof": 1000.0,
        "ureference": 1.0,
        "uamplitude": 0.1,
        "uperiod": 1.0,
        "utype": 1,
        "e": 300000.0,
        "h": 0.001,
        "m": 100,
        "newtonmax": 10,
        "newtontol": 1e-12
    }  # Test case with increasing inlet velocity
    tol = 1e-12  # Test tolerance
    dt = 0.01  # Time step size
    n = 10  # Number of time steps
    a = m.pi * parameters["d"] ** 2 / 4.0 * np.ones(parameters["m"])  # Undisturbed area of cross section

    pipeflow = PipeFlow(parameters)
    pipeflow.settimestep(dt)
    pipeflow.initialize()
    for i in range(1, n):
        pipeflow.initializestep()
        p = pipeflow.calculate(a)
        s = abs(p[1:] - p[0:len(p)-1])
        assert min(s) > tol
        d = abs(max(s) - min(s))
        assert d < tol
        pipeflow.finalizestep()
    pipeflow.finalize()
