#imports
import math
from pulp import *

#optimisation solver from khouzani, refactored for multi edge key formatting across model files
def optimisation_solver(nodes, SINK_NODES, edges, controls, control_on_edges, base_line_prob, cost, ind_cost, effectiveness, B=2, IB=2):
    #defines tiny epsilon value to prioritise cheaper controls
    esp = 1e-8

    #create lp problem for minimisation of objective function
    model = LpProblem("multi_edge_optimisation", sense=LpMinimize)

    #binary decision variable for output set
    x = LpVariable.dicts("x", controls, lowBound=0, upBound=1, cat="Binary")

    #continous var for log risk at nodes
    lamb = LpVariable.dicts("lamb", nodes)

    #objective khouzani attack probability minimisation function 
    model += lpSum(lamb[0] - lamb[s] for s in SINK_NODES) + esp * lpSum(cost[c] * x[c] for c in controls)

    #for each edge
    for u, v, k in edges:
        #set edge key
        edge_key = (u, v, k)
        #get the log transformed probability from baseline slider input
        log_prob = math.log(base_line_prob.get(edge_key))
        #add to model using khouzani edge constraint equation
        model += (lamb[u] - lamb[v] >= log_prob + lpSum(x[c] * math.log(effectiveness[c]) for c in control_on_edges.get(edge_key, [])))
    
    #direct and indirect budget constraints add to model
    model += lpSum(cost[c] * x[c] for c in controls) <= B
    model += lpSum(ind_cost[c] * x[c] for c in controls) <= IB
    
    #for each control
    for c in controls:
        #check for duplicate controls
        if any(c2[0] == c[0] and c2 != c for c2 in controls):
            #prevent use of multiple controls
            model += lpSum(x[c2] for c2 in controls if c2[0] == c[0]) <= 1

    #solve the model
    model.solve(PULP_CBC_CMD(msg=False))
    
    #get risk
    risk = math.exp(model.objective.value())
    selected_controls = [c for c in controls if x[c].varValue >= 0.5]

    #return the risk, and the selected controls
    return risk, selected_controls