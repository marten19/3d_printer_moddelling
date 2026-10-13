from printer_states import *

class Printer(object):
    """ 
    A simple state machine that mimics the functionality of a device from a 
    high level.
    """
    filament_flag = "none"
    wiping_flag = "none"
    temperature = 0
    x = 0
    y = 0

    def __init__(self):
        """ Initialize the components. """

        # Start with a default state.
        self.state = PrintingState()

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        """

        # The next state will be the result of the on_event function.
        print(event)
        self.state = self.state.on_event(self, event)
        
    def tick(self):
        self.state = self.state.on_tick(self)
        
    def get_temperature(self):
        return self.temperature

    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    
    def run(self):
        while True:
            t += 0.1
            self.tick(t)
    
    

if __name__ == "__main__":
    printer = Printer()
    printer.x = 10
    printer.y = 10
    printer.temperature = 220
    printer.on_event('C')
    printer.tick()
    printer.temperature = 20
    printer.tick()
    printer.tick()
    printer.x = 0
    printer.y = 0
    printer.tick()
    printer.tick()
    printer.tick()
    printer.on_event('wipping_finished')
    printer.tick()
    printer.on_event('retracted')
    printer.tick()
    printer.temperature = 25
    printer.tick()
    printer.tick()
    printer.on_event('loaded')
    printer.temperature = 221
    printer.tick()
    printer.x = 10
    printer.y = 10
    printer.tick()
    
    

    
    
    

