class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        print("Processing current state:", str(self))

    def on_enter(self, printer):
        pass

    def on_tick(self, printer):
        return self
    
    def filament_rate(self, printer, x):
        return 0.0

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__
