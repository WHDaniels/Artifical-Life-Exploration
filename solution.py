import numpy as np
import os
import random
import pyrosim.pyrosim as pyrosim
import time
import constants as c

x, y, z = 0, 0, 0.5
length, width, height = 1, 1, 1

class SOLUTION:
	def __init__(self, myID):
		self.weights = 2 * np.random.rand(c.numSensorNeurons, c.numMotorNeurons) - 1
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
		# pyrosim.Send_Cube(name="Box", pos=[x-3, y+3, z], size=[length, width, height])
		pyrosim.End()

	def Create_Body(self):
		pyrosim.Start_URDF(f"body{self.myID}.urdf")

		# Torso
		pyrosim.Send_Cube(name="Torso", pos=[0, 0, 1], size=[length, width, height])

		# Back Leg
		pyrosim.Send_Joint( name = "Torso_BackLeg" , parent= "Torso" , child = "BackLeg", 
			type = "revolute", position = [0, -0.5, 1], jointAxis = "1 0 0")
		pyrosim.Send_Cube(name="BackLeg", pos=[0, -0.5, 0], size=[0.2, 1, 0.2])

		# Front Leg
		pyrosim.Send_Joint( name = "Torso_FrontLeg" , parent= "Torso" , child = "FrontLeg", 
			type = "revolute", position = [0, 0.5, 1], jointAxis = "1 0 0")
		pyrosim.Send_Cube(name="FrontLeg", pos=[0, 0.5, 0], size=[0.2, 1, 0.2])

		# Left Leg
		pyrosim.Send_Joint( name = "Torso_LeftLeg" , parent= "Torso" , child = "LeftLeg", 
			type = "revolute", position = [0.5, 0, 1], jointAxis = "0 1 0")
		pyrosim.Send_Cube(name="LeftLeg", pos=[0.5, 0, 0], size=[1, 0.2, 0.2])

		# Right Leg
		pyrosim.Send_Joint( name = "Torso_RightLeg" , parent= "Torso" , child = "RightLeg", 
			type = "revolute", position = [-0.5, 0, 1], jointAxis = "0 1 0")
		pyrosim.Send_Cube(name="RightLeg", pos=[-0.5, 0, 0], size=[1, 0.2, 0.2])

		# Lower Back Leg
		pyrosim.Send_Joint(name="BackLeg_LowerBackLeg", parent="BackLeg", child="LowerBackLeg", 
			type="revolute", position=[0, -1, 0], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="LowerBackLeg", pos=[0, 0, -0.5], size=[0.2, 0.2, 1])

		# Lower Front Leg
		pyrosim.Send_Joint(name="FrontLeg_LowerFrontLeg", parent="FrontLeg", child="LowerFrontLeg", 
			type="revolute", position=[0, 1, 0], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="LowerFrontLeg", pos=[0, 0, -0.5], size=[0.2, 0.2, 1])

		# Lower Left Leg
		pyrosim.Send_Joint(name="LeftLeg_LowerLeftLeg", parent="LeftLeg", child="LowerLeftLeg", 
			type="revolute", position=[1, 0, 0], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="LowerLeftLeg", pos=[0, 0, -0.5], size=[0.2, 0.2, 1])

		# Lower Right Leg
		pyrosim.Send_Joint(name="RightLeg_LowerRightLeg", parent="RightLeg", child="LowerRightLeg", 
			type="revolute", position=[-1, 0, 0], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="LowerRightLeg", pos=[0, 0, -0.5], size=[0.2, 0.2, 1])

		pyrosim.End()

	def Create_Brain(self):
		pyrosim.Start_NeuralNetwork(f"brain{self.myID}.nndf")

		pyrosim.Send_Sensor_Neuron(name = 0 , linkName = "LowerBackLeg")
		pyrosim.Send_Sensor_Neuron(name = 1 , linkName = "LowerFrontLeg")
		pyrosim.Send_Sensor_Neuron(name = 2 , linkName = "LowerLeftLeg")
		pyrosim.Send_Sensor_Neuron(name = 3 , linkName = "LowerRightLeg")

		pyrosim.Send_Motor_Neuron(name = 4 , jointName = "Torso_BackLeg")
		pyrosim.Send_Motor_Neuron(name = 5 , jointName = "Torso_FrontLeg")
		pyrosim.Send_Motor_Neuron(name = 6 , jointName = "Torso_LeftLeg")
		pyrosim.Send_Motor_Neuron(name = 7 , jointName = "Torso_RightLeg")
		pyrosim.Send_Motor_Neuron(name = 8 , jointName = "BackLeg_LowerBackLeg")
		pyrosim.Send_Motor_Neuron(name = 9 , jointName = "FrontLeg_LowerFrontLeg")
		pyrosim.Send_Motor_Neuron(name = 10 , jointName = "LeftLeg_LowerLeftLeg")
		pyrosim.Send_Motor_Neuron(name = 11 , jointName = "RightLeg_LowerRightLeg")


		for currentRow in range(c.numSensorNeurons):
			for currentColumn in range(c.numMotorNeurons):
				pyrosim.Send_Synapse( sourceNeuronName = currentRow,
									  targetNeuronName = c.numSensorNeurons + currentColumn,
									  weight = self.weights[currentRow][currentColumn] )

		pyrosim.End()