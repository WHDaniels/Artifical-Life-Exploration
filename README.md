# cs397-ludobots

## For Assignment 5 (Hopper Creature)

### Background
This creature is constructed to be a creature that takes sutble hops to get as far as possible in the y direction.

The fitness function is multi-objective and minimizes
```
y-(z*2)^2
```
where *y* is the current y position of the creature and *z* is the average z position (height) of the creature over its life.

This maximizes the distance the creature travels in the y direction as well as a jumping behaviour.

### Running
Clone repository and, assuming the requisite enviroment with pybullet installed, run
```
python main.py random
```
for the creature with random behaviour and 
```
python main.py train
```
to train and display the evolved "hopper" creature.

### Brief Visualizations
Random:
https://youtu.be/sDqdE_9GzQ8

Evolved:
https://youtu.be/41ceLS-wUsE
