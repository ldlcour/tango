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

# Create classes
flowsolvermodule = importlib.import_module(settings["flowsolvermodule"])
flowsolverclass = getattr(flowsolvermodule, settings["flowsolverclass"])
structuresolvermodule = importlib.import_module(settings["structuresolvermodule"])
structuresolverclass = getattr(structuresolvermodule, settings["structuresolverclass"])
