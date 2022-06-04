from email.errors import BoundaryError
import numpy as np
from math import dist
from matplotlib import pyplot as plt
from collections import OrderedDict, defaultdict


class MachineTemplate:
    def __init__(self, machine, machine_code, inandoutpos=None):
        self.rules = np.array([[]])
        self.occupy = machine
        self.layout = machine
        self.machine_code = machine_code
        if inandoutpos == None:
            self.In = self.out = [i // 2 for i in np.shape(machine)]
        else:
            self.In, self.out = inandoutpos
        # self.background = machine

    def Rules(self, Rules):
        self.rules.vstack(Rules)

    def background_sole(
        self, background
    ):  # without any other machine, only the machine is in the entire background
        self.background = background
        self.inandout()
        return background


class BackgroundTemplate:
    def __init__(self, bg, inandout=None):
        self.null_bg = bg
        self.bg = bg
        self.machine_dict = defaultdict(MachineTemplate)
        self.product_machines = {}
        if inandout == None:
            inandout = (
                [np.shape(bg)[0] // 2, 0],
                [np.shape(bg)[0] // 2, np.shape(bg)[1]],
            )
        self.In, self.out = inandout
        self.product_machines = {}

    def collide_check(self):
        if 2 in self.bg:
            return True
        return False

    def product_line(self, product_name, machine_line):
        for m in machine_line:
            assert m in self.machine_dict.keys()
        self.product_machines[product_name] = machine_line

    def product_distance_calculate(self, product_name):
        machines = self.product_machines[product_name]
        out = self.In
        distance = 0.0
        for code in machines:
            machine = self.machine_dict[code]
            distance += np.linalg.norm(out - machine.In)
            out = machine.out
        distance += np.linalg.norm(out - self.out)
        return distance
            

    def machine_add(self, machine):  # Adding dictionary of machine
        self.machine_dict[machine.machine_code] = machine

    def machine_distance_calculate(self, passage_path=None):
        self.machine_dict = OrderedDict(sorted(self.machine_dict.items()))
        num_of_machine = len(self.machine_dict)
        if not passage_path:
            passage_path = np.ones((num_of_machine, num_of_machine))
        self.machine_dist_mat = np.zeros((num_of_machine, num_of_machine))
        print("machine_dict", self.machine_dict)
        for y, start_code in enumerate(self.machine_dict):
            for x, end_code in enumerate(self.machine_dict):
                start_template = self.machine_dict[start_code]
                end_template = self.machine_dict[end_code]
                print(
                    "in: ",
                    y,
                    ", out: ",
                    x,
                    start_template.output_pos,
                    end_template.input_pos,
                    dist(start_template.output_pos, end_template.input_pos),
                )
                self.machine_dist_mat[y][x] = dist(
                    start_template.output_pos, end_template.input_pos
                )

        return self.machine_dist_mat

    def machine_batch(self, position, machine_code):
        try:
            one_machine_layout = self.null_bg
            one_machine_layout[
                position[0] : position[0]
                + self.machine_dict[machine_code].occupy.shape[0],
                position[1] : position[1]
                + self.machine_dict[machine_code].occupy.shape[1],
            ] += self.machine_dict[machine_code].occupy
            self.machine_dict[machine_code].In += position
            self.machine_dict[machine_code].out += position
            self.machine_dict[machine_code].background_sole(one_machine_layout)
            self.machine_dict[machine_code] = self.machine_dict[machine_code]
        except ValueError as e:
            print(e)
            raise BoundaryError(
                "Machine exceeds boundary, machine position is {} and machine size is {}".format(
                    position, self.machine_dict[machine_code].occupy.shape
                )
            )
        if self.collide_check():
            self.collision = 1
            print("collision")
        return self.bg

    def products_manufacturing_process_table(
        self, products_manufacturing_process_table
    ):
        self.products_manufacturing_process_table = products_manufacturing_process_table

    def bg2img(self):
        img = np.zeros((self.bg.shape[0], self.bg.shape[1], 3), dtype=np.uint8)
        img[self.bg == 0] = (255, 255, 255)
        img[self.bg == 1] = (0, 0, 0)
        img[self.bg == 2] = (255, 0, 0)
        img[self.bg == 3] = (0, 255, 0)
        img[self.bg == 5] = (0, 0, 255)

        img = plt.imshow(img)


# I think machine class is needed because substances in and out must be defined
# What kind of characteristics do machines have to have?
# In and Out of substance and size of machine and Rules
if __name__ == "__main__":
    for i in range(10):
        m1 = np.ones([20, 10])
        m1[0, i] = 3  # start position
        m1[i, 9] = 5
        m2 = np.ones([10, 20])
        m2[i, 0] = 3
        m2[0, i] = 5
        m3 = np.ones([30, 20])
        m3[i, 0] = 3
        m3[0, 5] = 5

        machine1 = MachineTemplate(m1, 1)
        machine2 = MachineTemplate(m2, 2)
        machine3 = MachineTemplate(m3, 3)

        # machine1.inandout([50,0],[50,100])
        Incheon_Airport = BackgroundTemplate(np.zeros([100, 100]))
        Incheon_Airport.machine_add(machine1)
        Incheon_Airport.machine_add(machine2)
        Incheon_Airport.machine_add(machine3)
        Incheon_Airport.machine_batch([30, 20], 1)
        Incheon_Airport.machine_batch([20, 5], 2)
        Incheon_Airport.machine_batch([50, 40], 3)
        # print(Incheon_Airport.machine_dict)
        print(Incheon_Airport.machine_distance_calculate())
        Incheon_Airport.bg2img()
        #
