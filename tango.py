import sys
import os
import json
import importlib

# Obtain case name as first input argument or user input
if len(sys.argv) > 1:
    case = sys.argv[1]
else:
    case = input("case?")

# Create path to case and ensure it exists
path = os.path.join(os.getcwd(), case)
if os.path.isdir(path):
    print("Running case in "+path)
else:
    raise ValueError("No case in "+path)

# Read settings file
with open(os.path.join(path, "settings.txt")) as f:
    settings = json.load(f)

# Read classes and create instances
flowsolvermodule = importlib.import_module(settings["flowsolvermodule"])
flowsolverclass = getattr(flowsolvermodule, settings["flowsolverclass"])
flowsolver = flowsolverclass(path)
structuresolvermodule = importlib.import_module(settings["structuresolvermodule"])
structuresolverclass = getattr(structuresolvermodule, settings["structuresolverclass"])
structuresolver = structuresolverclass(path)
couplermodule = importlib.import_module(settings["couplermodule"])
couplerclass = getattr(couplermodule, settings["couplerclass"])
coupler = couplerclass(path)
extrapolatormodule = importlib.import_module(settings["extrapolatormodule"])
extrapolatorclass = getattr(extrapolatormodule, settings["extrapolatorclass"])
extrapolator = extrapolatorclass(path)
convergencemodule = importlib.import_module(settings["convergencemodule"])
convergenceclass = getattr(convergencemodule, settings["convergenceclass"])
convergence = convergenceclass(path)
objects = [flowsolver, structuresolver, coupler, extrapolator, convergence]

# Read settings
nstart = settings["nstart"]
nstop = settings["nstop"]
kstop = settings["kstop"]
dt = settings["dt"]

# Initialize solvers
flowsolver.settimestep(dt)
structuresolver.settimestep(dt)
flowsolver.initialize()
structuresolver.initialize()

# To do: mapping (layer around solver with same interface as solver)

# Initialize coupling
x = flowsolver.getinputdata()
r = x

# Time step loop
for n in range(nstart, nstop):
    for object in objects:
        object.initializestep()

    # Coupling iteration loop
    for k in range(0, kstop):
        if k == 0:
            x = extrapolator.predict()
        else:
            dx = coupler.predict(-r) + r
            x += dx
        y = flowsolver.calculate(x)
        xt = structuresolver.calculate(y)
        r = xt - x
        coupler.add(r, xt)

        convergence.add(r)
        if convergence.issatisfied():
            break

    for object in objects:
        object.finalizestep()

flowsolver.finalize()
structuresolver.finalize()
