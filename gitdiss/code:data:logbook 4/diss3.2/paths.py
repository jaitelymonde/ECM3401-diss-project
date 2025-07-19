#imports
import math
import heapq
from collections import defaultdict

#shortest path computation in log space
def path_prob(nodes, edges, base_line_prob, control_on_edges, effectiveness):
    adj = defaultdict(list)
    #loop through edges
    for u, v, k in edges:
        #assign probabilities to all edges in network
        #get base line prob from edge
        base_prob = base_line_prob.get((u, v, k))
        eff_prob = base_prob
        #for each control, empty list if not
        for ctrl in control_on_edges.get((u, v, k), []):
            #get reduction probability frmo effectiveness of ctrl 1-effectiveness of control
            eff_prob *= (1 - effectiveness.get(ctrl, 0))
        if eff_prob > 0:
            #log-space weight
            adj[u].append((v, -math.log(eff_prob)))  

    #minimum risk log path to each node from any source
    min_log_risk = {n: float('inf') for n in nodes}
    best_path = {n: None for n in nodes}

    for source in nodes:
        #store log risk from source to node
        dist = {n: float('inf') for n in nodes}
        #store previous nodes on strongest papth
        prev = {n: None for n in nodes}
        #distance to self node is 0
        dist[source] = 0
        #prio queue
        heap = [(0, source)]

        #dijkstra
        while heap:
            cur_dist, u = heapq.heappop(heap)
            #for neighbor v
            for v, weight in adj[u]:
                alt = cur_dist + weight
                #total log risk to reach v from u
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))

        #loop through all nodes
        for target in nodes:
            if dist[target] < min_log_risk[target]:
                #self node
                if target == source:
                    #only allow node to path to itself if self-loop edge exists
                    has_self_loop = any(
                        edge[0] == target and edge[1] == target for edge in control_on_edges
                    )
                    if not has_self_loop:
                        continue
                
                #best path
                min_log_risk[target] = dist[target]

                #initialise stored lists for shortest paths
                path = []
                #start from target node
                curr = target
                #backtrack to source node
                while curr is not None:
                    path.append(curr)
                    curr = prev[curr]
                #store best path to target
                best_path[target] = list(reversed(path))

    #results
    sp_data = {}
    #loop through nodes
    for node in nodes:
        #if node can be reached
        if min_log_risk[node] < float('inf'):
            #convert the log space result to probability: exp(-distance)
            prob = math.exp(-min_log_risk[node])
            sp_data[node] = {
                "prob": round(prob, 5),
                "shortest_path": best_path[node]
            }
        #else return empty dataset
        else:
            sp_data[node] = {
                "prob": 0.0,
                "shortest_path": None
            }

    #return probabilities
    return sp_data