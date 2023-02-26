import numpy as np
from matplotlib import pyplot as plt
import pickle

fitnesses = []
for num in range(5):
    with open(f'best_fitnesses{num}.pkl', 'rb') as file:
        fitnesses.append([pickle.load(file), f'Gen {num+1}'])

colors = ['b', 'r', 'k', 'm', 'c']
for n, run in enumerate(fitnesses):
    data = [abs(x) for x in run[0]]
    plt.plot(data, label=run[1], color=colors[n], linewidth=3)

plt.legend()
plt.show()