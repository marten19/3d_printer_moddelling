from src.printer import *
from src.dynamics import *
from src.filament_temp_pde import *
from src.model_nozzle import *

import src
import argparse

SQUARE = [(0.01, 0.01), (0.1, 0.01), (0.1, 0.1), (0.01, 0.1), (0.01, 0.01)]

def sim_square():
    printer = Printer()
    printer.target_points = SQUARE
    printer.run(300)
    printer.plot()


def sim_square_empty_filament():
    printer = Printer()
    printer.target_points = SQUARE
    printer.new_roll = 1.5
    printer.x[9] = 0.001
    printer.run(10000)
    printer.plot()


def ellipse_input_response(K=1, L=3):
    U, X0 = ellipse_input(K,L)
    input_response(U, X0)


def heart_input_response(K=5):
    U, X0 = heart_input(K)
    input_response(U, X0)


def main():
    parser = argparse.ArgumentParser(description="Run one simulation")
    parser.add_argument(
        "-run",
        required=True,
        choices=["square", "square_empty", "ellipse", "heart", "pde", "nozzle_step"],
    )
    parser.add_argument("params", nargs="*", type=float)
    args = parser.parse_args()

    match args.run:
        case "square":
            sim_square()
        case "square_empty":
            sim_square_empty_filament()
        case "ellipse":
            ellipse_input_response(*args.params)
        case "heart":
            heart_input_response(*args.params)
        case "pde":
            pde_sim()
        case "nozzle_step":
            step_response(*args.params)


if __name__ == "__main__":    
    main()
