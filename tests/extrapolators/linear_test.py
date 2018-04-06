from extrapolators.linear import Linear
import numpy as np
import pytest


# Test whether initial value is returned in first step
def test_initial():
    tol = 1e-12
    m = 10
    x0 = np.ones(m)
    x1 = 2.0 * np.ones(m)

    extrapolator = Linear()
    extrapolator.initialize(x0)
    extrapolator.initializestep()

    xp = extrapolator.predict()
    d = abs(xp - x0)
    assert max(d) < tol

    xpp = extrapolator.predict()
    d = abs(xpp - x0)
    assert max(d) < tol

    extrapolator.add(x1)
    xppp = extrapolator.predict()
    d = abs(xppp - x0)
    assert max(d) < tol

    extrapolator.finalizestep()


# Test whether extrapolation is linear
def test_linear():
    tol = 1e-12
    m = 10
    x0 = np.ones(m)
    x1 = 2.0 * np.ones(m)
    x2 = 3.0 * np.ones(m)

    extrapolator = Linear()
    extrapolator.initialize(x0)
    extrapolator.initializestep()
    extrapolator.add(x1)
    extrapolator.finalizestep()
    extrapolator.initializestep()

    xp = extrapolator.predict()
    d = abs(xp - x2)
    assert max(d) < tol

    extrapolator.add(x2)
    xpp = extrapolator.predict()
    d = abs(xpp - x2)
    assert max(d) < tol

    extrapolator.finalizestep()


# Test whether adding information is enforced
def test_add():
    m = 10
    x0 = np.ones(m)

    extrapolator = Linear()
    extrapolator.initialize(x0)
    extrapolator.initializestep()
    with pytest.raises(RuntimeError):
        extrapolator.finalizestep()
