import numpy as np
import random


class Spot():

    def __init__(self, x: float, y: float, z: float, success: bool|None = None):
        self.x = x
        self.y = y 
        self.z = z
        self.success = success

class Ant():

    def __init__(self, idx, memory_slots: int, nest: list[float], space: list, func):
        self.memory = [None for i in range(memory_slots)]
        self.space = space
        self.nest = nest
        self.func = func
        self.pos = self.q_explo()
        self.func = func
        self.idx = idx
        self.current_spot = None

    def find_new_spot(self):
        x, y = self.q_explo(self.a_site(self.idx))
        spot = Spot(x, y, self.func(x, y))
        self.add_to_memory(spot)
        self.current_spot = spot
        
    def get_random_point_radius(self, radius: float, x: float, y: float) -> list:
        if radius == 0:
            return [x, y]
        alpha = 2 * np.pi * random.random()
        r = radius * np.sqrt(random.random())
        x = r * np.cos(alpha) + x
        y = r * np.sin(alpha) + y
        return [x, y]
    
    def q_explo(self, amplitude: float) -> list[float, float]:
        x, y, z = self.nest
        return self.get_random_point_radius(amplitude * self.side_len, x, y)

    def a_site(self, ant_idx):
        val = (self.a_site_x**ant_idx) * self.a_site_par
        print(f'A site value: {val}')
        if val < 0 or val > 1:
            raise Exception(f'Invalid a site value: {val}')
        return val
    
    def add_to_memory(self, spot: Spot):
        for idx, slot in enumerate(self.memory):
            if not slot:
                self.memory[idx] = spot


class Anthill():

    def __init__(self, ants_number: int, memory_slots: int, t_moves: int, 
                 space: list, extremum_type: str, extremum_point: tuple[float], 
                 func, a_site: float, a_local: float):
        self.space = {'X': space[0], 'Y': space[1], 'Z': space[2]}
        self.func = func
        self.nest = self.q_rand()        
        self.ants = [Ant(i, memory_slots, self.nest, self.space, func) for i in range(1, ants_number+1)]
        self.t_moves = t_moves        
        self.extremum_type = extremum_type
        self.extremum_point = extremum_point        
        self.a_site_par = a_site
        self.a_site_x = (1/a_site)**(1/ants_number)
        self.a_local_par = a_local
        x_len = self.space['X'][-1] - self.space['X'][0]
        y_len = self.space['Y'][-1] - self.space['Y'][0]
        self.side_len = x_len if x_len > y_len else y_len
        
    def move(self):
        for ant in self.ants:
            if any([slot is None for slot in ant.memory]):
                ant.find_new_spot()

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