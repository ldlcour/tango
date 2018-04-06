from convergence.relativenorm import RelativeNorm
import numpy as np
import pytest


def test_convergence():
    parameters = {
        "kmin": 2,
        "mintol": 1e-12,
        "reltol": 1e-2
    }  # Test case
    m = 10
    r0 = np.ones(m)
    r1 = 1e-3 * np.ones(m)
    r2 = 1e-1 * np.ones(m)
    r3 = 1e-4 * np.ones(m)

    convergence = RelativeNorm(parameters)
    convergence.initializestep()
    assert not convergence.issatisfied()
    convergence.add(r0)
    assert not convergence.issatisfied()
    convergence.add(r1)
    assert convergence.issatisfied()
    convergence.add(r2)
    assert not convergence.issatisfied()
    convergence.add(r3)
    assert convergence.issatisfied()
    convergence.finalizestep()

def test_add():
    parameters = {
        "kmin": 2,
        "mintol": 1e-12,
        "reltol": 1e-2
    }  # Test case
    m = 10
    r0 = np.ones(m)

    convergence = RelativeNorm(parameters)
    convergence.initializestep()
    with pytest.raises(RuntimeError):
        convergence.finalizestep()
