from transitions.extensions import GraphMachine

states = ["q0", "q1", "q2", "q3"]

machine = GraphMachine(
    states=states,
    initial="q0",
    title="Parked detection",
)


machine.add_transition("(H,0)", "q0", "q1")
machine.add_transition("(V,0)", "q0", "q2")
machine.add_transition("(V,+)", "q0", "q0")
machine.add_transition("(H,+)", "q0", "q0")
machine.add_transition("(V,0)", "q1", "q3")
machine.add_transition("(H,+)", "q1", "q1")
machine.add_transition("(H,0)", "q1", "q1")
machine.add_transition("(V,+)", "q1", "q1")
machine.add_transition("(H,0)", "q2", "q3")
machine.add_transition("(V,+)", "q2", "q2")
machine.add_transition("(V,0)", "q2", "q2")
machine.add_transition("(H,+)", "q2", "q2")
machine.add_transition("(H,+)", "q3", "q3")
machine.add_transition("(H,0)", "q3", "q3")
machine.add_transition("(V,+)", "q3", "q3")
machine.add_transition("(V,0)", "q3", "q3")


subcomments = {
    "q0": "q0\n x=+, y=+",
    "q1": "q1\n x=0, y=+",
    "q2": "q2\n x=+, y=0",
    "q3": "q3\n x=0, y=0",
}

ACCEPTING = {"q3"}

graph = machine.get_graph()
# graph.graph_attr["rankdir"] = "LR"

if hasattr(graph, "get_node"):
    for name, text in subcomments.items():
        node = graph.get_node(name)
        node.attr.update(
            label=text,
            shape="circle",
            peripheries="2" if name in ACCEPTING else "1",
            style="filled",
            fillcolor="white",
            color="black",
        )
    graph.add_node("start", label="", shape="none", width="0", height="0")
    graph.add_edge("start", "q0", label="start")
    graph.draw("parked_model.png", prog="dot")
else:
    for name, text in subcomments.items():
        graph.node(
            name,
            label=text,
            shape="circle",
            peripheries="2" if name in ACCEPTING else "1",
            style="filled",
            fillcolor="white",
            color="black",
        )
    graph.node("start", label="", shape="none", width="0", height="0")
    graph.edge("start", "q0", label="start")
    graph.render("parked_model", format="png", cleanup=True)

print("Saved FSM diagram to parked_model.png")
