from transitions.extensions import GraphMachine

states = [
    "printing",
    "stop",
    "to_tower",
    "wiping",
    "retract_filament",
    "cooling_nozzle",
    "load_filament",
    "heating_nozzle",
    "resume",
]

machine = GraphMachine(
    states=states,
    initial="printing",
    title="Filament Replacement FSM",
)


machine.add_transition("C", "printing", "stop")
machine.add_transition("F", "printing", "stop")
machine.add_transition("", "stop", "to_tower")
machine.add_transition("x=0, y=0", "to_tower", "wiping")

machine.add_transition("C", "wiping", "retract_filament")
machine.add_transition("retracted", "retract_filament", "cooling_nozzle")
machine.add_transition("F", "wiping", "cooling_nozzle")

machine.add_transition("T < T_target", "cooling_nozzle", "load_filament")
machine.add_transition("loaded", "load_filament", "heating_nozzle")
machine.add_transition("T = T_target", "heating_nozzle", "resume")
machine.add_transition("x = x_saved, y = y_saved", "resume", "printing")


subcomments = {
    "printing": "printing",
    "stop": "stop\nSave (x_saved, y_saved)",
    "to_tower": "to_tower_c\nMove to (0, 0)",
    "wiping": "wiping_c\nWiping excess",
    "cooling_nozzle": "cooling_nozzle\nHeater off",
    "retract_filament": "retract_filament\nRetract old filament",
    "load_filament": "load_filament\nLoad new filament",
    "heating_nozzle": "heating_nozzle\nHeater to T_target",
    "resume": "resume\nMove to (x_saved, y_saved)",
}

graph = machine.get_graph()

if hasattr(graph, "get_node"):
    for name, text in subcomments.items():
        node = graph.get_node(name)
        node.attr["label"] = text
    graph.draw("fsm_model.png", prog="dot")
else:
    for name, text in subcomments.items():
        graph.node(name, label=text)
    graph.render("fsm_model", format="png", cleanup=True)

print("Saved FSM diagram to fsm_model.png")
