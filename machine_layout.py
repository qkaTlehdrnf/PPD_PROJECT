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
        self.code = machine_code
        if inandoutpos == None:
            self.In = [i // 2 for i in np.shape(machine)]
            self.out = [
                i // 2 for i in np.shape(machine)
            ]  # if you make a = b = lsit type, then you cannot change in and out position by itself
        else:
            self.In, self.out = inandoutpos
        # self.background = machine

    def Rules(self, Rules):
        self.rules.vstack(Rules)

    def background_sole(
        self, background
    ):  # without any other machine, only the machine is in the entire background
        self.background = background
        return background


class BackgroundTemplate:
    def __init__(self, bg, inandout=None):
        self.null_bg = bg.copy()  # this is just blanck background
        self.bg = bg  # background of the factory, it is a 2D array
        self.machine_dict = defaultdict(
            MachineTemplate
        )  # machine code to machine template
        self.product_machines = {}  # machine line used for each product
        self.machine_inandout = {}  # machine code to in and out position
        self.sole_bg = defaultdict(
            lambda: np.zeros(self.bg.shape)
        )  # machine code to machine template
        self.collision = False
        if inandout == None:
            inandout = (
                [np.shape(bg)[0] // 2, 0],
                [np.shape(bg)[0] // 2, np.shape(bg)[1]],
            )
        self.In, self.out = inandout

    def reset_bg(self):
        self.bg = self.null_bg.copy()
        for machine_code in self.machine_dict:
            self.sole_bg[machine_code] = self.null_bg.copy()
        self.collision = False

    def collide_check(self):
        if 2 in self.bg:
            self.collision = True

    def product_line(self, product_name, machine_line:list):
        for m in machine_line:
            assert m in self.machine_dict.keys()
        self.product_machines[product_name] = machine_line

    def product_distance_calculate(self, product_name):
        machines = self.product_machines[product_name]
        out = self.In
        distance = 0.0
        for machine_code in machines:
            machine = self.machine_dict[machine_code]
            distance += dist(out, self.machine_inandout[machine_code][0])
            out = self.machine_inandout[machine_code][1]
        distance += dist(out, self.out)
        return distance

    def machine_add(self, machine):  # Adding dictionary of machine
        self.machine_dict[machine.code] = machine

    def machine_batch(self, position, machine_code):
        try:
            machine = self.machine_dict[machine_code]
            self.sole_bg[machine_code] = self.null_bg.copy()
            self.sole_bg[machine_code][
                position[0] : position[0] + machine.occupy.shape[0],
                position[1] : position[1] + machine.occupy.shape[1],
            ] = machine.occupy
            self.bg = np.add(self.bg, self.sole_bg[machine_code])
            self.machine_inandout[machine_code] = [
                [sum(x) for x in zip(machine.In, position)],
                [sum(x) for x in zip(machine.out, position)],
            ]
        except ValueError as e:
            msg = "Machine exceeds boundary, machine position is {} and machine size is {}".format(
                position, machine.occupy.shape
            )
            raise BoundaryError(msg)
        self.collide_check()

    def product_line_img(self, product):
        machine_line = self.product_machines[product]
        img = self.null_bg.copy()
        out = self.In
        for machine_code in machine_line:
            machine = self.machine_dict[machine_code]
            In = self.machine_inandout[machine_code][0]
            img = np.add(img, self.sole_bg[machine_code])
            plt.plot([In[1], out[1]], [In[0], out[0]], color="red", marker="o")
            out = self.machine_inandout[machine_code][1]
        In = self.out
        plt.plot([In[1], out[1]], [In[0], out[0]], color="green", marker="o")
        product_line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        product_line_img[img == 0] = (255, 255, 255)
        product_line_img[img == 1] = (0, 0, 0)
        product_line_img[img >= 2] = (0, 255, 0)
        plt.imshow(product_line_img)
        plt.show()

    def bg2img(self):
        img = np.zeros((self.bg.shape[0], self.bg.shape[1], 3), dtype=np.uint8)
        img[self.bg == 0] = (255, 255, 255)
        img[self.bg == 1] = (0, 0, 0)
        img[self.bg == 2] = (255, 0, 0)
        img[self.bg == 3] = (0, 255, 0)
        img[self.bg == 5] = (0, 0, 255)
        img = plt.imshow(img)
    
    def calculate_collision(self):
        collide_part = np.add(self.bg, -np.ones(self.bg.shape))
        collide_part[collide_part<0] = 0
        return np.sum(collide_part)
    
    def loss(self, collide_mul = 8):
        loss = 0
        for product in self.product_machines:
            loss += self.product_distance_calculate(product)
        loss += collide_mul * self.calculate_collision()
        return loss


class BoundaryError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# I think machine class is needed because substances in and out must be defined
# What kind of characteristics do machines have to have?
# In and Out of substance and size of machine and Rules
if __name__ == "__main__":
    for i in range(2):
        m1 = np.ones([20 + i, 10])
        m2 = np.ones([10 + 4 * i, 20 - i])
        m3 = np.ones([30 + i, 20 + i])
        m4 = np.ones([10, 30 + i])

        machine1 = MachineTemplate(m1, "m1", inandoutpos=[[10, 0], [20, 10]])
        machine2 = MachineTemplate(m2, "m2", inandoutpos=[[10, 0], [0, 15]])
        machine3 = MachineTemplate(m3, "m3", inandoutpos=[[20, 0], [20, 20]])
        machine4 = MachineTemplate(m4, "m4", inandoutpos=[[0, 20], [10, 30]])

        # machine1.inandout([50,0],[50,100])
        ICN = BackgroundTemplate(np.zeros([100, 100]))
        ICN.machine_add(machine1)
        ICN.machine_add(machine2)
        ICN.machine_add(machine3)
        ICN.machine_add(machine4)
        ICN.machine_batch([30, 20], "m1")
        ICN.machine_batch([20, 5], "m2")
        ICN.machine_batch([50, 40], "m3")
        ICN.machine_batch([10, 10], "m4")
        ICN.product_line("p1", ["m1", "m2", "m3"])
        ICN.product_line("p2", ["m2", "m3"])
        ICN.product_line("p3", ["m3", "m4", "m1"])

        # print(ICN.machine_dict)
        print(ICN.product_distance_calculate("p1"))
        print(ICN.product_distance_calculate("p2"))
        print(ICN.product_distance_calculate("p3"))
        ICN.product_line_img("p1")
        ICN.product_line_img("p2")
        ICN.product_line_img("p3")
