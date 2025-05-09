import numpy as np

def rastrigin(x: float, y: float) -> float:
    return 10*2 + (x**2 - 10*np.cos(2*np.pi*x)) + (y**2 - 10*np.cos(2*np.pi*y))

def schwefel(x: float, y: float) -> float:
    return x * np.sin(np.sqrt(np.abs(x))) + y * np.sin(np.sqrt(np.abs(y)))