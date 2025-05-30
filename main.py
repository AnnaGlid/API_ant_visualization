import time
import threading
import numpy as np
import tkinter as tk
from matplotlib import cm
import ttkbootstrap as tb
from matplotlib.figure import Figure 
from ttkbootstrap.dialogs.dialogs import Messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from api import Anthill

# tabelka: funckja, wartości parametrów, iteracja w której osiągnięto optimum / odległość od optimum

def rastrigin(x: float|np.ndarray, y: float|np.ndarray):
    return 10*2 + (x**2 - 10*np.cos(2*np.pi*x)) + (y**2 - 10*np.cos(2*np.pi*y))  

def schwefel(x: float|np.ndarray, y: float|np.ndarray):
    return - (x * np.sin(np.sqrt(np.abs(x))) + y * np.sin(np.sqrt(np.abs(y))))

def sferic(x: float|np.ndarray, y: float|np.ndarray):
    return x**2 + y**2

def rosenbrock(x: float|np.ndarray, y: float|np.ndarray):
    return (x-1)**2 + 100 * (y - (x**2))**2

def michalewicz(x: float|np.ndarray, y: float|np.ndarray):
    return - np.sin(x) * (np.sin((x**2)/np.pi))**20 - np.sin(y) * (np.sin((2* y**2)/ np.pi))**20

def easom(x: float|np.ndarray, y: float|np.ndarray):
    return -np.cos(x) * np.cos(y) * np.exp(-((x - np.pi)**2 + (y - np.pi)**2))

def ackley(x: float|np.ndarray, y: float|np.ndarray):
    return -20*np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2))) \
            - np.exp(0.5 * (np.cos(2*np.pi*x) + np.cos(2*np.pi*y))) \
            + 20 + np.e

def griewank(x: float|np.ndarray, y: float|np.ndarray):
    return ((x**2 + y**2)/4000) - (np.cos(x) * np.cos(y / np.sqrt(2))) + 1

def perm(x: float|np.ndarray, y: float|np.ndarray): 
    b = 0.5
    return ((1 + b)*(x - 1) + (2 + b)*(y/2 - 1 ))**2 \
        +  ((1 + b)*(x**2 - 1) + (4 + b)*((y/2)**2 - 1) )**2    

def sheckel(x: float|np.ndarray, y: float|np.ndarray):
    C = np.array([
        [4, 1, 8, 6, 3],
        [4, 1, 8, 6, 7]
    ])    
    B = np.array([1/10, 2/10, 2/10, 4/10, 4/10])

    result = np.zeros_like(x, dtype=np.float64)

    for i in range(len(B)):
        xi = C[0, i]
        yi = C[1, i]
        result += 1.0 / ((x - xi)**2 + (y - yi)**2 + B[i])

    return -result
        

