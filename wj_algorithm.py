from machine_layout import MachineTemplate, BackgroundTemplate, BoundaryError
import numpy as np
import random
import time
from copy import deepcopy
from tqdm import trange


def factory_random_batch(factory: BackgroundTemplate):
    random.seed(time.time())
    factory.reset_bg()
    h, w = factory.null_bg.shape
    batch_state = []
    for m_code in factory.machine_dict:
        while True:
            randh = random.randint(0, h - 10)
            randw = random.randint(0, w - 10)
            try:
                factory.machine_batch([randh, randw], m_code)
                batch_state.append([randh, randw])
                break
            except BoundaryError as e:
                continue
    return np.array(batch_state).flatten()


def factory_batch_loss(factory: BackgroundTemplate, batch, collide_mul=8):
    factory.reset_bg()
    for idx, m_code in enumerate(factory.machine_dict):
        try:
            factory.machine_batch(batch[idx * 2 : idx * 2 + 2], m_code)
        except BoundaryError as e:
            return np.array(1e4)
        except IndexError as e:
            print(idx, m_code, batch)
            raise e
    return np.array(factory.loss(collide_mul=8))


def factory_img(factory: BackgroundTemplate, batch):
    factory.reset_bg()
    for idx, m_code in enumerate(factory.machine_dict):
        factory.machine_batch(batch[idx * 2 : idx * 2 + 2], m_code)
    for p in factory.product_machines:
        factory.product_line_img(p)


def factory_best_cases(factory, batch_size, training_size):
    best_cases = []
    for i in (pbar := trange(batch_size)) :
        best_loss = int(1e10)
        for batch_idx in range(training_size):
            batch = factory_random_batch(factory)
            cost = factory_batch_loss(factory, batch, collide_mul=2)
            if not batch_idx % (training_size // 100 if training_size > 100 else 1):
                pbar.set_description(
                    "{0:>2}%".format(int(batch_idx / training_size * 100) + 1)
                )
            if best_loss > cost:
                best_batch = deepcopy(batch)
                best_loss = cost
        best_cases.append(best_batch)
    return best_cases


def factory_batch_change2min(factory, batch, steps, collide_mul=2, batch_size=100):
    pre_batch = deepcopy(batch)
    def_loss = factory_batch_loss(factory, batch, collide_mul)
    new_loss = def_loss
    for i in steps:
        for j in range(batch_size):
            pre_batch = deepcopy(batch)
            for k in range(len(pre_batch)):
                pre_batch[k] += random.randint(-i, i)
            new_loss = factory_batch_loss(factory, pre_batch, collide_mul)
            if new_loss < def_loss:
                batch = deepcopy(pre_batch)
                def_loss = new_loss
    return def_loss, batch


def factory_bestcases2better(factory, best_cases, steps, batch_size):
    historical_low = int(1e4)
    batches = []
    for k in (pbar := trange(len(best_cases))) :
        batch = best_cases[k]
        def_loss, batch = factory_batch_change2min(
            factory, batch, steps=steps, batch_size=batch_size
        )
        batches.append(list(batch))
        if def_loss < historical_low:
            historical_low = def_loss
            historical_batch = deepcopy(batch)
            pbar.set_description("{0:>5}%".format(int(historical_low)))
    best_cases = list(map(list, best_cases))
    return (
        historical_batch,
        [[best_cases[i], batches[i]] for i in range(len(best_cases))],
    )


if __name__ == "__main__":
    m1 = np.ones([20, 10])
    m2 = np.ones([10, 20])
    m3 = np.ones([30, 20])
    m4 = np.ones([10, 30])
    m5 = np.ones([35, 35])

    machine1 = MachineTemplate(m1, "m1", inandoutpos=[[10, 0], [20, 10]])
    machine2 = MachineTemplate(m2, "m2", inandoutpos=[[10, 0], [0, 15]])
    machine3 = MachineTemplate(m3, "m3", inandoutpos=[[20, 0], [20, 20]])
    machine4 = MachineTemplate(m4, "m4", inandoutpos=[[0, 20], [10, 30]])
    machine5 = MachineTemplate(m5, "m5", inandoutpos=[[0, 0], [35, 35]])

    ICN = BackgroundTemplate(np.zeros([100, 100]))
    ICN.machine_add(machine1)
    ICN.machine_add(machine2)
    ICN.machine_add(machine3)
    ICN.machine_add(machine4)
    ICN.machine_add(machine5)

    ICN.add_product_line("p1", ["m1", "m2", "m3", "m4"])
    ICN.add_product_line("p2", ["m1", "m5", "m2", "m3"])
    ICN.add_product_line("p3", ["m2", "m3"])
    ICN.add_product_line("p4", ["m3", "m4", "m1", "m5"])

    best_loss = int(1e3)
    best_best_loss = int(1e3)
    # batch_size = int(1e2)
    # training_size = int(1e3)
    steps = [3, 2, 1]
    collide_mul = 2
    best_model = None
    with open("batch_training_size.txt", "w") as f:
        for bs in range(3, 10):
            batch_size = 2 ** bs
            for ts in range(5, 15):
                training_size = 2 ** ts
                f.write(
                    "Batch size: {0:>5}/ Training size: {1:>5}\n".format(
                        batch_size, training_size
                    )
                )
                loses = []
                for i in range(32):
                    if i > 8 and np.std(loses) < 1e-3:
                        break
                    best_cases = factory_best_cases(
                        ICN, batch_size=batch_size, training_size=training_size
                    )
                    best_case, best_cases = factory_bestcases2better(
                        factory=ICN,
                        best_cases=best_cases,
                        steps=steps,
                        batch_size=batch_size,
                    )
                    loses.append(
                        factory_batch_loss(ICN, best_case, collide_mul=collide_mul)
                    )
                    # for case in best_cases: print(case[0], '->', case[1])
                    # print(best_case)
                    # print(factory_batch_loss(ICN, best_case, collide_mul = 2))
                    # factory_img(ICN, best_case)
                f.write("{0:>5}/{1:>5} {i}th end".format(np.mean(loses), np.std(loses)))

