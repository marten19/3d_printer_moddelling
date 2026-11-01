# Modelling of Dynamical Systems: Mini Project
## Setup
From the project folder, create and activate a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib pyyaml control transitions
```
## Running the simulations

All simulations are started from the project folder with one command, choosing the simulation with `-run`:

```bash
source .venv/bin/activate
python -m src.main -run <simulation>
```

| Command | Simulation |
|---|---|
| `python -m src.main -run ellipse` | CoreXY input response: ellipse |
| `python -m src.main -run ellipse K L` | Ellipse with own parameters, e.g. `ellipse 3 2` |
| `python -m src.main -run heart` | CoreXY input response: heart |
| `python -m src.main -run heart K` | Heart with own scale, e.g. `heart 5` |
| `python -m src.main -run nozzle_step` | Step response of the nozzle temperature |
| `python -m src.main -run pde` | Cooling of one printed layer of filament (PDE) |
| `python -m src.main -run square` | Hybrid system: printing a square |
| `python -m src.main -run square_empty` | Hybrid system: square where the filament runs out midway |

