import numpy as np
import random


class Spot():

    def __init__(self, x: float, y: float, z: float, success: bool|None = None):
        self.x = x
        self.y = y 
        self.z = z
        self.success = success
        self.failed = 0

class Ant():

    def __init__(self, idx, memory_slots: int, nest: list[float], space: list, 
                 func, my_a_site: float, my_a_local: float, max_side_len: float,
                 extremum_type: str):
        self.memory = [None for i in range(memory_slots)]
        self.memory_slots = memory_slots
        self.space = space
        self.nest = nest        
        self.func = func
        self.idx = idx
        self.current_spot = None
        self.my_a_site = my_a_site
        self.my_a_local = my_a_local
        self.side_len = max_side_len
        self.pos = self.q_explo(my_a_site)
        self.extremum_type = extremum_type

    def set_current_spot(self, spot: Spot):
        self.current_spot = spot
        self.pos = [spot.x, spot.y]

    def find_new_spot(self):
        x, y = self.q_explo(self.my_a_site)
        spot = Spot(x, y, self.func(x, y))
        self.add_to_memory(spot)
        self.set_current_spot(spot)
        
    def get_random_point_radius(self, radius: float, x: float, y: float) -> list:
        if radius == 0:
            return [x, y]
        alpha = 2 * np.pi * random.random()
        r = radius * np.sqrt(random.random())
        x = r * np.cos(alpha) + x
        y = r * np.sin(alpha) + y
        if x < self.space['X'][0]:
            x = self.space['X'][0]
        if x > self.space['X'][-1]:
            x = self.space['X'][-1]
        if y < self.space['Y'][0]:
            y = self.space['Y'][0]
        if y > self.space['Y'][-1]:
            y = self.space['Y'][-1]
        return [x, y]
    
    def q_explo(self, amplitude: float) -> list[float, float]:
        x, y, z = self.nest
        return self.get_random_point_radius(amplitude * self.side_len, x, y)
    
    def add_to_memory(self, spot: Spot):
        for idx, slot in enumerate(self.memory):
            if not slot:
                self.memory[idx] = spot
                return
    
    def clean_memory(self):
        self.memory = [None for i in range(self.memory_slots)]

    def choose_random_spot_from_memory(self):
        spot = random.choice(self.memory)
        self.set_current_spot(spot)

    def explore_current_spot(self):
        spot_nearby = self.get_random_point_radius(self.my_a_local * self.side_len,
                                                     self.current_spot.x, self.current_spot.y)
        spot_nearby_val = self.func(*spot_nearby)
        if (self.extremum_type == 'min' and spot_nearby_val < self.current_spot.z) or\
            (self.extremum_type == 'max' and spot_nearby_val > self.current_spot.z):
            self.current_spot.success = True
            self.current_spot = Spot(spot_nearby[0], spot_nearby[1], spot_nearby_val, True)
        else:
            self.current_spot.success = False
            self.current_spot.failed += 1
            
        

class Anthill():

    def __init__(self, ants_number: int, memory_slots: int, t_moves: int, 
                 space: list, extremum_type: str, extremum_point: tuple[float], 
                 func, a_site: float, a_local: float, failed_explo: int):
        self.space = {'X': space[0], 'Y': space[1], 'Z': space[2]}
        self.func = func
        self.nest = self.q_rand()                
        self.t_moves = t_moves        
        self.extremum_type = extremum_type
        self.extremum_point = extremum_point        
        a_site_x = (1/a_site)**(1/ants_number)
        self.failed_explo = failed_explo
        x_len = self.space['X'][-1] - self.space['X'][0]
        y_len = self.space['Y'][-1] - self.space['Y'][0]
        self.ants = [
            Ant(i, memory_slots, self.nest, self.space, func,
                my_a_site = (a_site_x**i) * a_site,
                my_a_local = a_local,
                max_side_len = x_len if x_len > y_len else y_len,
                extremum_type=extremum_type)
            for i in range(1, ants_number+1)
        ]
        
    def move(self):
        for ant in self.ants:
            if any([slot is None for slot in ant.memory]):
                ant.find_new_spot()
                ant.explore_current_spot()
            else:
                if ant.current_spot.success:
                    ant.explore_current_spot()
                else:
                    ant.choose_random_spot_from_memory()
                    ant.explore_current_spot()
        self.sort_out_ants_memory()
        for idx in range(len(self.ants) - 1):
            self.tandem_run(self.ants[idx], self.ants[idx+1])

    def move_nest(self):
        best_spot = None
        best_spot_val = 99999999999 if self.extremum_type == 'min' else -9999999999
        for ant in self.ants:
            for spot in ant.memory:
                if not spot:
                    continue
                if (self.extremum_type == 'min' and spot.z < best_spot_val) or \
                    (self.extremum_type == 'max' and spot.z > best_spot_val):
                    best_spot = spot
                    best_spot_val = spot.z
        if best_spot:
            self.nest = [best_spot.x, best_spot.y, best_spot.z]
        else:
            print('Did not find best spot!')

        for ant in self.ants:
            ant.nest = self.nest
            ant.clean_memory()

    def tandem_run(self, ant_a: Ant, ant_b: Ant):
        if self.extremum_type == 'min':
            min_a = min(place.z for place in ant_a.memory if place)
            min_b = min(place.z for place in ant_b.memory if place)
            if min_a < min_b:
                best_place = next(filter(lambda x: x and x.z == min_a, ant_a.memory))
                place_to_replace = next(filter(lambda x: x and x.z == min_b, ant_b.memory))
                ant_b.memory.remove(place_to_replace)
                ant_b.memory.append(best_place)
            elif min_a > min_b:
                best_place = next(filter(lambda x: x and x.z == min_b, ant_b.memory))
                place_to_replace = next(filter(lambda x: x and x.z == min_a, ant_a.memory))
                ant_a.memory.remove(place_to_replace)
                ant_a.memory.append(best_place)                
    
    def sort_out_ants_memory(self):
        for ant in self.ants:
            for spot in ant.memory:
                if spot and spot.failed > self.failed_explo:
                    ant.memory.remove(spot)
                    ant.memory.append(None)

    def q_rand(self):
        x = random.choice(self.space['X'])
        y= random.choice(self.space['Y'])
        return [x, y, self.func(x,y)]
    
    def get_ants(self) -> list:        
        return [ant.pos for ant in self.ants]
    
    # def get_ants_in_extr(self):
    #     count = 0
    #     ex_x, ex_y, ex_z = self.extremum_point
    #     for ant in self.ants:
    #         x = ant.pos[0]
    #         y = ant.pos[1]
    #         if x == ex_x and y == ex_y:
    #             count += 1
    #     return count
    
    def get_nest_in_extr(self):
        ex_x, ex_y, ex_z = self.extremum_point
        if self.nest[0] == ex_x and self.nest[1] == ex_y:
            return True
        return False