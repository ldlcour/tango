import numpy as np
import json
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as ani


with open("pipeflow0/settings.txt") as f:
    parameters = json.load(f)
l = parameters["l"]
m = parameters["m"]

data = np.loadtxt("../../data/pipeflow0/output.dat")
dataa = data[0::3, :]

fig = plt.figure()
amax = 1.1 * max(max(dataa.tolist()))
axes = plt.axes(xlim=(0, l), ylim=(0, amax))
line, = axes.plot([], [], linewidth=2)


def init():
    line.set_data([], [])
    return line,


def animate(i):
    z = np.linspace(0, l, m + 2)
    a = dataa[i, :]
    line.set_data(z, a)
    return line,

anim = ani.FuncAnimation(fig, animate, init_func=init, frames=len(dataa), repeat=False)

plt.show()
