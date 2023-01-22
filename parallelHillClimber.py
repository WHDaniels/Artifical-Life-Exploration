from solution import SOLUTION
import constants as c
import copy
import os

class PARALLEL_HILL_CLIMBER:
	def __init__(self):
		os.system('del brain*.nndf')
		os.system('del fitness*.nndf')

		self.nextAvailableID = 0
		self.parents = {}

		for parent_key in range(c.populationSize):
			self.parents[parent_key] = SOLUTION(self.nextAvailableID)
			self.nextAvailableID += 1

	def Evolve(self):
		self.Evaluate(self.parents)
		for currentGeneration in range(c.numberOfGenerations):
			self.Evolve_For_One_Generation()

	def Evolve_For_One_Generation(self):
		self.Spawn()
		self.Mutate()
		self.Evaluate(self.children)
		self.Print()
		self.Select()

	def Spawn(self):
		self.children = {}
		for k in self.parents:
			self.children[k] = copy.deepcopy(self.parents[k])
			self.children[k].Set_ID(self.nextAvailableID)
			self.nextAvailableID += 1

	def Mutate(self):
		for k in self.children:
			self.children[k].Mutate()

	def Evaluate(self, solutions):
		for k in solutions:
			solutions[k].Start_Simulation('DIRECT')
		for k in solutions:
			solutions[k].Wait_For_Simulation_To_End()

	def Select(self):
		for k in self.parents:
			if self.parents[k].fitness > self.children[k].fitness:
				self.parents[k] = self.children[k]

	def Print(self):
		for k in self.parents:
			print(f'\nParent fitness: {self.parents[k].fitness}, \
				Children fitness: {self.children[k].fitness}\n')

	def Show_Best(self):
		parent_fitnesses = [] 
		for k in self.parents:
			parent_fitnesses.append(self.parents[k].fitness)
		best_key = parent_fitnesses.index(min(parent_fitnesses))

		self.parents[best_key].Start_Simulation('GUI')