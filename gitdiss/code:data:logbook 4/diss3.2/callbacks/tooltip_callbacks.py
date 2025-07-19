#imports
from logic.data_store import G, edge_controls, node_data, sink_nodes
from dash import Output, Input, State, ctx, html
from dash import Input, Output, State, ctx, ALL, html, dcc

def register_callbacks(app):   

    #callback to populate tooltip box to the right of attack graph to dislpay node/edge/control info 
    @app.callback(
            Output("tooltip-box", "children"),
        [
            Input("cytoscape-graph", "tapNode"),
            Input("cytoscape-graph", "tapEdge"),
            Input("cytoscape-graph", "tapBlank"),
            Input({'type': 'set-sink-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-sink-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-node-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-ctrl-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-edge-btn', 'index': ALL}, 'n_clicks'),
        ],
        [
            State("cytoscape-graph", "tapNode"),
            State("cytoscape-graph", "tapEdge"),
            State("graph-data", "data"),
            State("cytoscape-graph", "elements"),
        ],
        prevent_initial_call=True
    )
    def update_tooltip(_, _1, _2, _3, _4, _5, _6, _7, tapped_node, tapped_edge, graph_data, elements):
        if not ctx.triggered:
            return ""

        #set input 
        input = ctx.triggered[0]["prop_id"]
        base_prob = 1.0

        #tooltip styling for buttons
        btn_style = {
            "padding": "6px 10px", "margin-top": "6px", "font-size": "12px",
            "font-family": "Computer Modern, Georgia, serif", "border": "none",
            "border-radius": "3px", "cursor": "pointer", "width": "100%",
            "text-align": "center", "transition": "background-color 0.3s ease"
        }

        #specific styling for removing controls and edges
        remove_control_style = {**btn_style, "background-color": "#d9534f", "color": "white"}
        remove_edge_style = {**btn_style, "background-color": "#b52b27", "color": "white", "font-weight": "bold"}

        #when a node or button is clicked
        if tapped_node and (input.startswith("cytoscape-graph.tapNode") or 'sink-btn' in input or 'remove-node-btn' in input):
            #get node data
            node_id = tapped_node["data"]["id"]
            matched = next((n for n in G.nodes if str(n) == str(node_id)), None)

            if matched is None:
                return "Node not found."

            #get label, sle, aro, and ale (ROSI) input values
            label = node_id
            sle = node_data.get(matched, {}).get("SLE", "N/A")
            aro = node_data.get(matched, {}).get("ARO", "N/A")
            ale = round(sle * aro, 2) if isinstance(sle, (int, float)) and isinstance(aro, (int, float)) else "N/A"

            #get flow to node
            flow_details, total_flow = [], 0
            for el in elements:
                if el['data'].get('target') == node_id:
                    #get source and controls
                    source = el['data']['source']
                    controls = el['data'].get("controls", [])
                    #set flow = base probability
                    flow = base_prob
                    #for each control on the edge
                    for c in controls:
                        #multiply by probability reduction (1-control effectiveness) for edge
                        flow *= (1 - c.get("effectiveness", 0))
                    #add flow to total for node
                    total_flow += flow
                    flow_details.append(f"{source} -> {label} | Flow: {round(flow, 4)}")
            
            #return html div with node info SLE, ALE, flow by edges, flow total, and buttons
            return html.Div([
                html.Strong(f"{label} ({list(G.nodes).index(matched)})", style={"text-decoration": "underline", "font-size": "14px"}),
                html.Br(), f"SLE: {sle}", html.Br(), f"ARO: {aro}",
                html.Br(), f"ALE: {ale}", html.Br(),
                *[html.Div(f) for f in flow_details],
                html.Strong(f"-> Total Flow: {round(total_flow, 2)}"),
                #set sink/remove sink button
                html.Button(
                    "Remove as Sink" if str(node_id) in sink_nodes else "Set Sink",
                    id={'type': 'remove-sink-btn', 'index': str(node_id)} if str(node_id) in sink_nodes else {'type': 'set-sink-btn', 'index': str(node_id)},
                    n_clicks=0,
                    style={**remove_edge_style, "margin-top": "10px"}
                ),
                #remove node button
                html.Button(
                    "Remove Node",
                    id={'type': 'remove-node-btn', 'index': str(node_id)},
                    n_clicks=0,
                    style={**remove_edge_style, "margin-top": "10px"}
                )
            ], style={"padding": "5px", "font-size": "12px"})

        #if edge or remove control button hit
        if tapped_edge and (input.startswith("cytoscape-graph.tapEdge") or 'remove-ctrl-btn' in input):
            edge_id = tapped_edge["data"]["id"]
            controls = edge_controls.get(edge_id, [])
            metrics = graph_data.get("metric_data", {})
            blocks = []

            #loop through controls
            for c in controls:
                #get control name
                name = c["name"]
                #get rosi, shapley, and viability values
                ros = metrics.get(name, {}).get("rosi_score", "N/A")
                shp = metrics.get(name, {}).get("shapley_value", "N/A")
                via = metrics.get(name, {}).get("viability", "N/A")

                #round shapley and viability in case wasn't done before
                shp = round(shp, 3) if isinstance(shp, (int, float)) else shp
                via = round(via, 3) if isinstance(via, (int, float)) else via

                #display control information on edge tooltip box
                blocks.extend([
                    html.Div([
                        html.Strong(name, style={"text-decoration": "underline", "font-size": "14px"}), html.Br(),
                        f"Effectiveness: {c.get('effectiveness', 'N/A')}", html.Br(),
                        f"Direct Cost: {c.get('direct_cost', 'N/A')}", html.Br(),
                        f"Indirect Cost: {c.get('indirect_cost', 'N/A')}", html.Br(),
                        html.Strong(f"ROSI Score: {ros}%"), html.Br(),
                        html.Strong(f"Shapley Value: {shp}"), html.Br(),
                        html.Strong(f"Viability Score: {via}")
                    ]),
                    #remove button for control
                    html.Button( 
                        f"Remove {name}",
                        id={'type': 'remove-ctrl-btn', 'index': f"{edge_id}::{name}"},
                        n_clicks=0, style=remove_control_style
                    )
                ])
            #remove edge button on tooltip
            blocks.append(html.Button( 
                "Remove Edge", id={'type': 'remove-edge-btn', 'index': edge_id},
                n_clicks=0, style=remove_edge_style
            ))
            
            #return html div 
            return html.Div(blocks, style={"padding": "5px", "font-size": "12px"})