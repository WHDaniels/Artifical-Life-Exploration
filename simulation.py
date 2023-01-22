import constants as c

import pybullet as p
import pybullet_data
import pyrosim.pyrosim as pyrosim

from world import WORLD
from robot import ROBOT

import time

class SIMULATION:
	def __init__(self, directOrGUI):
		self.directOrGUI = directOrGUI
		if directOrGUI == 'DIRECT':
			self.physicsClient = p.connect(p.DIRECT)
		if directOrGUI == 'GUI':
			self.physicsClient = p.connect(p.GUI)
		p.setAdditionalSearchPath(pybullet_data.getDataPath())
		p.setGravity(0, 0, -9.8)

		self.world = WORLD()
		self.robot = ROBOT()

	def run(self):
		for n in range(c.ticks):
			p.stepSimulation()
			self.robot.SENSE(n)
			self.robot.Think()
			self.robot.Act(n)

			if self.directOrGUI == 'GUI':
				time.sleep(1e-5)
			# if n % 50 == 0:
			# 	print(n)

	def Get_Fitness(self):
		self.robot.Get_Fitness()

	def __del__(self):
		p.disconnect()