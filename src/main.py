from src.printer import *
from src.dynamics import *
from src.heat import *
import argparse

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
    input_response(U, X0)


def heart_input_response():
    U, X0 = heart_input()
    input_response(U, X0)


def main():
    parser = argparse.ArgumentParser(description="Run one simulation")
    parser.add_argument(
        "-run",
        required=True,
        choices=["square", "square_empty", "ellipse", "heart", "pde"],
    )
    args = parser.parse_args()

    match args.run:
        case "square":
            sim_square()
        case "square_empty":
            sim_square_empty_filament()
        case "ellipse":
            ellipse_input_response()
        case "heart":
            heart_input_response()
        case "pde":
            pde_sim()


if __name__ == "__main__":
    main()
