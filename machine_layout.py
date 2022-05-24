from email.errors import BoundaryError
import numpy as np
from math import dist
from matplotlib import pyplot as plt
from collections import OrderedDict, defaultdict

class MachineTemplate:
    def __init__(self,machine,machine_code):
        #Rules are 2 axis matrix where first row means rule name and 
        #other rows mean the characters that should define before we start the project
        self.rules = np.array([[]])
        self.occupy = machine
        self.layout = machine
        self.machine_code = machine_code#code is a string that can found on product manufacturing process table
        # self.in_position,self.out_position = self.inandout()
        # self.background = machine
    def inandout(self):
        self.input_pos = np.where(self.background==3)[0][0],np.where(self.background == 3)[1][0]
        self.output_pos = np.where(self.background==5)[0][0],np.where(self.background == 5)[1][0]
    def Rules(self,Rules):
        self.rules.vstack(Rules)
        '''How to assign rule is one of the main problem
        I think sort of matrix form would be perfect
        first line is the rule name(fire, water, etc)
        and the characters are on the same line
        for example, water has 1 in first row means water closer than 1 to machine'''
        
    def background_sole(self, background):#without any other machine, only the machine is in the entire background
        self.background = background
        self.inandout()
        return background

class FactoryTemplate:
    def __init__(self,bg):
        self.null_bg = bg
        self.bg = bg#background must be a numpy matrix with 0 and 1, 1 as already occupied and 0 for empty space
        self.machine_dict = defaultdict(MachineTemplate)

    def collide_check(self):
        if 2 in self.bg:
            return True
        return False

    def machine_add(self, machine):#Adding dictionary of machine
        self.machine_dict[machine.machine_code] = machine

    def machine_distance_calculate(self, passage_path=None):
        self.machine_dict = OrderedDict(sorted(self.machine_dict.items()))
        num_of_machine = len(self.machine_dict)
        if not passage_path:
            passage_path = np.ones((num_of_machine,num_of_machine))
        self.machine_dist_mat = np.zeros((num_of_machine,num_of_machine))
        print('machine_dict',self.machine_dict)
        for y,start_code in enumerate(self.machine_dict):
            for x,end_code in enumerate(self.machine_dict):
                start_template = self.machine_dict[start_code]
                end_template = self.machine_dict[end_code]
                print('in: ',y,', out: ', x, start_template.output_pos, end_template.input_pos,dist(start_template.output_pos, end_template.input_pos))
                self.machine_dist_mat[y][x] = dist(start_template.output_pos, end_template.input_pos)
        return self.machine_dist_mat
    
    def machine_batch(self,position,machine_code):
        try:
            one_machine_layout = self.null_bg
            one_machine_layout[position[0]:position[0]+self.machine_dict[machine_code].occupy.shape[0],
                    position[1]:position[1]+self.machine_dict[machine_code].occupy.shape[1]] += self.machine_dict[machine_code].occupy
            self.machine_dict[machine_code].background_sole(one_machine_layout)
            self.machine_dict[machine_code] = self.machine_dict[machine_code]
        except ValueError as e:
            print(e)
            raise BoundaryError('Machine exceeds boundary, machine position is {} and machine size is {}'.format(position,self.machine_dict[machine_code].occupy.shape))
        if self.collide_check():
            self.collision = 1
            print("collision")
        return self.bg
    def products_manufacturing_process_table(self,products_manufacturing_process_table):
        self.products_manufacturing_process_table = products_manufacturing_process_table
    def machine_distance(self):
        np.zeros(())
    def bg2img(self):
        img = np.zeros((self.bg.shape[0],self.bg.shape[1],3),dtype=np.uint8)
        img[self.bg==0]=(255,255,255)
        img[self.bg==1]=(0,0,0)
        img[self.bg==2]=(255,0,0)
        img[self.bg==3]=(0,255,0)
        img[self.bg==5]=(0,0,255)
        
        img = plt.imshow(img)
#I think machine class is needed because substances in and out must be defined
#What kind of characteristics do machines have to have?
#In and Out of substance and size of machine and Rules
# for i in range(10):
#     m1 = np.ones([20,10])
#     m1[0,i]=3#start position
#     m1[i,9] = 5
#     m2 = np.ones([10,20])
#     m2[i,0]=3
#     m2[0,i]=5
#     m3 = np.ones([30,20])
#     m3[i,0]=3
#     m3[0,5]=5
    
            
#     machine1 = MachineTemplate(m1,1)
#     machine2 = MachineTemplate(m2,2)
#     machine3 = MachineTemplate(m3,3)

#     # machine1.inandout([50,0],[50,100])
#     Incheon_Airport = FactoryTemplate(np.zeros([100,100]))
#     Incheon_Airport.machine_add(machine1)
#     Incheon_Airport.machine_add(machine2)
#     Incheon_Airport.machine_add(machine3)
#     Incheon_Airport.machine_batch([30,20],1)
#     Incheon_Airport.machine_batch([20,5],2)
#     Incheon_Airport.machine_batch([50,40],3)
#     # print(Incheon_Airport.machine_dict)
#     print(Incheon_Airport.machine_distance_calculate())
#     Incheon_Airport.bg2img()
#     #