#imports
from dash import callback, Input, Output, State, html, ALL, ctx
import time
from logic.data_store import sink_nodes, node_data
from optimise import optimisation_solver
from rosi import calc_rosi
from shapley import calc_shap
from viability import calc_viability
from paths import path_prob

def register_callbacks(app):

    #calculation callback to store all computed data: ROSI, Shapley, optimiser, viability to be passed to display callbacks
    @callback(
            Output('graph-data', 'data'),
            Input('run-btn', 'n_clicks'),
        [
            State('cytoscape-graph', 'elements'),
            State('direct-budget', 'value'),
            State('indirect-budget', 'value'),
            State('baseline-prob-slider', 'value')
        ],
        prevent_initial_call=True
    )
    def store_graph_data(_, elements, direct_budget, indirect_budget, slider_val):
        #if no elements in the graph
        if not elements:
            return {"message": "no elements in graph"}

        #initialise time
        t0 = time.time()

        #intialise data structures for nodes, sinks, edges, controls
        node_map = {el['data']['id']: idx for idx, el in enumerate(elements) if 'source' not in el['data']}
        nodes = list(node_map.values())
        sinks = sorted([node_map[n] for n in sink_nodes if n in node_map])
        edges, control_on_edges, controls = [], {}, set()
        effectiveness, cost, ind_cost = {}, {}, {}

        #for each element in the graph
        for el in elements:
            if 'source' in el['data']:
                #map edge keys and append to edges
                u, v = node_map[el['data']['source']], node_map[el['data']['target']]
                key = len([e for e in edges if e[0] == u and e[1] == v])
                edge = (u, v, key)
                edges.append(edge)

                #organize control data from current edge, store into data structures
                ct = []
                for ctrl in el['data'].get('controls', []):
                    c = (ctrl['name'], 1)
                    controls.add(c)
                    ct.append(c)
                    effectiveness[c] = ctrl.get("effectiveness", 0)
                    cost[c] = ctrl.get("direct_cost", 0)
                    ind_cost[c] = ctrl.get("indirect_cost", 0)

                control_on_edges[edge] = ct

        #set base edge probabilities across all edges to slider input value
        base_prob = {(u, v, k): slider_val or 1.0 for (u, v, k) in edges}
        #get single loss expectancy of all nodes
        sle_data = {node_map[str(k)]: v for k, v in node_data.items() if str(k) in node_map}

        #run rosi and shapley functions with input parameters
        rosi = calc_rosi(nodes, edges, base_prob, control_on_edges, effectiveness, cost, ind_cost, sle_data)
        shapley = calc_shap(controls, nodes, edges, base_prob, control_on_edges, effectiveness)

        #organise metrics
        metrics = {
            c[0]: {
                "rosi_score": round(rosi.get(c, 0) * 100),
                "shapley_value": shapley.get(c, 0)
            } for c in controls
        }

        #get risk and selected controls from optimisation solver function
        risk, selected = optimisation_solver(nodes, sinks, edges, controls, control_on_edges, base_prob, cost, ind_cost, effectiveness,B=direct_budget or 0, IB=indirect_budget or 0)

        #get viability score from viability function
        viability = calc_viability(
            rosi_scores={c[0]: rosi.get(c, 0) for c in controls},
            shapley_scores={c[0]: shapley.get(c, 0) for c in controls},
            optimiser_selected_controls={(c[0], 1) for c in selected}
        )
        
        #for each name and score in viability metrics
        for name, score in viability.items():
            #round score to 3 decimal places
            if name in metrics:
                metrics[name]["viability"] = round(score, 3)

        #get edge probability from shortest path calculation
        reachability = path_prob(nodes, edges, base_prob, control_on_edges, effectiveness)

        #runtime print
        print(f"runtime: {time.time() - t0:.2f}s")

        #return all data with metrics, optimal solutions, controls
        return {
            "metric_data": metrics,
            "optimal_solution": {
                "risk": round(risk, 3),
                "control_list": selected
            },
            "node_index_to_name": node_map,
            "reachability_result": reachability
        }

    #callback to display optimal solution box from stored graph data
    @callback(
        Output('graph-output', 'children'),
        [Input('graph-data', 'data'), Input('reset-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def display_graph_data(data, reset_clicks):
        #reset box
        if ctx.triggered_id == 'reset-btn':
            return ""
        #if theres no solution in the data, return message
        if not data or "optimal_solution" not in data:
            return "no solution data"

        #get risk and control set from optimal solution data
        risk = data["optimal_solution"]["risk"]
        controls = ", ".join(f"({c[0]}, {c[1]})" for c in data["optimal_solution"]["control_list"])

        #return html div to display
        return html.Div([
            html.Strong("Optimal Solution:"),
            html.Div(f"Risk of Attack: {risk}", style={'margin-top': '10px'}),
            html.Div("Selected Controls:"),
            html.Div(controls)
        ])

    #callback to display shortest path for all nodes (highest probability for attacker) from stored graph data
    @callback(
        Output('path-output', 'children'),
        [Input('graph-data', 'data'), Input('reset-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def display_path_data(data, reset_clicks):
        
        #reset sp box
        if ctx.triggered_id == 'reset-btn':
            return ""

        #if no path result in data, return message
        if not data or "reachability_result" not in data:
            return "no path data"

        #set results to output from data
        result = data["reachability_result"]
        mapping = data["node_index_to_name"]

        #initialise html div 
        out = []
        #for each node id and info in result
        for nid, info in result.items():
            #set id, and 
            name = next((k for k, v in mapping.items() if v == nid), f"Node {nid}")
            out.append(html.Strong(f"{name}:"))
            out.append(html.Div(f"Reachability: {info['prob']}"))

            #if information has shortest path data
            if info.get("shortest_path"):
                #format shortest paths with nodes, append to output
                path = [next((k for k, v in mapping.items() if v == i), str(i)) for i in info["shortest_path"]]
                out.append(html.Div(f"Shortest Path: {' → '.join(path)}"))

        #return the html div of nodes and shortest paths output
        return html.Div(out)


    #callback to set the baseline probability from input slider
    @callback(
        Output('baseline-prob-store', 'data'),
        Input('baseline-prob-slider', 'value')
    )
    def update_baseline_prob(val):
        #set value to baseline slider val
        return {'value': val}