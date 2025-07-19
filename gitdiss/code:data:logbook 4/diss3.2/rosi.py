#import path computation
from paths import path_prob

#helper function calculate annual loss expectancy
def calc_ale(node_data, path_probs):
    #initialise ale to 0
    ale = 0
    #for all nodes in path probability calculation
    for id, info in path_probs.items():
        #get data, including sle, aro, and probability per node
        node_params = node_data.get(id, {})
        sle = node_params.get("SLE", node_params.get("sle", 0))
        aro = node_params.get("ARO", node_params.get("aro", 0))
        prob = info.get("prob", 0)
        #ALE eq, ALE = SLE * ARO * PROB for each node
        ale += sle * aro * prob
    
    #return ale for node
    return ale

#calculate rosi, main function
def calc_rosi(nodes, edges, base_line_prob, control_on_edges, effectiveness, cost, ind_cost, node_data):
    #calc ALEafter with all controls applied
    after_probs = path_prob(nodes, edges, base_line_prob, control_on_edges, effectiveness)
    ale_after = calc_ale(node_data, after_probs)

    #initialise rosi scores as empty dict
    rosi_scores = {}

    #for each control
    for control in effectiveness:
        #remove control from the network
        #modified control set absent of control
        modified_controls = {
            edge: [c for c in ctrls if c != control]
            for edge, ctrls in control_on_edges.items()
        }

        #recalc path probs without control ALE before
        before_probs = path_prob(nodes, edges, base_line_prob, modified_controls, effectiveness)
        ale_before = calc_ale(node_data, before_probs)

        #calc control implementation cost by usage across edges
        usage = sum(1 for ctrls in control_on_edges.values() if control in ctrls)
        #get direct, indirect, and total cost
        dcost = cost.get(control, 0)
        idcost = ind_cost.get(control, 0)
        #usage * direct and indirect cost = total
        total = usage * (dcost + idcost)

        #debugging
        print(ale_before)
        print(f"{control}: {ale_after}")

        #calc ROSI from equation
        #if total cost is greater than 0 to prevent division error
        if total > 0:
            #rosi eq, rosi = (ALEb - aleA - Costj / Costj
            rosi = (ale_before - ale_after - total) / total
        else:
            #blank rosi, preset to neutral 0
            rosi = 0

        #set rosi score for selected control
        rosi_scores[control] = rosi

    #return rosi scores
    return rosi_scores