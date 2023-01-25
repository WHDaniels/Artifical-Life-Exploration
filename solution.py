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
		pyrosim.End()

	def Create_Body(self):
		pyrosim.Start_URDF(f"body{self.myID}.urdf")

		# Torso
		pyrosim.Send_Cube(name="Torso", pos=[0, 0, 1], size=[1, 2, 0.1])


		# Upper Legs
		# ---
		# Front Left Leg
		pyrosim.Send_Joint(name="Torso_FrontL", parent="Torso", child="FrontL",
							type="revolute", position=[-0.5, 1, 1], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="FrontL", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Front Right Leg
		pyrosim.Send_Joint(name="Torso_FrontR", parent="Torso", child="FrontR",
							type="revolute", position=[0.5, 1, 1], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="FrontR", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Back Left Leg
		pyrosim.Send_Joint(name="Torso_BackL", parent="Torso", child="BackL",
							type="revolute", position=[-0.5, -1, 1], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="BackL", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Back Right Leg
		pyrosim.Send_Joint(name="Torso_BackR", parent="Torso", child="BackR",
							type="revolute", position=[0.5, -1, 1], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="BackR", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])
		# ---

		# Lower Legs
		# ---
		# Front Lower Left Leg
		pyrosim.Send_Joint(name="FrontL_FrontLowerL", parent="FrontL", child="FrontLowerL",
							type="revolute", position=[0, 0, -0.5], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="FrontLowerL", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Front Lower Right Leg
		pyrosim.Send_Joint(name="FrontR_FrontLowerR", parent="FrontR", child="FrontLowerR",
							type="revolute", position=[0, 0, -0.5], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="FrontLowerR", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Back Lower Left Leg
		pyrosim.Send_Joint(name="BackL_BackLowerL", parent="BackL", child="BackLowerL",
							type="revolute", position=[0, 0, -0.5], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="BackLowerL", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])

		# Back Lower Right Leg
		pyrosim.Send_Joint(name="BackR_BackLowerR", parent="BackR", child="BackLowerR",
							type="revolute", position=[0, 0, -0.5], jointAxis="1 0 0")
		pyrosim.Send_Cube(name="BackLowerR", pos=[0, 0, -0.25], size=[0.1, 0.1, 0.5])
		# ---
		
		pyrosim.End()

	def Create_Brain(self):
		pyrosim.Start_NeuralNetwork(f"brain{self.myID}.nndf")

		pyrosim.Send_Sensor_Neuron(name = 0 , linkName = "FrontLowerL")
		pyrosim.Send_Sensor_Neuron(name = 1 , linkName = "FrontLowerR")
		pyrosim.Send_Sensor_Neuron(name = 2 , linkName = "BackLowerL")
		pyrosim.Send_Sensor_Neuron(name = 3 , linkName = "BackLowerR")

		pyrosim.Send_Motor_Neuron(name = 4 , jointName = "Torso_FrontL")
		pyrosim.Send_Motor_Neuron(name = 5 , jointName = "Torso_FrontR")
		pyrosim.Send_Motor_Neuron(name = 6 , jointName = "Torso_BackL")
		pyrosim.Send_Motor_Neuron(name = 7 , jointName = "Torso_BackR")

		pyrosim.Send_Motor_Neuron(name = 8 , jointName = "FrontL_FrontLowerL")
		pyrosim.Send_Motor_Neuron(name = 9 , jointName = "FrontR_FrontLowerR")
		pyrosim.Send_Motor_Neuron(name = 10 , jointName = "BackL_BackLowerL")
		pyrosim.Send_Motor_Neuron(name = 11 , jointName = "BackR_BackLowerR")


		for currentRow in range(c.numSensorNeurons):
			for currentColumn in range(c.numMotorNeurons):
				pyrosim.Send_Synapse( sourceNeuronName = currentRow,
									  targetNeuronName = c.numSensorNeurons + currentColumn,
									  weight = self.weights[currentRow][currentColumn] )

		pyrosim.End()