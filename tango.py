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
def createinstance(name):
    objectmodule = importlib.import_module(settings[name+"module"])
    objectclass = getattr(objectmodule, settings[name+"class"])
    return objectclass(path)

flowsolver = createinstance("flowsolver")
structuresolver = createinstance("structuresolver")
coupler = createinstance("coupler")
extrapolator = createinstance("extrapolator")
convergence = createinstance("convergence")
components = [flowsolver, structuresolver, coupler, extrapolator, convergence]

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
    # Initialize step for all components
    for component in components:
        component.initializestep()

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

    # Finalize step for all components
    for component in components:
        component.finalizestep()

# Finalize solvers
flowsolver.finalize()
structuresolver.finalize()
