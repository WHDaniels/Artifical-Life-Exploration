import pybullet as p
import time

physicsClient = p.connect(p.GUI)

for n in range(1000):
	p.stepSimulation()
	time.sleep(1/60)
	
	if n % 50 == 0:
		print(n)

p.disconnect()