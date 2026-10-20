from src.printer import *
from src.dynamics import *

SQUARE = [(10, 10), (100, 10), (100, 100), (10, 100), (10, 10)]


def sim_square():
    printer = Printer()
    printer.target_points = SQUARE
    printer.run(300)
    printer.plot()


def sim_square_empty_filament():
    printer = Printer()
    printer.target_points = SQUARE
    printer.filament_on_roll = 150
    printer.run(300)
    printer.plot()
    
def ellipse_input_response():
    U, X0 = ellipse_input()
    input_response(U,X0)

def heart_input_response():
    U, X0 = heart_input()
    input_response(U,X0)
    
if __name__ == "__main__":
    ellipse_input_response()
    heart_input_response()
    # sim_square()
    sim_square_empty_filament()
