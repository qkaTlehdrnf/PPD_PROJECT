from machine_layout import MachineTemplate, BackgroundTemplate, BoundaryError
import numpy as np
import random
import time
from copy import deepcopy
from tqdm import trange

def factory_random_batch(factory:BackgroundTemplate):
    random.seed(time.time())
    factory.reset_bg()
    batch_state = []
    for m_code in machines:
        while True:
            randh = random.randint(0, h-10)
            randw = random.randint(0, w-10)
            try:
                factory.machine_batch([randh, randw], m_code)
                batch_state.append([randh, randw])
                break
            except BoundaryError as e:
                continue
    return np.array(batch_state).flatten()
    
def factory_batch_loss(factory: BackgroundTemplate, batch_state, collide_mul = 8):
    factory.reset_bg()
    machines = ['m1', 'm2', 'm3', 'm4']
    for idx, m_code in enumerate(machines):
        try:
            factory.machine_batch(batch_state[idx*2:idx*2+2], m_code)
        except BoundaryError as e:
            return np.array(1e4)
    return np.array(factory.loss(collide_mul=8))

def factory_batch_change2min(factory, batch, steps, collide_mul = 2, batch_size = 100):
    pre_batch = deepcopy(batch)
    def_loss = factory_batch_loss(factory, batch, collide_mul)
    new_loss = def_loss
    
    for i in steps:
        for j in range(batch_size):
            pre_batch = deepcopy(batch)
            for k in range(len(pre_batch)):
                pre_batch[k] += random.randint(-i,i)
            new_loss = factory_batch_loss(factory, pre_batch, collide_mul)
            if new_loss < def_loss:
                batch = deepcopy(pre_batch)
                def_loss = new_loss
    
    return def_loss, batch

def factory_best_cases(factory, batch_size, training_time):
    best_cases = []
    for i in (pbar := trange(batch_size)):
        best_loss = int(1e3)
        for batch_idx in range(training_time):
            batch = factory_random_batch(factory)
            cost = factory_batch_loss(factory, batch, collide_mul = 2)
            if not batch_idx % (training_time//100):
                pbar.set_description('{0:>2}%'.format(int(batch_idx/training_time*100)+1))
            if best_loss > cost:
                best_batch = deepcopy(batch)
                best_loss = cost
        best_cases.append(best_batch)
    return best_batch

def factory_bestcases2better(factory, best_cases, steps, batch_size):
    for k in (pbar := trange(len(best_cases))):
        batch = best_cases[k]
        def_loss, batch = factory_batch_change2min(factory, batch, steps= steps, batch_size)
        if def_loss < historical_low:
            historical_low = def_loss
            historical_batch = deepcopy(batch)
            pbar.set_description('{0:>5}%'.format(int(historical_low)))
        new_batch.append(batch)
    
    


if __name__ == "__main__":
    m1 = np.ones([20, 10])
    m2 = np.ones([10, 20])
    m3 = np.ones([30, 20])
    m4 = np.ones([10, 30])

    machine1 = MachineTemplate(m1, 'm1', inandoutpos = [[10,0],[20,10]])
    machine2 = MachineTemplate(m2, 'm2', inandoutpos = [[10,0],[0,15]])
    machine3 = MachineTemplate(m3, 'm3', inandoutpos = [[20,0],[20,20]])
    machine4 = MachineTemplate(m4, 'm4', inandoutpos = [[0,20],[10,30]])

    ICN = BackgroundTemplate(np.zeros([100, 100]))
    ICN.machine_add(machine1)
    ICN.machine_add(machine2)
    ICN.machine_add(machine3)
    ICN.machine_add(machine4)

    ICN.product_line("p1", ['m1', 'm2', 'm3', 'm4'])
    ICN.product_line("p2", ['m1', 'm2', 'm3'])
    ICN.product_line("p3", ['m2', 'm3'])
    ICN.product_line("p4", ['m3', 'm4', 'm1'])
    machines = ['m1', 'm2', 'm3', 'm4']
    
    best_loss = int(1e3)
    best_best_loss = int(1e3)
    best_model = None
    best_cases = factory_best_cases(ICN, batch_size=1e2, epoch=1e3)
    best_cases = factory_batch_change2min(ICN, best_cases, steps= [3,2,1], batch_size= 100)
    new_batch = []
    historical_low = 1e3
    