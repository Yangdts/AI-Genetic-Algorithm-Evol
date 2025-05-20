import creature 
import numpy as np

class Population:
    def __init__(self, pop_size, gene_count, fixed_body_shape=None):
        self.pop_size = pop_size
        self.creatures = []
        self.fixed_body_shape = fixed_body_shape
        for _ in range(pop_size):
            cr = creature.Creature(gene_count)
            if fixed_body_shape:
                cr.set_dna(fixed_body_shape)
            self.creatures.append(cr)

    @staticmethod
    def get_fitness_map(fits):
        fitmap = []
        total = 0
        for f in fits:
            total = total + f
            fitmap.append(total)
        return fitmap
    
    @staticmethod
    def select_parent(fitmap):
        r = np.random.rand() # 0-1
        r = r * fitmap[-1]
        for i in range(len(fitmap)):
            if r <= fitmap[i]:
                return i

