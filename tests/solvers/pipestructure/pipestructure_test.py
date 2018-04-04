from solvers.pipestructure.pipestructure import PipeStructure
import numpy as np
import math as m


# Test whether errors occur when getting and setting grid
def test_getsetgrid():
    parameters = {
        'l':  0.05,
        'd':  0.005,
        'rhof': 1000.0,
        'e': 300000.0,
        'h': 0.001,
        'm': 100,
    }  # Test case

    pipestructure = PipeStructure(parameters)
    xi = pipestructure.getinputgrid()
    assert len(xi) == parameters['m']
    xo = pipestructure.getoutputgrid()
    assert len(xo) == parameters['m']
    pipestructure.setinputgrid(xi)
    pass
    pipestructure.setoutputgrid(xi)
    pass