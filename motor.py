import numpy as np
import constants as c
import pybullet as p
import pyrosim.pyrosim as pyrosim

class MOTOR:
	def __init__(self, jointName):
		self.jointName = jointName
		self.Prepare_To_Act()

	def Prepare_To_Act(self):
		self.values = np.zeros(c.ticks)

		self.amplitude = c.amplitude
		self.frequency = c.frequency
		self.phaseOffset = c.phaseOffset

		if self.jointName == b'Torso_BackLeg':
			self.amplitude *= 2

		lin_arr = np.linspace(0, np.pi*2, c.ticks)
		self.motorValues = np.sin(self.frequency*lin_arr+self.phaseOffset)*self.amplitude

	def Set_Value(self, robotId, t):
		pyrosim.Set_Motor_For_Joint(
			bodyIndex = robotId,
			jointName = self.jointName,
			controlMode = p.POSITION_CONTROL,
			targetPosition = self.motorValues[t],
			maxForce = c.maxForce
		)

	def Save_Values(self):
		np.save('data/motorValues.npy', self.motorValues)