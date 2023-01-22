import numpy as np
import os
import random
import pyrosim.pyrosim as pyrosim

x, y, z = 0, 0, 0.5
length, width, height = 1, 1, 1

class SOLUTION:
	def __init__(self):
		self.weights = 2 * np.random.rand(3, 2) - 1

	def Evaluate(self, directOrGUI='DIRECT'):
		self.Create_World()
		self.Create_Body()
		self.Create_Brain()
		os.system(f"python simulate.py {str(directOrGUI)}")

		with open('fitness.txt', 'r') as in_file:
			self.fitness = float(in_file.readlines()[0])

	def Mutate(self):
		row, col = self.weights.shape
		self.weights[random.randint(0, row-1), random.randint(0, col-1)] = 2 * random.random() - 1

	def Create_World(self):
		pyrosim.Start_SDF("world.sdf")
		pyrosim.Send_Cube(name="Box", pos=[x-3, y+3, z], size=[length, width, height])
		pyrosim.End()

	def Create_Body(self):
		pyrosim.Start_URDF("body.urdf")
		pyrosim.Send_Cube(name="Torso", pos=[0, 0, 1.5], size=[length, width, height])
		pyrosim.Send_Joint( name = "Torso_BackLeg" , parent= "Torso" , child = "BackLeg", 
			type = "revolute", position = [-0.5, 0, 1])
		pyrosim.Send_Cube(name="BackLeg", pos=[-0.5, 0, -0.5], size=[length, width, height])
		pyrosim.Send_Joint( name = "Torso_FrontLeg" , parent= "Torso" , child = "FrontLeg", 
			type = "revolute", position = [0.5, 0, 1])
		pyrosim.Send_Cube(name="FrontLeg", pos=[0.5, 0, -0.5], size=[length, width, height])
		pyrosim.End()

	def Create_Brain(self):
		pyrosim.Start_NeuralNetwork("brain.nndf")
		pyrosim.Send_Sensor_Neuron(name = 0 , linkName = "Torso")
		pyrosim.Send_Sensor_Neuron(name = 1 , linkName = "BackLeg")
		pyrosim.Send_Sensor_Neuron(name = 2 , linkName = "FrontLeg")
		pyrosim.Send_Motor_Neuron( name = 3 , jointName = "Torso_BackLeg")
		pyrosim.Send_Motor_Neuron( name = 4 , jointName = "Torso_FrontLeg")

		for currentRow in range(3):
			for currentColumn in range(2):
				pyrosim.Send_Synapse( sourceNeuronName = currentRow,
									  targetNeuronName = 3 + currentColumn,
									  weight = self.weights[currentRow][currentColumn] )

		pyrosim.End()