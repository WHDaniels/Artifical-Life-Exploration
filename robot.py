import os
import pybullet as p
import pyrosim.pyrosim as pyrosim
from pyrosim.neuralNetwork import NEURAL_NETWORK
import constants as c

from sensor import SENSOR
from motor import MOTOR

class ROBOT:
	def __init__(self, solutionID):
		self.solutionID = solutionID
		self.motors = {}
		self.robotId = p.loadURDF(f'body{solutionID}.urdf')
		self.nn = NEURAL_NETWORK(f'brain{solutionID}.nndf')
		pyrosim.Prepare_To_Simulate(self.robotId)
		self.Prepare_To_Sense()
		self.Prepare_To_Act()
		os.system(f'del brain{solutionID}.nndf')
		os.system(f'del body{solutionID}.urdf')

	def Prepare_To_Sense(self):
		self.sensors = {}
		for linkName in pyrosim.linkNamesToIndices:
			self.sensors[linkName] = SENSOR(linkName)

	def SENSE(self, t):
		for k, v in self.sensors.items():
			v.Get_Value(t)

	def Prepare_To_Act(self):
		self.motors = {}
		for jointName in pyrosim.jointNamesToIndices:
			self.motors[jointName] = MOTOR(jointName)

	def Act(self, t):
		for neuronName in self.nn.Get_Neuron_Names():
			if self.nn.Is_Motor_Neuron(neuronName):
				jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
				desiredAngle = self.nn.Get_Value_Of(neuronName) * c.motorJointRange
				# bytes hack :(
				self.motors[bytes(jointName,'UTF-8')].Set_Value(self.robotId, desiredAngle)

	def Think(self):
		self.nn.Print()
		self.nn.Update()

	def Get_Fitness(self):
		basePositionAndOrientation = p.getBasePositionAndOrientation(self.robotId)
		basePosition = basePositionAndOrientation[0]
		xPosition = basePosition[0]

		with open(f'tmp{self.solutionID}.txt', 'w') as out_file:
			out_file.write(str(xPosition))
		os.system(f'rename tmp{self.solutionID}.txt fitness{self.solutionID}.txt')