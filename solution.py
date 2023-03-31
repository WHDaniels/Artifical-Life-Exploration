import numpy as np
import os
import random
import pyrosim.pyrosim as pyrosim
import time
import re
import copy


class SOLUTION:
    def __init__(self, myID, root=False):
        self.root = root
        self.myID = myID
        self.initialBodies = random.randint(3, 4)
        self.path = None
        self.grafted = False

        self.body_encoding = {}
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

    def Mutate(self, path=None):
        """
        Perform a mutation. Either cut an encoding and shed information,
        combine a sliced encoding and another child's sliced encoding,
        or merely randomly mutate network weights.
        :param path: Type of mutation to perform
        """
        self.path = path
        if path == 'slice':
            self.body_encoding = self.sliceEncoding()
        elif path:
            self.body_encoding = self.sliceEncoding()
            other_slice = self.path.sliceEncoding()
            self.body_encoding = self.combineSlices(other_slice)
        else:
            row, col = self.weights.shape
            self.weights[random.randint(0, row - 1), random.randint(0, col - 1)] = 2 * random.random() - 1
            while random.random() > 0.5:
                self.weights[random.randint(0, row - 1), random.randint(0, col - 1)] = 2 * random.random() - 1

    def Set_ID(self, ID):
        self.myID = ID

    def Create_World(self):
        pyrosim.Start_SDF(f"world{self.myID}.sdf")
        pyrosim.End()

    def Create_Body(self):

        if self.root:
            # Get a random body encoding that gives a blueprint to 'createBodyFromInitialEncode'
            encoding = self.getInitialEncoding()

            # Creates an initial parent URDF file from a primitive initial encoding
            self.createBodyFromInitialEncode(encoding)

            # Make an URDF file from that encoding
            self.makeFromEncoding()

        else:
            # Make an URDF file from the current encoding
            self.makeFromEncoding()

    def Create_Brain(self):
        pyrosim.Start_NeuralNetwork(f"brain{self.myID}.nndf")

        # Perform a slice (cut) operation on an encoding
        if self.path == 'slice':
            self.weights = self.weights[:len(self.links), :len(self.joints)]

        # Graft two encodings through a slice and mend operation
        elif self.path:
            # Get some arguments for weight indexing
            try:
                slice_n = int(re.findall(r'\d+', self.slice_name)[0])
                path_slice_n = int(re.findall(r'\d+', self.path.slice_name)[0])
            except TypeError:
                slice_n, path_slice_n = 1, 1

            # Carry over the weights from the links kept from both encodings
            self.temp_weights = self.weights[:slice_n, :slice_n - 1]
            other_weights = self.path.weights[:path_slice_n, :path_slice_n - 1]
            n, m = len(self.links), len(self.joints)
            self.weights = np.random.rand(n, m)
            self.weights[:slice_n, :slice_n - 1] = self.temp_weights

            try:
                self.weights[slice_n:slice_n + other_weights.shape[0],
                slice_n:slice_n + other_weights.shape[1]] = other_weights
            except ValueError:
                pass

        self.sendSynapses()

        pyrosim.End()

    def sendSynapses(self):
        for n, name in enumerate(self.links):
            pyrosim.Send_Sensor_Neuron(name=n, linkName=name)
        for n, name in enumerate(self.joints):
            pyrosim.Send_Motor_Neuron(name=n + len(self.links), jointName=name)

        for row in range(len(self.links)):
            for col in range(len(self.joints)):
                pyrosim.Send_Synapse(sourceNeuronName=row,
                                     targetNeuronName=col + len(self.links),
                                     weight=self.weights[row][col])

    def getInitialEncoding(self):
        # Send initial primitive ancestor encoding
        return [1 for _ in range(self.initialBodies)]

    def makeFromEncoding(self):
        """
        Take a dictionary encoding and create a URDF file from it.
        Assign random weights if this is a root encoding (first parent).
        """
        self.links = []
        self.joints = []

        pyrosim.Start_URDF(f"body{self.myID}.urdf")
        for k, v in self.body_encoding.items():
            if '_' in k:
                self.sendJoint(k, v['parent'], v['child'], v['pos'])
                self.joints.append(k)
            else:
                self.sendLink(k, v['pos'], v['size'], v['body'])
                self.links.append(k)
        pyrosim.End()

        if self.root:
            self.weights = 2 * np.random.rand(len(self.links), len(self.joints)) - 1

    def sliceEncoding(self):
        """
        Slice an encoding at a random main body along the encoding.
        :return: Edited encoding after slicing.
        """
        slice_at = random.randint(2, self.initialBodies - 1)
        slice_name = None
        curr = 0
        for k, v in self.body_encoding.items():
            if '_' not in k:
                if v['body']:
                    curr += 1
                    if curr == slice_at:
                        slice_name = k
        self.slice_name = slice_name
        return self.deleteNames(slice_name)

    def deleteNames(self, name):
        """
        Delete all links and joints that follow from the cut sliced link.
        :param name: The link name at which to cut the encoding.
        :return: The final edited encoding after deletion.
        """
        temp_encode = copy.deepcopy(self.body_encoding)
        delete_list = [name]
        while delete_list:
            temp_keys = list(temp_encode.keys())
            for key in temp_keys:
                if '_' in key:
                    parent, child = key.split("_")
                    if delete_list[0] == parent:
                        delete_list.append(child)
                        del temp_encode[key]
                    elif delete_list[0] == child:
                        del temp_encode[key]
                else:
                    if delete_list[0] == key:
                        del temp_encode[key]
            delete_list.pop(0)
        return temp_encode

    def combineSlices(self, other_slice):
        """
        Take two slices and combine them by main body links.
        :param other_slice: The other slice to combine with (the first is a class object).
        :return: The combined encoding.
        """

        last = int(re.findall(r'\d+', list(self.body_encoding.keys())[-1])[0]) + 1
        last_other = int(re.findall(r'\d+', list(other_slice.keys())[-1])[0]) + 1

        if last_other > last:
            temp_body_encode = self.body_encoding
            self.body_encoding = other_slice
            other_slice = temp_body_encode
            last = int(re.findall(r'\d+', list(self.body_encoding.keys())[-1])[0]) + 1
            self.swap = True

        temp_other_items = list(other_slice.items())
        for k, v in temp_other_items:
            if '_' not in k:
                # Change key
                end_num = int(re.findall(r'\d+', k)[0])
                new_key = f'link{str(end_num + last)}'

                # Update slice
                del other_slice[k]
                other_slice[new_key] = v
            else:
                # Change key
                end_nums = re.findall(r'\d+', k)
                end_nums = [str(int(x) + last) for x in end_nums]
                new_key = f'link{end_nums[0]}_link{end_nums[1]}'

                # Change value
                end_parent_num = int(re.findall(r'\d+', v['parent'])[0])
                end_child_num = int(re.findall(r'\d+', v['child'])[0])
                new_parent = f'link{str(end_parent_num + last)}'
                new_child = f'link{str(end_child_num + last)}'

                # Update slice
                del other_slice[k]
                other_slice[new_key] = {'parent': new_parent, 'child': new_child, 'pos': v['pos']}

        # Hook up last body in A to first body in B (B is absolute so need to account for this)
        x, y, z = 0, 0.2, 0.2
        bv = random.randint(1, 10)
        new_body_pos = [x, y / bv, z / bv]  # MAYBE BUG

        last_body_A = None
        first_body_B = None

        for k, v in reversed(self.body_encoding.items()):
            if '_' not in k and v['body']:
                last_body_A = k
                break

        for k, v in other_slice.items():
            if '_' not in k and v['body']:
                first_body_B = k
                break

        assert last_body_A is not None and first_body_B is not None
        bridge = {f'{last_body_A}_{first_body_B}': {'parent': f'{last_body_A}', 'child': f'{first_body_B}',
                                                    'pos': new_body_pos}}

        combined = {**self.body_encoding, **bridge, **other_slice}
        return combined

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
        # pyrosim.Send_Cube(name=, pos=, size=)
        self.sendLink(name=f'link{n}', pos=link_vertex, size=size)
        self.links.append(f'link{n}')
        return size, link_vertex

    def createBodyFromInitialEncode(self, encode_list):
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
                self.sendJoint(name=f"link{last_body}_link{next_link}", parent=f"link{last_body}",
                               child=f"link{next_link}", pos=[x / 2, y / bv, z / bv])
                # Switch to relative link position
                body_link_pos = [x / 2, 0, 0]
            # If after second encode item, relative joint positioning
            if n > 1:
                self.sendJoint(name=f"link{last_body}_link{next_link}", parent=f"link{last_body}",
                               child=f"link{next_link}", pos=[x, y / bv, z / bv])

            # Send body link
            self.sendLink(name=f'link{next_link}', pos=body_link_pos, size=body_link_size, body=True)
            self.links.append(f'link{next_link}')
            # Track the 'name' of the last body link
            last_body = next_link
            # Grow limbs recursively
            next_link = self.grow(next_link, next_link + 1, body_link_size, body_link_pos)

        # Our new numLinks is the number of links generated
        self.numLinks = next_link - 1
        # Initialize the fully-connected weight matrix based on the number of links
        self.weights = 2 * np.random.rand(self.numLinks, self.numLinks) - 1

        pyrosim.End()

    def sendJoint(self, name=None, parent=None, child=None, pos=None):
        pyrosim.Send_Joint(name=name, parent=parent, child=child, type="revolute", position=pos, jointAxis="1 1 1")
        self.body_encoding[name] = {'parent': parent, 'child': child, 'pos': pos}

    def sendLink(self, name=None, pos=None, size=None, body=False):
        pyrosim.Send_Cube(name=name, pos=pos, size=size)
        self.body_encoding[name] = {'pos': pos, 'size': size, 'body': body}

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
            # pyrosim.Send_Joint(name=, parent=, child=,
            #                    type="revolute", position=, jointAxis="1 1 1")
            self.sendJoint(name=f"link{parent}_link{child}", parent=f"link{parent}",
                           child=f"link{child}", pos=stem_pos)
            self.joints.append(f"link{parent}_link{child}")
            # Place link
            prev_size, prev_pos = self.positLink(child)
            return self.grow(parent + 1, child + 1, prev_size, prev_pos, chance - 0.2)
        return child
