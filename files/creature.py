from turtle import distance
import genome 
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np
from typing import List

class MotorType(Enum):
    PULSE = 1
    SINE = 2

class Motor:
    def __init__(self, control_waveform, control_amp, control_freq):
        if control_waveform <= 0.5:
            self.motor_type = MotorType.PULSE
        else:
            self.motor_type = MotorType.SINE
        self.amp = control_amp
        self.freq = control_freq
        self.phase = 0
    

    def get_output(self):
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        if self.motor_type == MotorType.PULSE:
            if self.phase < np.pi:
                output = 1
            else:
                output = -1
            
        if self.motor_type == MotorType.SINE:
            output = np.sin(self.phase)
        
        return output 
    

class Creature:
    fixed_body_shape = None
    spec = None

    def __init__(self, gene_count):
        #self.spec = genome.Genome.get_gene_spec()
        #self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        if Creature.fixed_body_shape is None:
            Creature.spec = genome.Genome.get_gene_spec()
            Creature.fixed_body_shape = self.generate_fixed_body_shape(gene_count)
        self.dna = Creature.fixed_body_shape
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.get_flat_links()
        self.get_expanded_links()
        self.start_position = None
        self.last_position = None
        self.dist = 0
        self.fitness = 0

    @staticmethod
    def generate_fixed_body_shape(gene_count):
        spec = genome.Genome.get_gene_spec()
        dna = genome.Genome.get_random_genome(len(spec), gene_count)
        return dna

    def set_dna(self, dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.get_flat_links()
        self.get_expanded_links()
        self.start_position = None
        self.last_position = None
        self.dist = 0
        self.fitness = 0

    def get_flat_links(self):
        if self.flat_links == None:
            gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
            self.flat_links = genome.Genome.genome_to_links(gdicts)
        return self.flat_links
    
    def get_expanded_links(self):
        self.get_flat_links()
        if self.exp_links is not None:
            return self.exp_links
        
        exp_links = [self.flat_links[0]]
        genome.Genome.expandLinks(self.flat_links[0], 
                                self.flat_links[0].name, 
                                self.flat_links, 
                                exp_links)
        self.exp_links = exp_links
        return self.exp_links

    def to_xml(self):
        self.get_expanded_links()
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None, "start", None)
        robot_tag = adom.createElement("robot")
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        first = True
        for link in self.exp_links:
            if first:# skip the root node! 
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        robot_tag.setAttribute("name", "pepe") #  choose a name!
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()

    def get_motors(self):
        self.get_expanded_links()
        if self.motors == None:
            motors = []
            for i in range(1, len(self.exp_links)):
                l = self.exp_links[i]
                m = Motor(l.control_waveform, l.control_amp,  l.control_freq)
                motors.append(m)
            self.motors = motors 
        return self.motors 
    
    def update_position(self, pos):
        if self.last_position != None:
            p1 = np.asarray(self.last_position)
            p2 = np.asarray(pos)
            dist = np.linalg.norm(p1-p2)
            self.dist = self.dist + dist

        if self.start_position == None:
            self.start_position = pos
        else:
            self.last_position = pos

    def get_distance_travelled(self):
        # if self.start_position is None or self.last_position is None:
        #     return 0
        # p1 = np.asarray(self.start_position)
        # p2 = np.asarray(self.last_position)
        # dist = np.linalg.norm(p1-p2)
        # return dist 
        return self.dist


    def calculate_fitness(self, mountain_top: List[float]):
        if self.last_position is None:
            return 0.0

        #dist to mountain top
        distance_to_top = np.linalg.norm(np.array(self.last_position)- np.array(mountain_top))

        #closer to mountain top is better
        fitness = 1.0 / (distance_to_top + 1)
        return fitness

    def get_fitness(self):
        return self.fitness

    def update_dna(self, dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None