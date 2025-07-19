#imports
from logic.data_store import G, sink_nodes, edge_controls, node_positions, node_data

#main cytoscape elements
def generate_cytoscape_elements():
    elements = []
    #nodes in graph G
    for node in G.nodes:
        elements.append({
            #id, info, position of nodes in graph, sink class
            "data": {
                "id": str(node),
                "info": f"details about {node}"
            },
            "position": node_positions.get(node, {"x": 0, "y": 0}),
            "classes": "sink" if node in sink_nodes else "normal"
        })
    #edges in graph G
    for u, v, key in G.edges(keys=True):
        #edge id, controls on edge, and control labels
        edge_id = f"{u}-{v}-{key}"
        controls = edge_controls.get(edge_id, [])
        control_label = "\n".join([ctrl["name"] for ctrl in controls]) if controls else ""

        #edge data, id, source, target, label, controls, set as directed edges for arrows
        elements.append({
            "data": {
                "id": edge_id,
                "source": str(u),
                "target": str(v),
                "label": control_label,
                "controls": controls
            },
            "classes": "directed-edge"
        })

    #return elements of graph G
    return elements

#generate stylesheet for layout function
def generate_stylesheet():

    #stylesheet
    stylesheet = [
        #nodes
        {"selector": ".normal", "style": {
            "shape": "rectangle",
            "background-color": "white",
            "border-color": "black",
            "border-width": 1,
            "label": "data(id)",
            "color": "black",
            "font-size": "14px",
            "text-valign": "center",
            "text-halign": "center",
            "font-family": "Computer Modern, serif",
            "width": "label",
            "padding": "5px",
            "text-wrap": "wrap"
        }},
        #sink nodes
        {"selector": ".sink", "style": {
            "shape": "rectangle",
            "background-color": "#f28b82",
            "border-color": "black",
            "border-width": 1,
            "label": "data(id)",
            "color": "black",
            "font-size": "14px",
            "text-valign": "center",
            "text-halign": "center",
            "font-family": "Computer Modern, serif",
            "width": "label",
            "padding": "5px",
            "text-wrap": "wrap"
        }},
        #edges/controls
        {"selector": ".directed-edge", "style": {
            "curve-style": "bezier",
            "line-color": "black",
            "target-arrow-color": "black",
            "target-arrow-shape": "triangle",
            "width": 1,
            "label": "data(label)",
            "font-size": "14px",
            "color": "black",
            "text-rotation": "autorotate",
            "text-wrap": "wrap",
            "text-background-color": "white",
            "text-background-opacity": 1,
            "text-border-width": 0
        }}
    ]

    #return stylesheet for Dash attack graph
    return stylesheet