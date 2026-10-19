from transitions.extensions import GraphMachine

states = [
    "q0",
    "q1",
    "q2",
    "q3"
]

machine = GraphMachine(
    states=states,
    initial="q0",
    title="Parked detection",
)


# machine.add_transition("C", "printing", "stop_c")



subcomments = {
    # "stop_c": "STOP\n[Save (x_saved, y_saved)]",
}

graph = machine.get_graph()

if hasattr(graph, "get_node"):
    for name, text in subcomments.items():
        node = graph.get_node(name)
        node.attr["label"] = text
    graph.draw("parked_model.png", prog="dot")
else:
    for name, text in subcomments.items():
        graph.node(name, label=text)
    graph.render("parked_model.png", format="png", cleanup=True)

print("Saved FSM diagram to parked_model.png")
