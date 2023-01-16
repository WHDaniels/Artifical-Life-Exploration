import pybullet as p
import pybullet_data
import time
import pyrosim.pyrosim as pyrosim
import numpy as np
import random

physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
planeId = p.loadURDF("plane.urdf")
robotId = p.loadURDF("body.urdf")
p.loadSDF("world.sdf")
pyrosim.Prepare_To_Simulate(robotId)

ticks = 500
backLegSensorValues = np.zeros(ticks)
frontLegSensorValues = np.zeros(ticks)

for n in range(ticks):
	p.stepSimulation()
	backLegSensorValues[n] = pyrosim.Get_Touch_Sensor_Value_For_Link("BackLeg")
	frontLegSensorValues[n] = pyrosim.Get_Touch_Sensor_Value_For_Link("FrontLeg")

	pyrosim.Set_Motor_For_Joint(
	bodyIndex = robotId,
	jointName = b'Torso_BackLeg',
	controlMode = p.POSITION_CONTROL,
	targetPosition = np.pi/(4*(random.random()-0.5)),
	maxForce = 25
	)

	pyrosim.Set_Motor_For_Joint(
	bodyIndex = robotId,
	jointName = b'Torso_FrontLeg',
	controlMode = p.POSITION_CONTROL,
	targetPosition = np.pi/(4*(random.random()-0.5)),
	maxForce = 25
	)
	print(4*(random.random()-0.5))

	time.sleep(1/60)
	
	if n % 50 == 0:
		print(n)

p.disconnect()

np.save("data/backLegSensorValues.npy", backLegSensorValues)
np.save("data/frontLegSensorValues.npy", frontLegSensorValues)