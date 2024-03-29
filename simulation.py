import constants as c

import pybullet as p
import pybullet_data
import pyrosim.pyrosim as pyrosim

from world import WORLD
from robot import ROBOT

import time

class SIMULATION:
	def __init__(self, directOrGUI, solutionID):
		self.directOrGUI = directOrGUI
		self.solutionID = solutionID

		if directOrGUI == 'DIRECT':
			self.physicsClient = p.connect(p.DIRECT)
		if directOrGUI == 'GUI':
			self.physicsClient = p.connect(p.GUI)
			p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)

		p.setAdditionalSearchPath(pybullet_data.getDataPath())
		p.setGravity(0, 0, -9.8)

		self.world = WORLD(solutionID)
		self.robot = ROBOT(solutionID)

	def run(self):
		for n in range(c.ticks):
			p.stepSimulation()
			self.robot.SENSE(n)
			self.robot.Think()
			self.robot.Act(n)

			if self.directOrGUI == 'GUI':
				time.sleep(1e-3)
			# if n % 50 == 0:
			# 	print(n)

	def Get_Fitness(self):
		self.robot.Get_Fitness()

	def __del__(self):
		p.disconnect()
