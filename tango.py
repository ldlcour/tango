import sys
import os
import json
import importlib

# Obtain short case path as first input argument or user input
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = input("case path?")

# Create full case path to case and read settings file
path = os.path.join(os.getcwd(), path)
if os.path.isdir(path):
    print("Running case in " + path)
else:
    raise ValueError("No directory in " + path)
with open(os.path.join(path, "settings.txt")) as f:
    settings = json.load(f)


# Function to create instance from module and class name
def createinstance(name):
    objectmodule = importlib.import_module(settings[name + "module"])
    objectclass = getattr(objectmodule, settings[name + "class"])
    return objectclass(path)

# Create instances
flowsolver = createinstance("flowsolver")
structuresolver = createinstance("structuresolver")
coupler = createinstance("coupler")
extrapolator = createinstance("extrapolator")
convergence = createinstance("convergence")
components = [flowsolver, structuresolver, coupler, extrapolator, convergence]

# Read coupling settings
nstart = settings["nstart"]  # First time step (with time step 0 the initial condition)
nstop = settings["nstop"]  # Final time step
kstop = settings["kstop"]  # Maximal number of coupling iterations
dt = settings["dt"]  # Time step size

# Set time step and initialize solvers
flowsolver.settimestep(dt)
structuresolver.settimestep(dt)
flowsolver.initialize()
structuresolver.initialize()

# To do: mapping (layer around solver with same interface as solver)

# Initialize coupling
x = flowsolver.getinputdata()

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
            dx = coupler.predict(r)
            x += dx
        y = flowsolver.calculate(x)
        xt = structuresolver.calculate(y)
        r = xt - x
        coupler.add(x, xt)

        convergence.add(r)
        if convergence.issatisfied():
            break

    # Finalize step for all components
    for component in components:
        component.finalizestep()

# Finalize solvers
flowsolver.finalize()
structuresolver.finalize()
