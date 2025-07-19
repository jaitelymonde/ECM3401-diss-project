#imports
from dash import Input, Output, State, ctx, html, dcc, no_update
from dash.dependencies import ALL
import json, base64
from logic.data_store import edge_controls

#calculates total cost of control additions and adds to total box
def register_callbacks(app):
    @app.callback(
            Output("cost-box", "children"),
        [
            Input('add-ctrl-btn', 'n_clicks'),
            Input({'type': 'remove-ctrl-btn', 'index': ALL}, 'n_clicks'),
            Input({'type': 'remove-edge-btn', 'index': ALL}, 'n_clicks'),
            Input('reset-btn', 'n_clicks'),
            Input('upload-json', 'contents'),
        ],
        [
            State('edge-dropdown', 'value'),
            State('control-name', 'value'),
            State('effectiveness', 'value'),
            State('direct-cost', 'value'),
            State('indirect-cost', 'value'),
            State({'type': 'remove-ctrl-btn', 'index': ALL}, 'id'),
            State({'type': 'remove-edge-btn', 'index': ALL}, 'id'),
        ],
        prevent_initial_call=False
    )
    def update_total_cost(_, _1, _2, _3, upload_contents,selected_edge, control_name, effectiveness, direct_cost, indirect_cost, remove_control_ids, remove_edge_ids):
        #if no controls exist and no file is uploaded show zero
        if not edge_controls and not upload_contents:
            return calc_costs([])

        #set ctx trigger to identify inputs
        input = ctx.triggered_id

        #if reset button hit, clear all controls
        if input == 'reset-btn':
            edge_controls.clear()

        #emergency fallback
        #if add control button hit
        elif input == 'add-ctrl-btn':
            #if no edge or no name, do nothing
            if not selected_edge or not control_name:
                return no_update
            #make control if there isnt one
            edge_controls.setdefault(selected_edge, [])
            #check for duplicate and if control added to edge
            if not any(ctrl['name'] == control_name for ctrl in edge_controls[selected_edge]):
                #appends dictionary for edge controls with all information
                edge_controls[selected_edge].append({
                    "name": control_name,
                    "effectiveness": effectiveness or 0,
                    "direct_cost": direct_cost or 0,
                    "indirect_cost": indirect_cost or 0
                })

        #remove control is hit
        elif isinstance(input, dict) and input.get("type") == "remove-ctrl-btn":
            #loop throguh clicks and if clicked
            for i, clicks in enumerate(_1):
                if clicks:
                    #split edge id from control names
                    edge_id, ctrl_name = remove_control_ids[i]['index'].split("::")
                    #replaces the list of controls on edge with filtered list where matching control is removed
                    edge_controls[edge_id] = [c for c in edge_controls.get(edge_id, []) if c["name"] != ctrl_name]
                    if not edge_controls[edge_id]:
                        edge_controls.pop(edge_id)
                    break

        #remove edge is hit
        elif isinstance(input, dict) and input.get("type") == "remove-edge-btn":
            #loop through clicks and if clicked
            for i, clicks in enumerate(_2):
                if clicks:  
                    # get edge ID
                    edge_id = remove_edge_ids[i]['index']
                    #remove edge from edge_controls
                    edge_controls.pop(edge_id, None)
                    break  


        #if a json file is uploaded
        elif input == 'upload-json' and upload_contents:
            try:
                #split upload content
                _, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)
                data = json.loads(decoded)
                #render the cost box with uploaded data
                return calc_costs(data.get("edges", []))
            #exception
            except Exception as e:
                return html.Div([
                    html.Strong("upload failed to render cost:"),
                    html.Div(str(e), style={"color": "red"})
                ])

        #return costs from helper function
        return calc_costs()

    #helper function to calculate total costs
    def calc_costs(edges=None):
        #initialise direct and indirect costs
        total_dc, total_ic = 0, 0

        edge_source = edges if edges is not None else edge_controls.values()

        #loop through items
        for item in edge_source:
            #if item is list, use directly, if item is json dict get controls
            controls = item if isinstance(item, list) else item.get("controls", [])
            #for each control
            for ctrl in controls:
                #add the direct and indirect to total direct and indirect costs
                total_dc += ctrl.get("direct_cost", 0)
                total_ic += ctrl.get("indirect_cost", 0)

        #total costs = total direct + total indirect costs
        total = total_dc + total_ic

        #return html div with totals to output box
        return html.Div([
            html.Strong("Total Control Cost:", style={"margin-top": "-7px", "display": "block"}),
            html.Div(f"Direct: {total_dc:.2f}"),
            html.Div(f"Indirect: {total_ic:.2f}"),
            html.Div(f"Total: {total:.2f}", style={"font-weight": "bold"})
        ])