import numpy as np
import random

class Point():

    def __init__(self, x: float, y: float, z: float, success: bool):
        self.x = x
        self.y = y 
        self.z = z
        self.success = success


class Ant():

    def __init__(self, memory_slots: int, nest: list[float], space: list, func):
        self.memory = [None for i in range(memory_slots)]
        self.space = space
        self.nest = nest
        self.func = func
        self.pos = self.q_explo()
        self.func = func

    def q_explo(self, amplitude: float = 0.5) -> list[float]:
        x, y = random.choice(self.space['X']), random.choice(self.space['Y'])
        return [x, y, self.func(x, y)]

class Anthill():

    def __init__(self, ants_number: int, memory_slots: int, t_moves: int, 
                 space: list, extremum_type: str, extremum_point: tuple[float], func):
        self.space = {'X': space[0], 'Y': space[1], 'Z': space[2]}
        self.func = func
        self.nest = self.q_rand()        
        self.ants = [Ant(memory_slots, self.nest, self.space, func) for i in range(ants_number)]
        self.t_moves = t_moves        
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
        x = random.choice(self.space['X'])
        y= random.choice(self.space['Y'])
        return [x, y, self.func(x,y)]
    
    def q_explo(self, amplitude: float):
        pass

    def get_ants(self) -> list:
        return [ant.pos for ant in self.ants]