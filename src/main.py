from src.printer import *

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
    



if __name__ == "__main__":
    sim_square()
    sim_square_empty_filament()
