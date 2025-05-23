# If you on a Windows machine with any Python version 
# or an M1 mac with any Python version
# or an Intel Mac with Python > 3.7
# the multi-threaded version does not work
# so instead, you can use this version. 

import unittest
import population
import simulation 
import genome 
import creature 
import numpy as np
import os

class TestGA(unittest.TestCase):
    def testBasicGA(self):
        gene_count = 3
        fixed_body_shape = creature.Creature.generate_fixed_body_shape(gene_count)

        pop = population.Population(pop_size=10, gene_count=gene_count, fixed_body_shape=fixed_body_shape)
        #sim = simulation.ThreadedSim(pool_size=1)
        sim = simulation.Simulation()

        results = 'simulation_results/experimentm'

        #generations 
        for iteration in range(5):
            # this is a non-threaded version 
            # where we just call run_creature instead
            # of eval_population
            for cr in pop.creatures:
                sim.run_creature(cr, 3000) #Timestep in sim
                cr.fitness = cr.calculate_fitness(sim.mountain_top_position)            
            #sim.eval_population(pop, 2400)
            fits = [cr.get_fitness() 
                    for cr in pop.creatures]
            
            with open(os.path.join(results, f'generation_{iteration}.csv'),'w') as f:
                f.write('creature,fitness\n')
                for i, fit in enumerate(fits):
                    f.write(f'{i},{fit}\n')

            links = [len(cr.get_expanded_links()) 
                    for cr in pop.creatures]
            print(iteration, "fittest:", np.round(np.max(fits), 3), 
                  "mean:", np.round(np.mean(fits), 3), "mean links", np.round(np.mean(links)), "max links", np.round(np.max(links)))       
            fit_map = population.Population.get_fitness_map(fits)
            new_creatures = []
            for i in range(len(pop.creatures)):
                p1_ind = population.Population.select_parent(fit_map)
                p2_ind = population.Population.select_parent(fit_map)
                p1 = pop.creatures[p1_ind]
                p2 = pop.creatures[p2_ind]
                # now we have the parents!
                #Creature evolution
                dna = genome.Genome.crossover(p1.dna, p2.dna)
                dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                dna = genome.Genome.grow_mutate(dna, rate=0.1)

                #Motor function evolution
                # dna = genome.Genome.crossover_motor_functions(p1.dna, p2.dna)
                # dna = genome.Genome.mutate_motor(dna, rate=0.1, amount=0.1)
                
                cr = creature.Creature(1)
                cr.update_dna(dna)
                new_creatures.append(cr)
            # elitism
            max_fit = np.max(fits)
            elite_saved = False
            for cr in pop.creatures:
                if cr.get_fitness() == max_fit:
                    new_cr = creature.Creature(1)
                    new_cr.update_dna(cr.dna)
                    new_creatures[0] = new_cr
                    #save to results folder
                    filename = os.path.join(results, f"elite_{iteration}.csv")
                    genome.Genome.to_csv(cr.dna, filename)
                    elite_saved = True
                    break
            if not elite_saved:
                print(f"Warning: elite creature not saved")

            
            pop.creatures = new_creatures
                            
        self.assertNotEqual(fits[0], 0)

unittest.main()
