import numpy as np
import random

class Point():

    def __init__(self, x: float, y: float, z: float, success: bool):
        self.x = x
        self.y = y 
        self.z = z
        self.success = success


class Ant():

    def __init__(self, memory_slots: int):
        self.memory = [None for i in range(memory_slots)]
        self.pos = (None, None, None)


class Anthill():

    def __init__(self, ants_number: int, memory_slots: int, t_moves: int, 
                 space: list, extremum_type: str, extremum_point: tuple[float]):
        self.ants = [Ant(memory_slots) for i in range(ants_number)]
        self.t_moves = t_moves
        self.space = {'X': space[0], 'Y': space[1], 'Z': space[2]}
        self.extremum_type = extremum_type
        self.extremum_point = extremum_point
        self.nest = self.q_rand()

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
        x_idx = random.choice(range(len(self.space['X'])))
        y_idx = random.choice(range(len(self.space['Y'])))
        return (self.space['X'][x_idx], self.space['Y'][y_idx], self.space['Z'][y_idx][x_idx])
    
    def q_explo(self, amplitude: float):
        pass

    def get_val(self, x: float, y: float):
        pass