class App():

    ELEMENTS = 100    
    TEST_FUNCTIONS = {
        'Sferic model': {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 0,
            'extremum_y': 0,
            'domain_min': -5.12,
            'domain_max': 5.12,
            'func': sferic          
        },
        "Perm's f.": {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 1,
            'extremum_y': 2,
            'domain_min': -2,
            'domain_max': 2,
            'func': perm      
        },
        "Rosenbrock's f.": {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 1,
            'extremum_y': 1,
            'domain_min': -5,
            'domain_max': 5,
            'func': rosenbrock                
        },
        "Michalewicz's f.": {
            'type': 'min',
            'extremum_val': -1.8013,
            'extremum_x': 2.20319,
            'extremum_y': 1.57049,
            'domain_min': 0,
            'domain_max': 5,
            'func': michalewicz
        },
        "Easom's f.": {
            'type': 'min',
            'extremum_val': -1,
            'extremum_x': round(np.pi, 5),
            'extremum_y': round(np.pi, 5),
            'domain_min': -100,
            'domain_max': 100,
            'func': easom
        },        
        "Rastrigin's f.": {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 0,
            'extremum_y': 0,
            'domain_min': -5.12,
            'domain_max': 5.12,            
            'func': rastrigin
        },
        "Schwefel's  f.": {
            'type': 'min',
            'extremum_val': -418.9829 * 2,
            'extremum_x': 420.9687,
            'extremum_y': 420.9687,
            'domain_min': -500,
            'domain_max': 500,
            'func': schwefel
        },
        "Ackley's f.": {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 0,
            'extremum_y': 0,
            'domain_min': -32.768,
            'domain_max': 32.768,
            'func': ackley
        },
        "Griewank's f.": {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 0,
            'extremum_y': 0,
            'domain_min': -600,
            'domain_max': 600,
            'func': griewank
        },
        "Shekel's foxholes": {
            'type': 'min',
            'extremum_val': -10.1532,
            'extremum_x': 4,
            'extremum_y': 4,
            'domain_min': 0,
            'domain_max': 10,
            'func': sheckel
        }
    } 

    print('Calculating functions...')
    for func_name, val in TEST_FUNCTIONS.items():
        TEST_FUNCTIONS[func_name]['x'] = np.linspace(val['domain_min'], val['domain_max'], ELEMENTS)
        TEST_FUNCTIONS[func_name]['y'] = np.linspace(val['domain_min'], val['domain_max'], ELEMENTS)
        f_X, f_Y = np.meshgrid(TEST_FUNCTIONS[func_name]['x'], TEST_FUNCTIONS[func_name]['y'], indexing='xy')
        TEST_FUNCTIONS[func_name]['X'] = f_X
        TEST_FUNCTIONS[func_name]['Y'] = f_Y
        TEST_FUNCTIONS[func_name]['Z'] = val['func'](f_X, f_Y)
    print('Done.')
    
    def __init__(self):
        self.exit_event = threading.Event()            
        # visuals
        self.root = tb.Window(themename='darkly')
        self.root.title ('API ant algoritm visualization')
        self.defaultFont = tk.font.nametofont("TkDefaultFont") 
        self.defaultFont.configure(size=10)
        max_width, max_height = self.root.maxsize()
        self.root.geometry('{}x{}'.format(max_width, max_height))
        self.root.state('zoomed')
        root_frame = tb.Frame(self.root)
        root_frame.grid(column=0, row=0, padx=50, pady=10)        
        root_frame.columnconfigure(0, weight=4)
        root_frame.columnconfigure(1, weight=1)
        root_frame.columnconfigure(2, weight=1)

        lframe_info = tb.LabelFrame(root_frame, text="Information")
        lframe_info.grid(column=1, row=0, columnspan=1, ipadx=5, sticky='ns', padx=(50,0))
        frame_graph = tb.Frame(root_frame)
        frame_graph.grid(row=0, column=0)   
        frame_plot_dist = tb.Frame(frame_graph, padding=5)
        frame_plot_dist.grid(row=0)
        frame_plot_func = tb.Frame(frame_graph)
        frame_plot_func.grid(row=1)

        frame_parameters = tb.Frame(root_frame)
        frame_parameters.grid(row=0, column=2, padx=5, sticky='ns')    

        #region info
        info_w_width = 200
        frame_iteration = tb.LabelFrame(lframe_info, text='Iteration', width=info_w_width)
        frame_iteration.grid(row=0, column=0, padx=10, pady=(10,5), sticky='nesw')
        self.label_iteration = tb.Label(frame_iteration, text=0)
        self.label_iteration.pack(padx=50, pady=10)

        frame_nest_in_extr = tb.LabelFrame(lframe_info, text="Nest in extremum", width=info_w_width)
        frame_nest_in_extr.grid(row=1, padx=10, pady=5, sticky='nesw')
        self.label_nest_in_extr = tb.Label(frame_nest_in_extr, text='No', justify='left')
        self.label_nest_in_extr.pack(padx=50, pady=10)
        
        frame_nest_pos = tb.LabelFrame(lframe_info, text="Nest coordinates", width=info_w_width)
        frame_nest_pos.grid(row=2, padx=10, pady=5, sticky='nesw')
        self.label_nest_pos = tb.Label(frame_nest_pos, text='None\n\n x', justify='left')
        self.label_nest_pos.pack(padx=(30, 10), pady=10)

        frame_func_extr = tb.LabelFrame(lframe_info, text="Function extremum", width=info_w_width)
        frame_func_extr.grid(row=3, padx=10, pady=5, sticky='news')
        self.label_func_extr = tb.Label(frame_func_extr)
        self.label_func_extr.pack(padx=(30, 10), pady=10)                

        frame_nest_dist = tb.LabelFrame(lframe_info, text="Distance to extremum", width=info_w_width)
        frame_nest_dist.grid(row=4, padx=10, pady=5, sticky='news')
        self.label_nest_dist = tb.Label(frame_nest_dist)
        self.label_nest_dist.pack(padx=(30, 10), pady=10)       
        #endregion

        #region parameters
        lframe_parameters = tb.LabelFrame(frame_parameters, text="Parameters")
        lframe_parameters.pack(padx=(0,5), anchor='n')

        frame_ants_nbr = tb.LabelFrame(lframe_parameters, text="Number of ants")
        frame_ants_nbr.pack(pady=10)
        self.input_ants_nbr = tb.Entry(frame_ants_nbr, width=10)
        self.input_ants_nbr.pack(padx=10, pady=5)

        frame_ant_memory = tb.LabelFrame(lframe_parameters, text="Ant memory")
        frame_ant_memory.pack(pady=10)
        self.input_ant_memory = tb.Entry(frame_ant_memory, width=10)
        self.input_ant_memory.pack(padx=10, pady=5) 

        frame_ant_moves = tb.LabelFrame(lframe_parameters, text="Ant moves")
        frame_ant_moves.pack(pady=10)
        self.input_ant_moves = tb.Entry(frame_ant_moves, width=10)
        self.input_ant_moves.pack(padx=10, pady=5) 

        frame_a_site = tb.LabelFrame(lframe_parameters, text="A site parameter")
        frame_a_site.pack(pady=10)
        self.input_a_site = tb.Entry(frame_a_site, width=10)
        self.input_a_site.pack(padx=10, pady=5) 

        frame_a_local = tb.LabelFrame(lframe_parameters, text="A local parameter")
        frame_a_local.pack(pady=10)
        self.input_a_local = tb.Entry(frame_a_local, width=10)
        self.input_a_local.pack(padx=10, pady=5) 

        frame_failed = tb.LabelFrame(lframe_parameters, text="Failed explorations")
        frame_failed.pack(pady=10)
        self.input_failed = tb.Entry(frame_failed, width=10)
        self.input_failed.pack(padx=10, pady=5)         

        self.test_function_var = tk.StringVar(lframe_parameters)
        frame_function = tb.LabelFrame(lframe_parameters, text="Test function")
        frame_function.pack(pady=10)
        combobox_function = tb.Combobox(frame_function, textvariable=self.test_function_var, 
                                        state='readonly', width=15)
        combobox_function.bind('<<ComboboxSelected>>', self.update_plot)
        combobox_function['values'] = list(self.TEST_FUNCTIONS)
        combobox_function.pack(padx=10, pady=5)

        frame_speed = tb.LabelFrame(lframe_parameters, text="Timelapse speed")
        frame_speed.pack(pady=10)
        self.speed_val = tk.IntVar(lframe_parameters, 10)
        self.scale_speed = tb.Scale(frame_speed, from_=1, to=100, orient=tb.HORIZONTAL, 
                               length=200, variable=self.speed_val)
        self.scale_speed.pack(padx=10, pady=5)

        reset_btn = tb.Button(lframe_parameters, text="Reset", takefocus=False, 
                              command=self.reset_parameters, width=10)
        reset_btn.pack(pady=(20, 5), ipadx=30, ipady=3)

        self.btn_run = tb.Button(lframe_parameters, text="Run", takefocus=False, 
                            command=self.run, width=10, style="success")
        self.btn_parameters = {
            "pady" :(1,15), 
            "ipadx": 30, 
            "ipady": 3
        }
        self.btn_run.pack(**self.btn_parameters)
        self.btn_stop = tb.Button(lframe_parameters, text="Stop", takefocus=False, width=10, 
                                  command=self.pause, style='danger')        
        #endregion
        self.dots = None        
        #region plot
        self.fig_dist = Figure(figsize = (11, 2), dpi = 100)                                   
        self.canvas_dist = FigureCanvasTkAgg(self.fig_dist, master=frame_plot_dist)
        self.canvas_dist.draw()
        self.canvas_dist.get_tk_widget().pack()
        self.plot_dist = self.fig_dist.add_subplot()

        self.fig = Figure(figsize = (11, 5.8), dpi = 100)                                   
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_plot_func)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_plot_func)      
        #endregion
        self.reset_parameters(without_plot = True)
        self.update_plot()        
        self.root.mainloop()        

    def reset_parameters(self, without_plot: bool = False):        
        self.set_text(self.input_ants_nbr, '3000')
        self.set_text(self.input_ant_memory, '2')
        self.set_text(self.input_ant_moves, '5')
        self.set_text(self.input_a_site, '0.01')
        self.set_text(self.input_a_local, '10')
        self.set_text(self.input_failed, '6')
        self.label_nest_dist.config(text="None")
        self.test_function_var.set(list(self.TEST_FUNCTIONS)[0])
        self.speed_val.set(10)
        self.label_nest_in_extr.config(text="No")
        self.label_iteration.config(text="0")
        func_data = self.TEST_FUNCTIONS[self.test_function_var.get()]
        self.label_nest_pos.config(text="None\n\n o")
        self.label_func_extr.config(text=f'x: {func_data['extremum_x']}\ny: {func_data['extremum_y']}\nz: {func_data['extremum_val']}')
        self.exit_event.set()
        self.dist_values = []
        self.plot_dist.clear()
        # self.canvas_dist.draw()
        if not without_plot:
            self.update_plot()

    def run(self):
        self.plot_dist.clear()
        self.dist_values = []
        func = self.test_function_var.get()        
        func_info = self.TEST_FUNCTIONS[func]
        print(f'run: {func}')
        self.anthill = Anthill(
            ants_number=self.get_int(self.input_ants_nbr),
            memory_slots=self.get_int(self.input_ant_memory),
            t_moves=self.get_int(self.input_ant_moves),
            space=[
                func_info['x'],
                func_info['y'],
                func_info['Z']
            ],
            extremum_type=func_info['type'],
            extremum_point=(
                func_info['extremum_x'],
                func_info['extremum_y'],
                func_info['extremum_val']
            ),
            func=func_info['func'],
            a_site = self.get_float(self.input_a_site),
            a_local = self.get_float(self.input_a_local, max=900000),
            failed_explo = self.get_int(self.input_failed)
        )
        try:
            try: self.ax_3d.remove()
            except: pass
            try: self.ax.remove()
            except: pass
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.pcolor(func_info['X'], func_info['Y'], func_info['Z'])     
            self.show_nest(*self.anthill.nest)
            self.show_ants(self.anthill.get_ants())
            self.fig.tight_layout()
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
            self.toolbar.update() 
            self.canvas.get_tk_widget().pack()                
            self.exit_event.clear()
            self.iteration_per_second = self.speed_val.get()
            th = threading.Thread(target=self.run_algorithm, daemon=True)
            self.btn_run.pack_forget()
            self.btn_stop.pack(**self.btn_parameters)
            th.start()
            self.wait_for_finish()
        except Exception as ex:
            print(ex)
            self.exit_event.set()        

    def pause(self):
        print(f'pause: {self.test_function_var.get()}')
        self.btn_stop.pack_forget()
        self.btn_run.pack(**self.btn_parameters)
        self.exit_event.set()

    def run_algorithm(self):        
        print('Run algorithm')        
        now = time.time()
        timeout = now + 60*30
        iteration = 0
        time.sleep(1)
        nest_in_extr = False
        self.canvas.draw_idle()       
        while not self.exit_event.is_set() and time.time() < timeout:                          
            curr_nest_in_extr = self.anthill.get_nest_in_extr()
            if nest_in_extr != curr_nest_in_extr:
                self.label_nest_in_extr.config(text = 'Yes' if curr_nest_in_extr else 'No')
                self.exit_event.set()
            for move in range(self.anthill.t_moves):
                self.anthill.move()
                self.move_ants(self.anthill.get_ants())
                self.canvas.draw_idle()
                time.sleep(1 / (self.speed_val.get() * 20))
            self.anthill.move_nest()
            self.move_nest(*self.anthill.nest)
            nx, ny, nz = self.anthill.nest
            x_str = round(nx, 5) if 'e' not in str(nx) else format(nx, '.3e')   
            y_str = round(ny, 5) if 'e' not in str(ny) else format(ny, '.3e') 
            z_str = round(nz, 5) if 'e' not in str(nz) else format(nz, '.3e') 
            self.label_nest_pos.config(text=f'x: {x_str}\ny: {y_str}\nz: {z_str}')
            self.label_nest_pos.update()
            self.canvas.draw_idle()
            print('Iteration: '+str(iteration))
            iteration += 1            
            self.label_iteration.config(text=str(iteration))     
            self.label_iteration.update()                      
            time.sleep((1 / self.speed_val.get()) * 5)           

        if time.time() >= timeout:
            print('Timeout!')
            self.exit_event.set()
            self.reset_parameters()            

    def wait_for_finish(self):
        if self.exit_event.is_set():
            self.btn_stop.pack_forget()
            self.btn_run.pack(**self.btn_parameters)            
            self.root.update_idletasks()
            print('Finished')
        else:            
            self.root.after(100, self.wait_for_finish)

    def get_int(self, widget: tb.Entry) -> int:
        value = widget.get()
        try:
            val = int(value)
        except Exception as ex:
            Messagebox.show_error(f'Error while getting int value from input "{value}": {ex}')
        if val < 1 or val > 5000:
            Messagebox.show_error(f'Value {val} is out of range [1, 5000]')
        else:
            return val
    
    def get_float(self, widget: tb.Entry, min: int = 0, max: int = 1) -> float:
        value = widget.get()
        try:
            fl = float(value)
        except Exception as ex:
            Messagebox.show_error(f'Error while getting float value from input "{value}": {ex}')
        if fl < min or fl > max:
            Messagebox.show_error(f'Value {value} is out of range [{min}, {max}]!')
        else:
            return fl

    def set_text(self, widget, text):
        widget.delete(0,tk.END)
        widget.insert(0, text)
        
    def update_plot(self, widget = None):
        ''' Widget is passed during binded action'''
        self.exit_event.set()
        chosen_func = self.test_function_var.get()
        print('chosen func: ' + chosen_func)
        func_data = self.TEST_FUNCTIONS[chosen_func]
        self.label_func_extr.config(text=f'x: {func_data['extremum_x']}\ny: {func_data['extremum_y']}\nz: {func_data['extremum_val']}')        
        self.label_nest_pos.config(text="None\n\n")
        try: self.ax_3d.clear()
        except: pass
        try: self.ax.remove()
        except: pass
        try: self.fig.delaxes(self.ax)   
        except: pass
        self.canvas.draw()
        self.ax_3d = self.fig.add_subplot(1, 1, 1, projection='3d')
        p = self.ax_3d.plot_surface(func_data['X'], func_data['Y'], 
                                 func_data['Z'], rstride=1, cstride=1, 
                                 cmap=cm.coolwarm, linewidth=0, antialiased=False) 
        self.fig.tight_layout()
        self.ax_3d.set_position([0, 0, 1, 1])
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar.update() 
        self.canvas.get_tk_widget().pack()
        self.dist_values = []
        self.plot_dist.clear()
        self.canvas_dist.draw()

    def show_nest(self, x, y, z):
        self.nest_mark, = self.ax.plot(x, y, color='r', marker='X', markersize=13, zorder=10)

    def show_ants(self, ants: list[tuple[float]]):
        self.ant_marks, = self.ax.plot([ant[0] for ant in ants], [ant[1] for ant in ants], 
                                       'o', markersize=4, markerfacecolor='black',
                                       markeredgecolor='white', markeredgewidth=1)

    def move_nest(self, x, y, z):
        self.nest_mark.set_data(x, y)
        curr_distance = self.anthill.get_dist_from_optimum()
        self.dist_values.append(curr_distance)
        self.label_nest_dist.config(text=str(round(curr_distance, 5)) if 'e' not in str(curr_distance) else format(curr_distance, '.3e'))
        self.plot_dist.plot(self.dist_values)
        self.canvas_dist.draw()

    def move_ants(self, ants: list[tuple[float]]):
        self.ant_marks.set_data([ant[0] for ant in ants], [ant[1] for ant in ants])

app = App()