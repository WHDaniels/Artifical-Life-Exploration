import sys
from simulation import SIMULATION

directOrGUI, solutionID = sys.argv[1], sys.argv[2]

simulation = SIMULATION(directOrGUI, solutionID)
simulation.run()
simulation.Get_Fitness()
