import numpy as np
import os
import random
import pyrosim.pyrosim as pyrosim
import time


class SOLUTION:
    def __init__(self, myID):
        self.maxLinks = 5
        self.baseLinks = random.randint(1, 3)
        self.myID = myID

        self.links = []
        self.joints = []

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
        self.weights[random.randint(0, row - 1), random.randint(0, col - 1)] = 2 * random.random() - 1

    def Set_ID(self, ID):
        self.myID = ID

    def Create_World(self):
        pyrosim.Start_SDF(f"world{self.myID}.sdf")
        pyrosim.End()

    def Create_Body(self):
        pyrosim.Start_URDF(f"body{self.myID}.urdf")

        # Get a random body encoding that gives a blueprint to 'createBodyFromEncode'
        encoding = self.getRandomEncoding()

        # Creates a unique URDF file from encoding
        self.createBodyFromEncode(encoding)

    def Create_Brain(self):
        pyrosim.Start_NeuralNetwork(f"brain{self.myID}.nndf")

        for n, name in enumerate(self.links):
            pyrosim.Send_Sensor_Neuron(name=n, linkName=name)
        for n, name in enumerate(self.joints):
            pyrosim.Send_Motor_Neuron(name=n + self.numLinks, jointName=name)

        for row in range(self.numLinks):
            for col in range(self.numLinks):
                pyrosim.Send_Synapse(sourceNeuronName=row,
                                     targetNeuronName=col + self.numLinks,
                                     weight=self.weights[row][col])

        pyrosim.End()

    def getRandomEncoding(self):
        # Create a mutable object to store the encoding
        encode_list = []

        """ We will soon define an input encoding to generate a creature,
        for now the encoding just specifies how many main body links exist.
        """
        n = 0
        while n < self.baseLinks:
            n += 1
            if random.random() > 0:
                encode_list.append(1)

        return encode_list

    def getStemPos(self, prev_size, prev_pos):
        """
        Gets the coordinate of the next joint (where the next link will stem) given
        the last link's size and position. The coordinate always resides on the
        surface of one of the link faces.
        :param prev_size: Size of the previous link.
        :param prev_pos:  Position of the previous link.
        :return: The position of the next joint.
        """
        pos_x, pos_y, pos_z = prev_pos
        size_x, size_y, size_z = prev_size

        # Get some random perturbations to add to the previous position
        new_x = random.uniform(-size_x / 2, size_x / 2)
        new_y = random.uniform(-size_y / 2, size_y / 2)
        new_z = random.uniform(-size_z / 2, size_z / 2)

        """ Randomly choose the axis parallel to the face where the joint will lie by 
        randomly choosing the axis perpendicular to it (e.g. rnd=0 -> x-axis -> y-plane). 
        Then randomly choose one of the two faces (for example, if we are considering 
        the y-plane there are two faces on that plane) where the joint will lie. Other
        coordinates are random within the constraints of the link.
        """

        rnd = random.randint(0, 2)
        if rnd == 0:
            if random.random() > 0.5:
                stem_pos = [pos_x + size_x / 2, pos_y + new_y, pos_z + new_z]
            else:
                stem_pos = [pos_x - size_x / 2, pos_y + new_y, pos_z + new_z]
        elif rnd == 1:
            if random.random() > 0.5:
                stem_pos = [pos_x + new_x, pos_y + size_y / 2, pos_z + new_z]
            else:
                stem_pos = [pos_x + new_x, pos_y - size_y / 2, pos_z + new_z]
        elif rnd == 2:
            if random.random() > 0.5:
                stem_pos = [pos_x + new_x, pos_y + new_y, pos_z + size_z / 2]
            else:
                stem_pos = [pos_x + new_x, pos_y + new_y, pos_z - size_z / 2]
        return stem_pos

    def positLink(self, n):
        """
        Create a link with a random size configuration and position it such
        that one of its vertices is place at the last stem joint location.
        :param n: The link number for this link.
        :return: The size of the link and the position of the selected vertex.
        """
        # Get a random size configuration
        if random.random() > 0.5:
            # A "short-short-long" configuration
            size = [random.uniform(0.02, 0.05), random.uniform(0.02, 0.05), random.uniform(0.5, 0.1)]
        else:
            # A "long-long-short" configuration
            size = [random.uniform(0.5, 0.1), random.uniform(0.5, 0.1), random.uniform(0.02, 0.05)]

        # Shuffle our config
        random.shuffle(size)

        # Get one of 8 vertices of the link to be created
        link_vertex = [random.choice([-size[0] / 2, size[0] / 2]),
                       random.choice([-size[1] / 2, size[1] / 2]),
                       random.choice([-size[2] / 2, size[2] / 2])]

        # Send link
        pyrosim.Send_Cube(name=f'link{n}', pos=link_vertex, size=size)
        self.links.append(f'link{n}')
        return size, link_vertex

    def createBodyFromEncode(self, encode_list):
        """
        Create a contiguous body based on the encoding.
        :param encode_list: Body blueprint information.
        """
        pyrosim.Start_URDF(f"body{self.myID}.urdf")

        # Define initial body parameters
        x, y, z = 0.2, 0.2, 0.2
        body_link_size = [x, y, z]
        body_link_pos = [0, 0, z]

        next_link = 0
        for n, l in enumerate(encode_list):
            # Random perturbation value for body link positions
            bv = random.randint(1, 10)

            # If the second joint item, use absolute position
            if n == 1:
                pyrosim.Send_Joint(name=f"link{last_body}_link{next_link}", parent=f"link{last_body}",
                                   child=f"link{next_link}", type="revolute", position=[x/2, y/bv, z/bv], jointAxis="1 1 1")
                # Switch to relative link position
                body_link_pos = [x/2, 0, 0]
            # If after second encode item, relative joint positioning
            if n > 1:
                pyrosim.Send_Joint(name=f"link{last_body}_link{next_link}", parent=f"link{last_body}",
                                   child=f"link{next_link}", type="revolute", position=[x, y/bv, z/bv], jointAxis="1 1 1")
            # Send body link
            pyrosim.Send_Cube(name=f'link{next_link}', pos=body_link_pos, size=body_link_size)
            self.links.append(f'link{next_link}')
            # Track the 'name' of the last body link
            last_body = next_link
            # Grow limbs recursively
            next_link = self.grow(next_link, next_link+1, body_link_size, body_link_pos)

        # Our new numLinks is the number of links generated
        self.numLinks = next_link - 1
        # Initialize the fully-connected weight matrix based on the number of links
        self.weights = 2 * np.random.rand(self.numLinks, self.numLinks) - 1

        pyrosim.End()

    def grow(self, parent, child, prev_link_size, prev_link_pos, chance=0.8):
        """
        Grow a limb at a specified joint (stem point).
        :param parent: Parent name
        :param child: Child name
        :param prev_link_size: Size of previous link (body or limb)
        :param prev_link_pos: Position of previous link (body or limb)
        :param chance: Chance for limb to grow
        :return: Last child name
        """
        # Only grow if parent is first body or less than chance
        if not bool(parent) or random.random() < chance:
            # Get joint (stem) position
            stem_pos = self.getStemPos(prev_link_size, prev_link_pos)
            # Send limb joint
            pyrosim.Send_Joint(name=f"link{parent}_link{child}", parent=f"link{parent}", child=f"link{child}",
                               type="revolute", position=stem_pos, jointAxis="1 1 1")
            self.joints.append(f"link{parent}_link{child}")
            # Place link
            prev_size, prev_pos = self.positLink(child)
            return self.grow(parent+1, child+1, prev_size, prev_pos, chance-0.2)
        return child
