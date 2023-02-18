# cs397-ludobots

## Assignment 7

### Genotype graph
![Genotype graph](./figures/diagram1.png)

All creature brains are fully connected. So technically any sensor can activate any motor in a given creature.

### Codebase Description
Creature morphology is handled within the [solution.py](solution.py) file. Notably, [createBodyFromEncode()](solution.py#L153) takes an encoding (a placeholder that sends the number of main body or "base" links for the time being) from [getRandomEncoding()](solution.py#L68) to build a creature. Interesting helper functions include [getStemPos()](solution.py#L83), which creates joint positions from where limbs grow, [positLink()](solution.py#L125), which places limbs such that one of their vertices stems from the limb joint (or "stem_pos"), and [grow()](solution.py#L195), which recursively grows limbs with a diminishing chance (starts at 80%, -20% for each limb grown).

For more details, all linked code is substantially documented.

### What's the rundown?
Most creatures appear as a link of 1 to 3 sizeable main body links with limb random protrusions. These limbs stem from a main body and only grow sequentially on top of each other, stemming from random locations. Limbs can be of two configurations: a short-short-long and a long-long-short config. This results in 1) stick-like and 2) wing/flapper-like limbs. The main parameters that affect diversity are the "baseLinks" solution attribute (number of main bodies) and the grow chance (chance that limbs will grow recursively).

### Brief Visualization
https://youtu.be/jhMVZn2n3mA

### References

[Evolving Virtual Creatures](https://www.karlsims.com/papers/siggraph94.pdf) is referenced for genotype graph inspiration.

(No other references or outside information are used.)

## Assignment 6

### Running
Clone repository and, assuming the requisite enviroment with pybullet installed, run
```
python main.py random
```
for different variations of kinematic chains (jointed snakes) with random behaviour.

### Brief Visualization

https://youtu.be/ggGimPSdQyE
