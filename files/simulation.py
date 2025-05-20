import pybullet as p
from multiprocessing import Pool
import math
import random

class Simulation: 

    def __init__(self, sim_id=0):
        self.physicsClientId = p.connect(p.DIRECT)
        self.sim_id = sim_id
        self.mountain_top_position = (0, 0, 5) 

    def load_environment(self):
        pid = self.physicsClientId
        p.resetSimulation(physicsClientId=pid)
        p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=pid)
        p.setGravity(0, 0, -10, physicsClientId=pid)

        #create arena rocks and mountain
        arena_size = 20
        self.make_arena(arena_size)
        self.make_mountain()

    def make_mountain(self, num_rocks=100, max_size=0.25, arena_size=10, mountain_height=5):
        def gaussian(x, y, sigma=arena_size/4):
            """Return the height of the mountain at position (x, y) using a Gaussian function."""
            return mountain_height * math.exp(-((x**2 + y**2) / (2 * sigma**2)))

        # Set the path to your shape files
        p.setAdditionalSearchPath('shapes/')

        # Load the mountain URDF file
        mountain_position = (0, 0, -1)  # Adjust as needed
        mountain_orientation = p.getQuaternionFromEuler((0, 0, 0))
        mountain = p.loadURDF("gaussian_pyramid.urdf", mountain_position, mountain_orientation, useFixedBase=1)

        # Optionally, generate rocks on the mountain (uncomment if needed)
        # for _ in range(num_rocks):
        #     x = random.uniform(-1 * arena_size/2, arena_size/2)
        #     y = random.uniform(-1 * arena_size/2, arena_size/2)
        #     z = gaussian(x, y)  # Height determined by the Gaussian function
        #
        #     size_factor = 1 - (z / mountain_height)
        #     size = random.uniform(0.1, max_size) * size_factor
        #
        #     orientation = p.getQuaternionFromEuler([random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14)])
        #     rock_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[size, size, size])
        #     rock_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[size, size, size], rgbaColor=[0.5, 0.5, 0.5, 1])
        #     rock_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=rock_shape, baseVisualShapeIndex=rock_visual, basePosition=[x, y, z], baseOrientation=orientation)

    def make_arena(self, arena_size=10, wall_height=10):
        wall_thickness = 0.5
        floor_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness])
        floor_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, arena_size/2, wall_thickness], rgbaColor=[1, 1, 0, 1])
        floor_body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=floor_collision_shape, baseVisualShapeIndex=floor_visual_shape, basePosition=[0, 0, -wall_thickness])

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2])
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[arena_size/2, wall_thickness/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1])  # Gray walls

        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, arena_size/2, wall_height/2])
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[0, -arena_size/2, wall_height/2])

        wall_collision_shape = p.createCollisionShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2])
        wall_visual_shape = p.createVisualShape(shapeType=p.GEOM_BOX, halfExtents=[wall_thickness/2, arena_size/2, wall_height/2], rgbaColor=[0.7, 0.7, 0.7, 1])  # Gray walls

        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[arena_size/2, 0, wall_height/2])
        p.createMultiBody(baseMass=0, baseCollisionShapeIndex=wall_collision_shape, baseVisualShapeIndex=wall_visual_shape, basePosition=[-arena_size/2, 0, wall_height/2])

 
    
    def run_creature(self, cr, iterations=2400):
        try:
            pid = self.physicsClientId
            self.load_environment()
            # p.resetSimulation(physicsClientId=pid)
            # p.setPhysicsEngineParameter(enableFileCaching=0, physicsClientId=pid)

            # p.setGravity(0, 0, -10, physicsClientId=pid)
            # plane_shape = p.createCollisionShape(p.GEOM_PLANE, physicsClientId=pid)
            # floor = p.createMultiBody(plane_shape, plane_shape, physicsClientId=pid)

            xml_file = 'temp' + str(self.sim_id) + '.urdf'
            xml_str = cr.to_xml()
            with open(xml_file, 'w') as f:
                f.write(xml_str)
            
            cid = p.loadURDF(xml_file, physicsClientId=pid)

            p.resetBasePositionAndOrientation(cid, [0, 0, 2.5], [0, 0, 0, 1], physicsClientId=pid)


            for step in range(iterations):
                p.stepSimulation(physicsClientId=pid)
                if step % 24 == 0:
                    self.update_motors(cid=cid, cr=cr)

                pos, orn = p.getBasePositionAndOrientation(cid, physicsClientId=pid)
                cr.update_position(pos)
                #print(pos[2])
                #print(cr.get_distance_travelled())

            cr.fitness = cr.calculate_fitness(self.mountain_top_position)
        except:
            print("sim failed cr links: ", len(cr.get_expanded_links()))

    def update_motors(self, cid, cr):
        """
        cid is the id in the physics engine
        cr is a creature object
        """
        for jid in range(p.getNumJoints(cid,
                                        physicsClientId=self.physicsClientId)):
            m = cr.get_motors()[jid]

            p.setJointMotorControl2(cid, jid, 
                    controlMode=p.VELOCITY_CONTROL, 
                    targetVelocity=m.get_output(), 
                    force = 5, 
                    physicsClientId=self.physicsClientId)
        

    # You can add this to the Simulation class:
    def eval_population(self, pop, iterations):
        for cr in pop.creatures:
            self.run_creature(cr, 2400) 


class ThreadedSim():
    def __init__(self, pool_size):
        self.sims = [Simulation(i) for i in range(pool_size)]

    @staticmethod
    def static_run_creature(sim, cr, iterations):
        sim.run_creature(cr, iterations)
        return cr
    
    def eval_population(self, pop, iterations):
        """
        pop is a Population object
        iterations is frames in pybullet to run for at 240fps
        """
        pool_args = [] 
        start_ind = 0
        pool_size = len(self.sims)
        while start_ind < len(pop.creatures):
            this_pool_args = []
            for i in range(start_ind, start_ind + pool_size):
                if i == len(pop.creatures):# the end
                    break
                # work out the sim ind
                sim_ind = i % len(self.sims)
                this_pool_args.append([
                            self.sims[sim_ind], 
                            pop.creatures[i], 
                            iterations]   
                )
            pool_args.append(this_pool_args)
            start_ind = start_ind + pool_size

        new_creatures = []
        for pool_argset in pool_args:
            with Pool(pool_size) as p:
                # it works on a copy of the creatures, so receive them
                creatures = p.starmap(ThreadedSim.static_run_creature, pool_argset)
                # and now put those creatures back into the main 
                # self.creatures array
                new_creatures.extend(creatures)
        pop.creatures = new_creatures
