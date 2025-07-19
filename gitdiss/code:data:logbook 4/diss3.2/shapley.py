#imports
from paths import path_prob
import random
from collections import defaultdict

#calculate total breach probability from set of active controls in subset, helper function
def total_prob(active_controls, nodes, edges, base_line_prob, control_on_edges, effectiveness):
    #filter controls to include only ones on each edge
    controls = {
        edge: [c for c in control_on_edges.get(edge, []) if c in active_controls]
        for edge in control_on_edges
    }

    #calc shortest path probabilities based on active controls for each node
    reachability = path_prob(nodes, edges, base_line_prob, controls, effectiveness)

    #breach probability of network = sum of all node shortest path probabilities
    return sum(info["prob"] for info in reachability.values())

def calc_shap(all_controls, nodes, edges, base_line_prob,control_on_edges, effectiveness, samples=1000, seed=1):
    #seed random. call
    random.seed(seed)
    #intialise shap vals
    shap_vals = defaultdict(float)

    #get list of controls
    controls_list = list(all_controls)
    #length of controls list
    n = len(controls_list)

    #if the length is 0 return empty dict
    if n == 0:
        return {}

    #moonte carlo sampling through samples
    for _ in range(samples):
        perm = random.sample(controls_list, len(controls_list))
        active_set = set()

        #previous and current probabilities for marginal gain
        prev_prob = total_prob(active_set, nodes, edges, base_line_prob, control_on_edges, effectiveness)

        #for each control in permutation
        for ctrl in perm:
            #add control to current coalition
            active_set.add(ctrl)

            #get edge probability
            new_prob = total_prob(active_set, nodes, edges, base_line_prob, control_on_edges, effectiveness)

            #get marginal contribution
            marginal_contribution = prev_prob - new_prob
            shap_vals[ctrl] += marginal_contribution
            prev_prob = new_prob

    #average shapley by number of samples
    for ctrl in shap_vals:
        shap_vals[ctrl] /= samples

    #check output
    baseline = total_prob(set(), nodes, edges, base_line_prob, control_on_edges, effectiveness)
    full_control = total_prob(set(all_controls), nodes, edges, base_line_prob, control_on_edges, effectiveness)
    total_reduction = baseline - full_control
    shapley_sum = sum(shap_vals.values())

    #debugging
    print("\nshapley:")
    print(f"total breach prob (no controls): {baseline:.6f}")
    print(f"total breach prob (all controls): {full_control:.6f}")
    print(f"expected risk reduction: {total_reduction:.6f}")
    print(f"sum of values: {shapley_sum:.6f}")
    print(f"difference: {abs(total_reduction - shapley_sum):.6f}")

    #return shap values as dictionary
    return dict(shap_vals)