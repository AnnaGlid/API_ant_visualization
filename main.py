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

def rastrigin(x: float, y: float) -> float:
    return 10*2 + (x**2 - 10*np.cos(2*np.pi*x)) + (y**2 - 10*np.cos(2*np.pi*y))

def schwefel(x: float, y: float) -> float:
    return x * np.sin(np.sqrt(np.abs(x))) + y * np.sin(np.sqrt(np.abs(y)))

class App():

    ELEMENTS = 100    

    r_x = np.linspace(-5.12, 5.12, ELEMENTS)
    r_y = np.linspace(-5.12, 5.12, ELEMENTS)
    r_X, r_Y = np.meshgrid(r_x, r_y)
    r_Z = 10*2 + (r_X**2 - 10*np.cos(2*np.pi*r_X)) + (r_Y**2 - 10*np.cos(2*np.pi*r_Y))  

    s_x = np.linspace(-500, 500, ELEMENTS)
    s_y = np.linspace(-500, 500, ELEMENTS)
    s_X, s_Y = np.meshgrid(s_x, s_y)
    s_Z = - (s_X * np.sin(np.sqrt(np.abs(s_X))) + s_Y * np.sin(np.sqrt(np.abs(s_Y))))
    TEST_FUNCTIONS = {
        'F. Rastrigin': {
            'type': 'min',
            'extremum_val': 0,
            'extremum_x': 0,
            'extremum_y': 0,
            'domain_min': -5.12,
            'domain_max': 5.12,            
            'X': r_X,
            'Y': r_Y,
            'Z': r_Z,
            'x': r_x,
            'y': r_y,
            'func': rastrigin
        },
        'F. Schwefel': {
            'type': 'min',
            'extremum_val': -418.9829 * 2,
            'extremum_x': 420.9687,
            'extremum_y': 420.9687,
            'domain_min': -500,
            'domain_max': 500,
            'X': s_X,
            'Y': s_Y,
            'Z': s_Z,
            'x': s_x,
            'y': s_y,
            'func': schwefel
        }
    } 
    
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
        root_frame.grid(column=0, row=0, padx=50, pady=50)        
        root_frame.rowconfigure(0, weight=1)
        root_frame.rowconfigure(1, weight=4)
        root_frame.columnconfigure(0, weight=4)
        root_frame.columnconfigure(1, weight=1)
        top_frame = tb.Frame(root_frame)
        top_frame.grid(column=0, row=0, columnspan=1, pady=20, sticky='e')
        frame_graph = tb.Frame(root_frame)
        frame_graph.grid(row=1, column=0)
        frame_parameters = tb.Frame(root_frame)
        frame_parameters.grid(row=1, column=1, padx=50, sticky='ns')    

        #region top
        frame_iteration = tb.LabelFrame(top_frame, text='Iteration')
        frame_iteration.grid(row=0, column=0, padx=10, pady=2, sticky='e')
        self.label_iteration = tb.Label(frame_iteration, text=0)
        self.label_iteration.pack(padx=50, pady=10)
        frame_ants_number = tb.LabelFrame(top_frame, text="Number of ants in extremum")
        frame_ants_number.grid(row=0, column=1, padx=10, pady=0, sticky='e')
        self.label_ants_number = tb.Label(frame_ants_number, text='0')
        self.label_ants_number.pack(padx=50, pady=10)
        #endregion

        #region parameters
        lframe_parameters = tb.LabelFrame(frame_parameters, text="Parameters")
        lframe_parameters.pack(ipadx=5, anchor='n')

        # frame_x_min = tb.LabelFrame(lframe_parameters, text="Min x")
        # frame_x_min.pack(pady=10)
        # self.input_x_min = tb.Entry(frame_x_min, width=10)
        # self.input_x_min.pack(padx=10, pady=5)

        # frame_x_max = tb.LabelFrame(lframe_parameters, text="Max x")
        # frame_x_max.pack(pady=10)
        # self.input_x_max = tb.Entry(frame_x_max, width=10)
        # self.input_x_max.pack(padx=10, pady=5)

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

        frame_a_site = tb.LabelFrame(lframe_parameters, text="A site")
        frame_a_site.pack(pady=10)
        self.input_a_site = tb.Entry(frame_a_site, width=10)
        self.input_a_site.pack(padx=10, pady=5) 

        frame_a_local = tb.LabelFrame(lframe_parameters, text="A local")
        frame_a_local.pack(pady=10)
        self.input_a_local = tb.Entry(frame_a_local, width=10)
        self.input_a_local.pack(padx=10, pady=5) 

        self.test_function_var = tk.StringVar(lframe_parameters)
        frame_function = tb.LabelFrame(lframe_parameters, text="Test function")
        frame_function.pack(pady=10)
        for fn in list(self.TEST_FUNCTIONS):
            tb.Radiobutton(frame_function, text=fn, variable=self.test_function_var, value=fn, command=self.update_plot)\
                            .pack(padx=10, pady=5)

        # self.auto_run_var = tk.IntVar(lframe_parameters, 1)
        # auto_run = tb.Checkbutton(lframe_parameters, text="Auto run", variable=self.auto_run_var)
        # auto_run.pack(pady=10)

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
        self.reset_parameters(without_plot = True)
        #region plot
        self.fig = Figure(figsize = (11, 5.8), dpi = 100)                           
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graph)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_graph)      
        #endregion
        self.update_plot()        
        self.root.mainloop()        

    def reset_parameters(self, without_plot: bool = False):        
        # self.set_text(self.input_x_min, '-1000')
        # self.set_text(self.input_x_max, '1000')        
        self.set_text(self.input_ants_nbr, '20')
        self.set_text(self.input_ant_memory, '2')
        self.set_text(self.input_ant_moves, '5')
        self.set_text(self.input_a_site, '0.010')
        self.set_text(self.input_a_local, '0.001')
        self.test_function_var.set(list(self.TEST_FUNCTIONS)[0])
        # self.auto_run_var.set(1)
        self.speed_val.set(10)
        self.label_ants_number.config(text="0")
        self.label_iteration.config(text="0")
        self.exit_event.set()
        if not without_plot:
            self.update_plot()

    def run(self):
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
            a_local = self.get_float(self.input_a_local)
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
        timeout = now + 60*5        
        iteration = 0
        time.sleep(2)
        while not self.exit_event.is_set() and time.time() < timeout:
            iteration += 1
            self.show_ants(self.anthill.get_ants())
            self.canvas.draw_idle()
            self.label_iteration.config(text=str(iteration))
            self.label_iteration.update()
            time.sleep((1 / self.speed_val.get()) * 5)

        if time.time() >= timeout:
            print('Timeout!')

    def wait_for_finish(self):
        if self.exit_event.is_set():
            self.btn_stop.pack_forget()
            self.btn_run.pack(**self.btn_parameters)            
            self.root.update_idletasks()
            print('Finished')
        else:            
            self.root.after(100, self.wait_for_finish)

    def get_int(self, widget: tb.Entry):
        value = widget.get()
        try:
            return int(value)
        except Exception as ex:
            Messagebox.show_error(f'Error while getting int value from input "{value}": {ex}')
    
    def get_float(self, widget: tb.Entry):
        value = widget.get()
        try:
            fl = float(value)
        except Exception as ex:
            Messagebox.show_error(f'Error while getting float value from input "{value}": {ex}')
        if fl < 0 or fl > 1:
            Messagebox.show_error(f'Value {value} is out of range [0, 1]!')

    def set_text(self, widget, text):
        widget.delete(0,tk.END)
        widget.insert(0, text)
        
    def update_plot(self):
        self.exit_event.set()
        chosen_func = self.test_function_var.get()
        print('chosen func: ' + chosen_func)
        func_data = self.TEST_FUNCTIONS[chosen_func]
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

    def show_nest(self, x, y, z):
        self.nest_mark, = self.ax.plot(x, y, color='r', marker='X', markersize=13, zorder=10)

    def show_ants(self, ants: list[tuple[float]]):
        self.ant_marks, = self.ax.plot([ant[0] for ant in ants], [ant[1] for ant in ants], 
                                       'o', markersize=4, markerfacecolor='black',
                                       markeredgecolor='white', markeredgewidth=1)

    def move_nest(self, x, y, z):
        self.nest_mark.set_data(x, y)

    def move_ants(self, ants: list[tuple[float]]):
        self.ant_marks.set_data([ant[0] for ant in ants], [ant[1] for ant in ants])

app = App()