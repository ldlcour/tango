import sys
import os
import json
import shutil
import importlib
import numpy as np

# Obtain short case path as first input argument or user input
if len(sys.argv) > 1:
    casepath = sys.argv[1]
else:
    casepath = input("Case path? ")

# Create full case path to case and read settings file
casepath = os.path.join(os.getcwd(), casepath)
if os.path.isdir(casepath):
    print("Running case in " + casepath)
else:
    raise ValueError("No directory in " + casepath)
with open(os.path.join(casepath, "settings.txt")) as f:
    settings = json.load(f)

# Create data folder for results
casename = os.path.basename(casepath)
datapath = os.path.join("data/", casename)
if os.path.exists(datapath):
    remove = input("Remove data? [y/n] ")
    if remove == "y":
        shutil.rmtree(datapath, ignore_errors=True)
os.makedirs(datapath, exist_ok=True)


# Function to create instance from module and class name
def createinstance(name):
    objectmodule = importlib.import_module(settings[name + "module"])
    objectclass = getattr(objectmodule, settings[name + "class"])
    return objectclass(casepath, datapath)

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
r = np.zeros_like(x)
extrapolator.initialize(x)

# Time step loop
for n in range(nstart, nstop):
    # Initialize step for all components
    for component in components:
        component.initializestep()

    # Coupling iteration loop
    for k in range(1, kstop):
        if k == 1:
            x = extrapolator.predict()
        else:
            dx = coupler.predict(r)
            x += dx
        y = flowsolver.calculate(x)
        xt = structuresolver.calculate(y)
        r = xt - x
        coupler.add(x, xt)

        convergence.add(r)
        print(convergence.status())
        if convergence.issatisfied():
            break

    # Finalize step for all components
    extrapolator.add(x)
    for component in components:
        component.finalizestep()

# Finalize solvers
flowsolver.finalize()
structuresolver.finalize()

print("Ending case in " + casepath)
