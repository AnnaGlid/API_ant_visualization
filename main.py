import tkinter as tk
import ttkbootstrap as tb
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class App():
    TEST_FUNCTIONS = [
        'długa nazwa funkcji a',
        'długa nazwa funkcji b'
    ]
    
    def __init__(self):
        # visuals
        self.root = tb.Window(themename='darkly')
        # self.root.configure(background='#7a4930')
        self.root.title ('API ant algoritm visualization')
        # self.defaultFont.configure(family="Calibri", size=14)
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
        top_frame.grid(column=0, row=0, columnspan=2, padx=50, pady=20)
        frame_graph = tb.Frame(root_frame)
        frame_graph.grid(row=1, column=0)
        frame_parameters = tb.Frame(root_frame)
        frame_parameters.grid(row=1, column=1, padx=50, sticky='')
        
        #region plot
        self.fig = Figure(figsize = (11, 5.8), dpi = 100)         
        self.plot1 = self.fig.add_subplot()         
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graph)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_graph) 
        self.update_plot()
        #endregion

        #region top
        frame_iteration = tb.LabelFrame(top_frame, text='Iteration')
        frame_iteration.grid(row=0, column=0, padx=50, pady=2)
        self.label_iteration = tb.Label(frame_iteration, text=0)
        self.label_iteration.pack(padx=50, pady=10)
        frame_ants_number = tb.LabelFrame(top_frame, text="Number of ants in extremum")
        frame_ants_number.grid(row=0, column=1, padx=50, pady=0)
        self.label_ants_number = tb.Label(frame_ants_number, text='0')
        self.label_ants_number.pack(padx=50, pady=10)
        #endregion

        #region parameters
        lframe_parameters = tb.LabelFrame(frame_parameters, text="Parameters")
        lframe_parameters.pack(ipadx=40, ipady=60, fill='x', expand=True)

        frame_x_min = tb.LabelFrame(lframe_parameters, text="Min x")
        frame_x_min.pack(pady=10)
        input_x_min = tb.Entry(frame_x_min, width=10)
        input_x_min.pack(padx=10, pady=5)

        frame_x_max = tb.LabelFrame(lframe_parameters, text="Max x")
        frame_x_max.pack(pady=10)
        input_x_max = tb.Entry(frame_x_max, width=10)
        input_x_max.pack(padx=10, pady=5)

        frame_ants_nbr = tb.LabelFrame(lframe_parameters, text="Number of ants")
        frame_ants_nbr.pack(pady=10)
        input_ants_nbr = tb.Entry(frame_ants_nbr, width=10)
        input_ants_nbr.pack(padx=10, pady=5)

        frame_ant_memory = tb.LabelFrame(lframe_parameters, text="Ant memory")
        frame_ant_memory.pack(pady=10)
        input_ant_memory = tb.Entry(frame_ant_memory, width=10)
        input_ant_memory.pack(padx=10, pady=5) 

        self.test_function_var = self.TEST_FUNCTIONS[0]
        frame_function = tb.LabelFrame(lframe_parameters, text="Test function")
        frame_function.pack(pady=10)
        for idx, fn in enumerate(self.TEST_FUNCTIONS):
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
        
        #endregion
                
        self.root.mainloop()        
        
    def update_plot(self, x: list =[], xlim: list = [], y_iter: list = [], y_rec: list = []):
        self.plot1.clear()
        self.plot1.plot(x, y_iter, label="Iterative", marker='o')
        self.plot1.plot(x, y_rec, label="Recursive", marker='o')        
        self.plot1.set_xlabel('x')
        self.plot1.set_ylabel('f(x)')
        
        for xx, yy in zip(x, y_iter):
            self.plot1.annotate(self.format_small_number(yy), xy=(xx,yy),)
        for xx, yy in zip(x, y_rec):
            self.plot1.annotate(self.format_small_number(yy), xy=(xx,yy))
        self.plot1.legend()
        if xlim:
            self.plot1.set_xlim(xlim)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.toolbar.update() 
        self.canvas.get_tk_widget().pack()

app = App()