import numpy as np
import os
import random
import pyrosim.pyrosim as pyrosim
import pybullet as p
import time
import constants as c

x, y, z = 0, 0, 0.5
length, width, height = 1, 1, 1

class SOLUTION:
	def __init__(self, myID):
		self.numLinks = random.randint(3, 15)
		print('numLinks', self.numLinks)
		self.weights = 2 * np.random.rand(self.numLinks, self.numLinks) - 1
		self.myID = myID

	def Start_Simulation(self, directOrGUI):
		self.Create_World()
		self.Create_Body()
		self.Create_Brain()
		os.system(f"start /B python simulate.py {directOrGUI} {self.myID}")

	def Wait_For_Simulation_To_End(self):
		fit_path = f'fitness{self.myID}.txt'
		while not os.path.exists(fit_path):
			time.sleep(0.01)
		time.sleep(0.01)
		with open(fit_path, 'r') as in_file:
			self.fitness = float(in_file.readlines()[0])
		os.system(f'del {fit_path}')

	def Mutate(self):
		row, col = self.weights.shape
		self.weights[random.randint(0, row-1), random.randint(0, col-1)] = 2 * random.random() - 1

	def Set_ID(self, ID):
		self.myID = ID

	def Create_World(self):
		pyrosim.Start_SDF(f"world{self.myID}.sdf")
		pyrosim.End()

	def Create_Body(self):
		pyrosim.Start_URDF(f"body{self.myID}.urdf")

		for linkNo in range(self.numLinks):
			current = linkNo+1

			if linkNo == 0:
				startSize, sizeList = getRandomSizeList(), getRandomSizeList()
				pyrosim.Send_Cube(name=f'link{linkNo}', pos=[0, 0, 0], size=startSize)
				pyrosim.Send_Joint(name=f"link{linkNo}_link{current}", parent=f"link{linkNo}", child=f"link{current}",
								type="revolute", position=getPosFromSize(startSize), jointAxis="1 0 0")
				pyrosim.Send_Cube(name=f"link{current}", pos=getPosFromSize(sizeList), size=sizeList)

			else:
				pyrosim.Send_Joint(name=f"link{linkNo}_link{current}", parent=f"link{linkNo}", child=f"link{current}",
								type="revolute", position=getPosFromSize(sizeList), jointAxis="1 0 0")
				sizeList = getRandomSizeList()
				pyrosim.Send_Cube(name=f"link{current}", pos=getPosFromSize(sizeList), size=sizeList)

		pyrosim.End()

	def Create_Brain(self):
		pyrosim.Start_NeuralNetwork(f"brain{self.myID}.nndf")

		for n in range(self.numLinks):
			pyrosim.Send_Sensor_Neuron(name = n, linkName = f'link{n}')
			pyrosim.Send_Motor_Neuron(name = n+self.numLinks, jointName = f'link{n}_link{n+1}')

		for row in range(self.numLinks):
			for col in range(self.numLinks):
				pyrosim.Send_Synapse( sourceNeuronName = row,
								  		targetNeuronName = row+self.numLinks,
								  		weight = self.weights[row][col] )

		

		pyrosim.End()

def getRandomSizeList():
	a = random.randint(25, 50) * 0.01 * random.random()
	b = random.randint(60, 95) * 0.01 * random.random()
	c = random.randint(25, 50) * 0.01 * random.random()
	return [a, b, c]

def getPosFromSize(sizeList):
	a = (sizeList[0] / 2)
	b = (sizeList[1] / 2)
	c = (sizeList[2] / 2)
	return [a, b, c]