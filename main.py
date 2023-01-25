import sys
from hillclimber import HILL_CLIMBER
from parallelHillClimber import PARALLEL_HILL_CLIMBER

if __name__ == '__main__':
	switch = sys.argv[1]

	if switch == 'random' or switch == 'train':
		phc = PARALLEL_HILL_CLIMBER(mode=switch)
		phc.Evolve()
		phc.Show_Best()
	else:
		print("\n\nPlease input either \'random\' for random behaviour or \'train\' for evolved behaviour.")

	