class RelativeNorm:
    def __init__(self, parameters):
        self.n = 0

    def add(self, x):
        x[1] = 0

    def issatisfied(self):
        return True

    def initializestep(self):
        self.n += 1

    def finalizestep(self):
        print(self.n)
