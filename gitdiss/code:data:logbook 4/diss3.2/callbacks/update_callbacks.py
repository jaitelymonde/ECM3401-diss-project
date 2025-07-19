#imports
from dash import Input, Output, State, ctx, ALL, html, dcc
import json, base64
from dash.exceptions import PreventUpdate
from logic.graph_utils import generate_cytoscape_elements, generate_stylesheet
from logic.data_store import G, sink_nodes, edge_controls, node_positions, node_data

def register_callbacks(app):

    #main graph interaction callback for attaxk graph construction
    @app.callback(
        [
            Output('cytoscape-graph', 'elements'),
            Output('cytoscape-graph', 'stylesheet'),
            Output('output-msg', 'children'),
            Output('edge-dropdown', 'options'),
            Output('upload-feedback', 'children'),
        ],
        [
            Input({'type': 'remove-edge-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-ctrl-btn', 'index': ALL}, 'n_clicks'),
            Input('add-node-btn', 'n_clicks'),
            Input({'type': 'remove-node-btn', 'index': ALL}, 'n_clicks'),
            Input('add-edge-btn', 'n_clicks'),
            Input('add-ctrl-btn', 'n_clicks'),
            Input({'type': 'set-sink-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-sink-btn', 'index': ALL}, 'n_clicks'),
            Input('reset-btn', 'n_clicks'),
            Input('upload-json', 'contents')
        ],
        [
            State('node-name', 'value'),
            State('single-loss', 'value'),
            State('occurance-rate', 'value'),
            State('node1', 'value'),
            State('node2', 'value'),
            State('edge-dropdown', 'value'),
            State('control-name', 'value'),
            State('effectiveness', 'value'),
            State('direct-cost', 'value'),
            State('indirect-cost', 'value'),
            State('cytoscape-graph', 'elements'),
            State('upload-json', 'filename')
        ]
    )
    def update_graph(_0, _1, add_node, rm_node, add_edge, add_ctrl, set_sink, rm_sink, reset, upload,
                     name, sle, aro, n1, n2, selected_edge, ctrl_name, eff, dcost, icost, els, fname):

        #initialise message string and set ctx trigger input
        feedback = ""
        input = ctx.triggered_id

        #conserve node position during construction
        if els:
            for el in els:
                if 'position' in el:
                    node_positions[el['data']['id']] = el['position']

        #load graph from uploading json file
        if input == 'upload-json' and upload:
            try:
                _, content_string = upload.split(',')
                data = json.loads(base64.b64decode(content_string))
                G.clear(); sink_nodes.clear(); edge_controls.clear(); node_positions.clear(); node_data.clear()

                #retrieve nodes, data (sle, aro, flow), and positions
                for n in data.get("nodes", []):
                    G.add_node(n["id"])
                    node_data[n["id"]] = n.get("data", {})
                    node_positions[n["id"]] = n.get("position", {"x": 0, "y": 0})

                #get edges and controls
                #loop through edges
                for e in data.get("edges", []):
                    #add edge to graph G
                    G.add_edge(e["source"], e["target"], key=e.get("key", 0))
                    #add edge controls to graph G
                    edge_controls[f"{e['source']}-{e['target']}-{e.get('key', 0)}"] = e.get("controls", [])

                #set sink nodes
                sink_nodes.update(str(s) for s in data.get("sinks", []))
                #show loaded name
                feedback = f"loaded: '{fname}'"
            #failure to load graph
            except Exception as e:
                feedback = f"failed to load: {str(e)}"

        #if remove edge is hit (tooltip button)
        elif isinstance(input, dict) and input.get("type") == "remove-edge-btn":
            #ensure only on button click
            if ctx.triggered[0]['value'] > 0:
                try:
                    #split edge key
                    edge_id = input['index']
                    u, v, k = edge_id.split('-')
                    u, v, k = str(u), str(v), int(k)
                    #if G has the edge
                    if G.has_edge(u, v, key=k):
                        #remove edge from G and remove controls on edge
                        G.remove_edge(u, v, key=k)
                        edge_controls.pop(f"{u}-{v}-{k}", None)
                #failed to remove edge exception
                except Exception as e:
                    print("failed to remove edge:", e)

        #tooltip remove control button (tooltip button)
        elif isinstance(input, dict) and input.get("type") == "remove-ctrl-btn":
            #double check to prevent bug and click intentional
            if ctx.triggered[0]['value'] > 0:
                try:
                    combo = input['index']
                    edge_id, control_name = combo.split("::")
                    #check for edge id in edge controls
                    if edge_id in edge_controls:
                        #delete control by edge control id
                        edge_controls[edge_id] = [c for c in edge_controls[edge_id] if c["name"] != control_name]
                        if not edge_controls[edge_id]:
                            del edge_controls[edge_id]
                except Exception as e:
                    print("failed to remove control:", e)

        #if add node button is hit and the name is not already in the graph
        elif input == 'add-node-btn' and name and name not in G:
            #add node to G
            G.add_node(name)
            #set node position
            node_positions[name] = {"x": len(G)*50, "y": len(G)*50}
            #set node name
            node_data[name] = {"SLE": sle or 0, "ARO": aro or 0}

        #if remove node button is hit (tooltip button)
        elif isinstance(input, dict) and input.get("type") == "remove-node-btn":
            #ensure button clicks exceed 0
            if ctx.triggered[0]["value"] > 0:
                try:
                    #get node id
                    node_id = input["index"]
                    #check its in G
                    if node_id in G:
                        #remove node id from G
                        G.remove_node(node_id)
                        #discard sink nodes, and node positions
                        sink_nodes.discard(node_id)
                        node_positions.pop(node_id, None)
                        #remove controls
                        keys = [k for k in edge_controls if node_id in k]
                        for k in keys:
                            edge_controls.pop(k)
                #failure to remove exception
                except Exception as e:
                    print("failed to remove node:", e)

        #add edge button is hit
        elif input == 'add-edge-btn' and n1 and n2:
            #format keys
            u, v = str(n1).strip(), str(n2).strip()
            #if u and v are in G
            if u in G and v in G:
                #set k (key for multiple edges between nodes)
                k = max(G.get_edge_data(u, v, default={}).keys(), default=-1) + 1
                #add edge to G
                G.add_edge(u, v, key=k)
                #intialise control list for edge
                edge_controls[f"{u}-{v}-{k}"] = []

        #if add contrl button is hit
        elif input == 'add-ctrl-btn' and selected_edge and ctrl_name:
            try:
                #split edge keys
                u, v, k = selected_edge.split('-')
                eid = f"{u}-{v}-{k}"
                edge_controls.setdefault(eid, [])
                #if theres no control with same name in edge controls
                if not any(c['name'] == ctrl_name for c in edge_controls[eid]):
                    #add control by id
                    edge_controls[eid].append({
                        "name": ctrl_name,
                        "effectiveness": eff or 0,
                        "direct_cost": dcost or 0,
                        "indirect_cost": icost or 0
                    })
            except: pass

        #if set sink button is hit (tooltip button)
        elif isinstance(input, dict) and input.get("type") == "set-sink-btn":
            #double check to prevent bug and click intentional
            if ctx.triggered[0]['value'] > 0:
                try:
                    #set sink id
                    sink_id = input['index']
                    #add sink to nodes by id
                    sink_nodes.add(sink_id)
                except Exception as e:
                    print("failed to set sink:", e)

        #if remove sink button is hit (tooltip button)
        elif isinstance(input, dict) and input.get("type") == "remove-sink-btn":
            #double check to prevent bug and click intentional
            if ctx.triggered[0]['value'] > 0:
                try:
                    #get sink id
                    sink_id = input['index']
                    #discard sink id from sink nodes
                    sink_nodes.discard(sink_id)
                except Exception as e:
                    print("failed to remove sink:", e)

        #reset graph button hit
        elif input == 'reset-btn':
            #clear G and all associated components in case
            G.clear(); sink_nodes.clear(); edge_controls.clear(); node_positions.clear(); node_data.clear()

        #edge dropdown menu for adding control
        edge_opts = [
            {"label": f"{u} → {v} (Path {k})",
            "value": f"{u}-{v}-{k}"}
            for u, v, k in G.edges(keys=True)
        ]


        return generate_cytoscape_elements(), generate_stylesheet(), "", edge_opts, feedback

    #save graph as json file callback
    @app.callback(
        Output("download-graph-json", "data"),
        Input("save-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def save_graph(_):
        #get data and format
        data = {
            "nodes": [
                {"id": str(n), "data": node_data.get(n, {}), "position": node_positions.get(n, {"x": 0, "y": 0})}
                for n in G.nodes
            ],
            "edges": [
                {"source": u, "target": v, "key": k, "controls": edge_controls.get(f"{u}-{v}-{k}", [])}
                for u, v, k in G.edges(keys=True)
            ],
            "sinks": list(sink_nodes)
        }
        #return exported graph as json file containing graph G data
        return dcc.send_string(json.dumps(data, indent=4), filename="exported_graph.json")