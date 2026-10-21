from transitions.extensions import GraphMachine

states = [
    "printing",
    "stop_c",
    "to_tower_c",
    "wiping_c",
    "stop_f",
    "to_tower_f",
    "wiping_f",
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


machine.add_transition("C", "printing", "stop_c")
machine.add_transition("pos saved", "stop_c", "to_tower_c")
machine.add_transition("x=0, y=0", "to_tower_c", "wiping_c")
machine.add_transition("wiping_done", "wiping_c", "retract_filament")

machine.add_transition("F", "printing", "stop_f")
machine.add_transition("pos saved", "stop_f", "to_tower_f")
machine.add_transition("x=0, y=0", "to_tower_f", "wiping_f")
machine.add_transition("wiping_done", "wiping_f", "cooling_nozzle")

machine.add_transition("retracted", "retract_filament", "cooling_nozzle")
machine.add_transition("T < T_target", "cooling_nozzle", "load_filament")
machine.add_transition("loaded", "load_filament", "heating_nozzle")
machine.add_transition("T >= T_target", "heating_nozzle", "resume")
machine.add_transition("x = x_saved, y = y_saved", "resume", "printing")


subcomments = {
    "printing": "printing",
    "stop_c": "stop_c\nSave (x_saved, y_saved)",
    "stop_f": "stop_f\nSave (x_saved, y_saved)",
    "to_tower_c": "to_tower_c\nMove to (0, 0)",
    "to_tower_f": "to_tower_f\nMove to (0, 0)",
    "wiping_c": "wiping_c\nWiping excess",
    "wiping_f": "wiping_f\nWiping excess",
    "cooling_nozzle": "cooling_nozzle\nHeater off",
    "retract_filament": "retract_filament\nRetract old filament",
    "load_filament": "load_filament\nLoad new filament",
    "heating_nozzle": "heating_nozzle\nHeater to T_target",
    "resume": "resume\nMove to (x_saved, y_saved)",
}


graph = machine.get_graph()

ACCEPTING = {"printing"}

graph = machine.get_graph()
graph.graph_attr["rankdir"] = "LR"

if hasattr(graph, "get_node"):
    for name, text in subcomments.items():
        graph.get_node(name).attr.update(
            label=text,
            shape="box",
            peripheries="2" if name in ACCEPTING else "1",
            style="rounded,filled",
            fillcolor="white",
            color="black",
        )
    graph.add_node("start", label="", shape="none", width="0", height="0")
    graph.add_edge("start", "printing", label="start")
    graph.draw("fsm_model.png", prog="dot")
else:
    for name, text in subcomments.items():
        graph.node(
            name,
            label=text,
            shape="box",
            peripheries="2" if name in ACCEPTING else "1",
            style="rounded,filled",
            fillcolor="white",
            color="black",
        )
    graph.node("start", label="", shape="none", width="0", height="0")
    graph.edge("start", "printing", label="start")
    graph.render("fsm_model", format="png", cleanup=True)

print("Saved FSM diagram to fsm_model.png")
