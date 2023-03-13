import sys
from hillclimber import HILL_CLIMBER
from parallelHillClimber import PARALLEL_HILL_CLIMBER
import numpy as np
import random

if __name__ == '__main__':
	switch = sys.argv[1]

	# np.random.seed(4)
	# random.seed(4)

	if switch == 'random' or switch == 'train' or switch == 'saved':
		phc = PARALLEL_HILL_CLIMBER(mode=switch)
		phc.Evolve()
		phc.Show_Best()
	else:
		print("\n\nPlease input either \'random\' for random behaviour or \'train\' for evolved behaviour.")

	