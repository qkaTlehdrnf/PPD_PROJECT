from email.errors import BoundaryError
import numpy as np
from matplotlib import pyplot as plt


class BackgroundTemplate:
    def __init__(self,bg):
        self.bg = bg#background must be a numpy matrix with 0 and 1, 1 as already occupied and 0 for empty space
    def collide_check(self):
        if 2 in self.bg:
            return True
        return False
    def machine_batch(self,position,machine):
        print(position[0],machine.occupy.shape)
        try:
            self.bg[position[0]:position[0]+machine.occupy.shape[0],
                    position[1]:position[1]+machine.occupy.shape[1]] += machine.occupy
        except ValueError:
            raise BoundaryError('Machine exceeds boundary, machine position is {} and machine size is {}'.format(position,machine.shape))
        if self.collide_check():
            self.collision = 1
            print("collision")
        return self.bg
    def products_manufacturing_process_table(self,products_manufacturing_process_table):
        self.products_manufacturing_process_table = products_manufacturing_process_table
    def bg2img(self):
        img = np.zeros((self.bg.shape[0],self.bg.shape[1],3),dtype=np.uint8)
        img[self.bg==1]=(0,0,0)
        img[self.bg==0]=(255,255,255)
        img[self.bg==2]=(255,0,0)
        img = plt.imshow(img)
#I think machine class is needed because substances in and out must be defined
#What kind of characteristics do machines have to have?
#In and Out of substance and size of machine and Rules

class MachineTemplate:
    def __init__(self,machine,machine_code):
        #Rules are 2 axis matrix where first row means rule name and 
        #other rows mean the characters that should define before we start the project
        self.rules = np.array([[]])
        self.occupy = machine
        self.machine_code = machine_code#code is a string that can found on product manufacturing process table
    def inandout(self,in_position=None,out_position=None):
        if in_position is None:
            self.in_position ,self.out_position = 1/2*self.occupy
        self.in_position = in_position
        self.out_position = out_position
    def Rules(self,Rules):
        self.rules.vstack(Rules)
        #How to assign rule is one of the main problem
        #I think sort of matrix form would be perfect
        #first line is the rule name(fire, water, etc)
        #and the characters are on the same line
        #for example, water has 1 in first row means water closer than 1 to machine
        
        
machine1 = MachineTemplate(np.ones([10,10]),'darpa')
machine2 = MachineTemplate(np.ones([20,20]),'europa')
# machine1.inandout([50,0],[50,100])
Incheon_Airport = BackgroundTemplate(np.zeros([30,30]))
Incheon_Airport.machine_batch([15,20],machine1)
Incheon_Airport.machine_batch([10,10],machine2)
Incheon_Airport.bg2img()
#