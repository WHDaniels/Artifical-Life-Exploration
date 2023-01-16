import numpy as np
from matplotlib import pyplot as plt

backLegSensorValues = np.load("data/backLegSensorValues.npy")
frontLegSensorValues = np.load("data/frontLegSensorValues.npy")

plt.plot(backLegSensorValues, label='back leg', linewidth=3)
plt.plot(frontLegSensorValues, label='front leg')
plt.legend()
plt.show()