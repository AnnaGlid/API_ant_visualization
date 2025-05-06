import threading
import numpy as np
import tkinter as tk
from matplotlib import cm
import ttkbootstrap as tb
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
            'extremum': 0,
            'domain_min': -5.12,
            'domain_max': 5.12,
            'X': r_X,
            'Y': r_Y,
            'Z': r_Z
        },
        'F. Schwefel': {
            'type': 'min',
            'extremum': 420.9687,
            'domain_min': -500,
            'domain_max': 500,
            'X': s_X,
            'Y': s_Y,
            'Z': s_Z
        }
    }
    
    def __init__(self):
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

        self.test_function_var = tk.StringVar(lframe_parameters)
        frame_function = tb.LabelFrame(lframe_parameters, text="Test function")
        frame_function.pack(pady=10)
        for fn in list(self.TEST_FUNCTIONS):
            tb.Radiobutton(frame_function, text=fn, variable=self.test_function_var, value=fn)\
                            .pack(padx=10, pady=5)

        self.auto_run_var = tk.IntVar(lframe_parameters, 1)
        auto_run = tb.Checkbutton(lframe_parameters, text="Auto run", variable=self.auto_run_var)
        auto_run.pack(pady=10)

        frame_speed = tb.LabelFrame(lframe_parameters, text="Timelapse speed")
        frame_speed.pack(pady=10)
        self.speed_val = tk.IntVar(lframe_parameters, 50)
        scale_speed = tb.Scale(frame_speed, from_=1, to=100, orient=tb.HORIZONTAL, 
                               length=200, variable=self.speed_val)
        scale_speed.pack(padx=10, pady=5)

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
        self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')  
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graph)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_graph)      
        self.update_plot()   
        #endregion
                        
        self.exit_event = threading.Event()        
        self.root.mainloop()        

    def reset_parameters(self, without_plot: bool = False):        
        # self.set_text(self.input_x_min, '-1000')
        # self.set_text(self.input_x_max, '1000')
        self.dots = self.ax.scatter([],[],[], color='black', s=20)
        self.set_text(self.input_ants_nbr, '20')
        self.set_text(self.input_ant_memory, '2')
        self.test_function_var.set(list(self.TEST_FUNCTIONS)[0])
        self.auto_run_var.set(1)
        self.speed_val.set(50)
        if not without_plot:
            self.update_plot()

    def run(self):
        print(f'run: {self.test_function_var.get()}')
        try:
            self.exit_event.clear()
            self.update_plot()
            th = threading.Thread(target=self.run_algorithm, daemon=True)
            self.btn_run.pack_forget()
            self.btn_stop.pack(**self.btn_parameters)
            th.start()
            self.wait_for_finish()
        except Exception as ex:
            self.exit_event.set()
            print(ex)
        self.exit_event.set()

    def pause(self):
        print(f'pause: {self.test_function_var.get()}')
        self.btn_stop.pack_forget()
        self.btn_run.pack(**self.btn_parameters)        

    def run_algorithm(self):
        pass

    def wait_for_finish(self):
        if self.exit_event.is_set():
            self.btn_stop.grid_forget()
            self.btn_run.grid(**self.btn_parameters)            
            self.root.update_idletasks()
            print('Finished')
        else:            
            self.root.after(100, self.wait_for_finish)

    def set_text(self, widget, text):
        widget.delete(0,tk.END)
        widget.insert(0, text)
        
    def update_plot(self):
        chosen_func = self.test_function_var.get()
        func_data = self.TEST_FUNCTIONS[chosen_func]
        p = self.ax.plot_surface(func_data['X'], func_data['Y'], 
                                 func_data['Z'], rstride=1, cstride=1, 
                                 cmap=cm.coolwarm, linewidth=0, antialiased=False)                
        self.fig.tight_layout()
        self.canvas.draw_idle()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar.update() 
        self.canvas.get_tk_widget().pack()

    def update_plot_ants(self, ants: list = [[], [], []]):
        self.dots._offsets3d = ants
        self.canvas.draw_idle()
        
app = App()