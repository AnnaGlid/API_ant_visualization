import threading
import tkinter as tk
import ttkbootstrap as tb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.figure import Figure 
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def schwefel_fun(self):
        pass

class App():
    TEST_FUNCTIONS = {
        'F. Rastrigin': {
            
        },
        'F. Schwefel': {
            'type': 'min',
            'extremum': 420.9687,
            'domain_min': -500,
            'domain_max': 500,
            'func': schwefel_fun
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
        
        #region plot
        self.fig = Figure(figsize = (11, 5.8), dpi = 100)         
        self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')  
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graph)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_graph)         
        #endregion

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
                
        self.exit_event = threading.Event()
        self.reset_parameters()
        self.root.mainloop()        

    def reset_parameters(self):
        self.update_plot()
        # self.set_text(self.input_x_min, '-1000')
        # self.set_text(self.input_x_max, '1000')
        self.set_text(self.input_ants_nbr, '20')
        self.set_text(self.input_ant_memory, '2')
        self.test_function_var.set(list(self.TEST_FUNCTIONS)[0])
        self.auto_run_var.set(1)
        self.speed_val.set(50)

    def run(self):
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
        func_data = self.TEST_FUNCTIONS[self.test_function_var]
        x = np.linspace(0, 10, 100)
        y = np.linspace(0, 5, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        p = self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1, 
                                 cmap=cm.coolwarm, linewidth=0, antialiased=False)

        cb = self.fig.colorbar(p, shrink=0.5)     
        # self.plot1.clear()
        # self.plot1.plot(x, y_iter, label="Iterative", marker='o')
        # self.plot1.set_xlabel('x')
        # self.plot1.set_ylabel('f(x)')
        
        # for xx, yy in zip(x, y_iter):
        #     self.plot1.annotate(self.format_small_number(yy), xy=(xx,yy),)
        # for xx, yy in zip(x, y_rec):
        #     self.plot1.annotate(self.format_small_number(yy), xy=(xx,yy))
        # self.plot1.legend()
        # if xlim:
        #     self.plot1.set_xlim(xlim)
        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.toolbar.update() 
        self.canvas.get_tk_widget().pack()

app = App()