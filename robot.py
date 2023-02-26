import os
import random
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
		self.heightList = [1]
		self.robotId = p.loadURDF(f'body{solutionID}.urdf')
		self.nn = NEURAL_NETWORK(f'brain{solutionID}.nndf')

		for link in range(-1, 20):
			p.changeVisualShape(self.robotId, link, rgbaColor=[0, 0, 1, 1])

		pyrosim.Prepare_To_Simulate(self.robotId)
		self.Prepare_To_Sense()
		self.Prepare_To_Act()

		os.system(f'del brain{solutionID}.nndf')
		os.system(f'del body{solutionID}.urdf')

	def Prepare_To_Sense(self):
		self.sensors = {}

		neuron_keys = list(self.nn.Get_Neuron_Names())

		for linkName in pyrosim.linkNamesToIndices:
			linkNum = linkName[4:]
			if linkNum in neuron_keys and random.random() > 0.5:
				self.sensors[linkName] = SENSOR(linkName)
				p.changeVisualShape(self.robotId, int(linkNum), rgbaColor=[0, 1, 0, 1])

	def SENSE(self, t):
		for k, v in self.sensors.items():
			v.Get_Value(t)

	def Prepare_To_Act(self):
		self.motors = {}
		for jointName in pyrosim.jointNamesToIndices:
			self.motors[jointName] = MOTOR(jointName)
		# print(self.motors)

	def Act(self, t):
		for neuronName in self.nn.Get_Neuron_Names():
			if self.nn.Is_Motor_Neuron(neuronName):
				jointName = self.nn.Get_Motor_Neurons_Joint(neuronName)
				desiredAngle = self.nn.Get_Value_Of(neuronName) * c.motorJointRange
				## print(jointName)
				# bytes hack :(
				self.motors[bytes(jointName,'UTF-8')].Set_Value(self.robotId, desiredAngle)

	def Think(self):
		self.nn.Print()
		self.nn.Update()
		# self.Track_Height()

	def Track_Height(self):
		basePosition, baseOrientation = p.getBasePositionAndOrientation(self.robotId)
		zPosition = basePosition[2]
		if zPosition >= 0:
			self.heightList.append(zPosition)

	def Get_Fitness(self):
		basePosition, baseOrientation = p.getBasePositionAndOrientation(self.robotId)
		yPosition = basePosition[1]

		avgHeight = sum(self.heightList)/len(self.heightList)
		fitness = f'{yPosition-avgHeight}'
		with open(f'tmp{self.solutionID}.txt', 'w') as out_file:
			out_file.write(fitness)
		os.system(f'rename tmp{self.solutionID}.txt fitness{self.solutionID}.txt')

		with open(f'max_fitness.txt', 'w') as out_file:
			out_file.write(fitness)