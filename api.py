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
                 space: list, extremum_type: str, extremum_point: tuple[float], 
                 func, a_site: float, a_local: float):
        self.space = {'X': space[0], 'Y': space[1], 'Z': space[2]}
        self.func = func
        self.nest = self.q_rand()        
        self.ants = [Ant(memory_slots, self.nest, self.space, func) for i in range(ants_number)]
        self.t_moves = t_moves        
        self.extremum_type = extremum_type
        self.extremum_point = extremum_point        
        self.a_site_par = a_site
        self.a_site_x = (1/a_site)**(1/ants_number)
        self.a_local_par = a_local
        
    def move(self):
        pass

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

    def a_site(self, ant_idx):
        val = (self.a_site_x**ant_idx) * self.a_site_par
        print(f'A site value: {val}')
        if val < 0 or val > 1:
            raise Exception(f'Invalid a site value: {val}')
        return val

    def get_ants(self) -> list:        
        return [ant.pos for ant in self.ants]
    
    def get_ants_in_extr(self):
        count = 0
        ex_x, ex_y, ex_z = self.extremum_point
        for ant in self.ants:
            x, y, z = ant.pos            
            if x == ex_x and y == ex_y:
                count += 1
        return count