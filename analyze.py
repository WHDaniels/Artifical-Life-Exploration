import numpy as np
from matplotlib import pyplot as plt

backLegSensorValues = np.load("data/backLegSensorValues.npy")
frontLegSensorValues = np.load("data/frontLegSensorValues.npy")
targetAngles = np.load("data/targetAngles.npy")

# plt.plot(backLegSensorValues, label='back leg', linewidth=3)
# plt.plot(frontLegSensorValues, label='front leg')
plt.plot(targetAngles)
# plt.legend()
plt.show()