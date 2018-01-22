from solvers.pipeflow.pipeflow import PipeFlow
import numpy as np
import math as m

parameters = {
    'l':  0.05,
    'd':  0.005,
    'rhof': 1000.0,
    'ureference': 1.0,
    'uamplitude': 0.1,
    'uperiod': 1.0,
    'utype': 1,
    'e': 300000.0,
    'h': 0.001,
    'm': 100,
    'newtonmax': 10,
    'newtontol': 1e-6
}

dt = 0.01
a = m.pi*parameters['d']**2/4.0*np.ones(parameters['m'])

pipeflow = PipeFlow(parameters)
xi = pipeflow.getinputgrid()
xo = pipeflow.getoutputgrid()
pipeflow.setinputgrid(xi)
pipeflow.setoutputgrid(xi)
pipeflow.settimestep(dt)
pipeflow.initialize()
pipeflow.initializestep()
p = pipeflow.calculate(a)
pipeflow.finalizestep()
pipeflow.finalize()
