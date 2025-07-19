#import network x for graph
import networkx as nx

#share variables across callbacks
G = nx.MultiDiGraph()
sink_nodes = set()
edge_controls = {}
node_positions = {}
node_data = {}