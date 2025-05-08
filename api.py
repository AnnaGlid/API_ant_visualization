import numpy as np
import random

class Ant():

    def __init__(self, memory_slots: int):
        self.memory = [None for i in range(memory_slots)]
        self.pos = (None, None, None)

class Anthill():

    def __init__(self, ants_number: int, memory_slots: int, t_moves: int, 
                 space: list, extremum_type: str, extremum_point: tuple[float]):
        self.ants = [Ant(memory_slots) for i in range(ants_number)]
        self.nest = (None, None, None)
        self.t_moves = t_moves
        self.space = space # list of ndarrays: X, Y, Z
        self.extremum_type = extremum_type
        self.extremum_point = extremum_point


    def tandem_run(self, ant_a: Ant, ant_b: Ant):
        if self.extremum_type == 'min':
            min_a = min(place[2] for place in ant_a.memory)
            min_b = min(place[2] for place in ant_b.memory)
            if min_a <= min_b:
                best_place = next(filter(lambda x: x[2] == min_a, ant_a.memory))
                place_to_replace = next(filter(lambda x: x[2] == min_b, ant_b.memory))
                ant_b.memory.remove(place_to_replace)
                ant_b.memory.append(best_place)
            else:
                best_place = next(filter(lambda x: x[2] == min_b, ant_b.memory))
                place_to_replace = next(filter(lambda x: x[2] == min_a, ant_a.memory))
                ant_a.memory.remove(place_to_replace)
                ant_a.memory.append(best_place)                
    
    def q_rand(self):
        x = random.choice(self.x)
        y = random.choice(self.y)
        return (x, y, self.s[x][y])
    
    def q_explo(self, amplitude: float):
        pass
