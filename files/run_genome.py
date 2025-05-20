import genome
import creature
import pybullet as p
import time 
import numpy as np
import simulation
import os

# Connect to the physics server (GUI mode)
p.connect(p.GUI)
p.setPhysicsEngineParameter(enableFileCaching=0)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
plane_shape = p.createCollisionShape(p.GEOM_PLANE)
floor = p.createMultiBody(plane_shape)
p.setGravity(0, 0, -10)
p.setRealTimeSimulation(1)

# Load DNA from CSV file 
results_folder = 'simulation_results/experimenta1'
filename = os.path.join(results_folder, "elite_49.csv")  
dna = genome.Genome.from_csv(filename)

# Create a creature with the loaded DNA
cr = creature.Creature(gene_count=len(dna))
cr.set_dna(dna)

sim = simulation.Simulation()
sim.load_environment()


# Save the creature to XML (optional, for viewing or debugging)
with open('test.urdf', 'w') as f:
    f.write(cr.to_xml())

# Load the creature into the simulation at the foot of the mountain
mountain_top_position = sim.mountain_top_position  # Access mountain position from simulation.py

# Adjust the initial position of the creature
initial_position = (mountain_top_position[0] - 4, mountain_top_position[1] - 4, 2.5)  # Example offset from the mountain


# Load the creature into the simulation
rob1 = p.loadURDF('test.urdf', initial_position)
start_pos, _ = p.getBasePositionAndOrientation(rob1)

# Simulation loop
elapsed_time = 0
wait_time = 1.0 / 240  # seconds
total_time = 5  # seconds
step = 0
dist_moved = 0

while True:
    p.stepSimulation()
    step += 1
    if step % 120 == 0:
        motors = cr.get_motors()
        assert len(motors) == p.getNumJoints(rob1), "Number of motors and joints do not match"
        for jid in range(p.getNumJoints(rob1)):
            mode = p.VELOCITY_CONTROL
            vel = motors[jid].get_output()
            p.setJointMotorControl2(rob1, jid, controlMode=mode, targetVelocity=vel)
        
        new_pos, _ = p.getBasePositionAndOrientation(rob1)
        dist_moved = np.linalg.norm(np.asarray(start_pos) - np.asarray(new_pos))
        #print("Distance moved:", dist_moved)
    
    time.sleep(wait_time)
    elapsed_time += wait_time
    
    if elapsed_time > total_time:
        break

print("TOTAL DISTANCE MOVED:", dist_moved)
