import pybullet as p
import pybullet_data
import time
import pyrosim.pyrosim as pyrosim
import numpy as np
import random

b_amplitude = np.pi/2
b_frequency = 7
b_phaseOffset = np.pi

f_amplitude = np.pi
f_frequency = 2
f_phaseOffset = np.pi/4

# b_targetAngles = np.load("data/targetAngles.npy")
# f_targetAngles = np.load("data/targetAngles.npy")

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
planeId = p.loadURDF("plane.urdf")
robotId = p.loadURDF("body.urdf")
p.loadSDF("world.sdf")
pyrosim.Prepare_To_Simulate(robotId)

ticks = 1000
backLegSensorValues = np.zeros(ticks)
frontLegSensorValues = np.zeros(ticks)
# np.save("data/targetAngles.npy", np.sin(np.linspace(0, np.pi*2, ticks)*-np.pi/4))
# np.save("data/targetAngles.npy", 
	# np.sin(frequency*np.linspace(0, np.pi*2, ticks)+phaseOffset)*amplitude)

b_targetAngles = np.sin(b_frequency*np.linspace(0, np.pi*2, ticks)+b_phaseOffset)*b_amplitude
f_targetAngles = np.sin(f_frequency*np.linspace(0, np.pi*2, ticks)+f_phaseOffset)*f_amplitude

for n in range(ticks):
	p.stepSimulation()
	backLegSensorValues[n] = pyrosim.Get_Touch_Sensor_Value_For_Link("BackLeg")
	frontLegSensorValues[n] = pyrosim.Get_Touch_Sensor_Value_For_Link("FrontLeg")

	pyrosim.Set_Motor_For_Joint(
	bodyIndex = robotId,
	jointName = b'Torso_BackLeg',
	controlMode = p.POSITION_CONTROL,
	targetPosition = b_targetAngles[n],
	maxForce = 25
	)

	pyrosim.Set_Motor_For_Joint(
	bodyIndex = robotId,
	jointName = b'Torso_FrontLeg',
	controlMode = p.POSITION_CONTROL,
	targetPosition = f_targetAngles[n],
	maxForce = 25
	)

	time.sleep(1/60)
	
	if n % 50 == 0:
		print(n)

p.disconnect()

np.save("data/backLegSensorValues.npy", backLegSensorValues)
np.save("data/frontLegSensorValues.npy", frontLegSensorValues)