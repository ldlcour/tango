import os
import json
from itertools import count


class Linear:
    _ids = count(0)

    def __init__(self, casepath, datapath):
        self.id = next(self._ids)

        if type(casepath) is dict:
            parameters = casepath
        else:
            with open(os.path.join(casepath, "linear" + str(self.id) + "/settings.txt")) as f:
                parameters = json.load(f)

        self.datapath = os.path.join(datapath, "pipeflow" + str(self.id))
        os.makedirs(self.datapath, exist_ok=True)
        self.filepath = os.path.join(self.datapath, "output.dat")
        self.datafile = open(self.filepath, mode='w')