import networkx as nx
import matplotlib.pyplot as plt

# Redefine the nodes and edges with shapes for routers and hosts, and correct the connection for Router_Layer2
G = nx.DiGraph()

# Define the nodes with shapes
nodes_with_shapes = {
    "DMZ_Segment": {"label": "192.168.1.0/24", "shape": "diamond"},
    "DMZ_Host": {"label": "192.168.1.1", "shape": "hexagon"},
    "Internal1_Segment1": {"label": "192.168.2.0/24", "shape": "diamond"},
    "Internal1_Host1_1": {"label": "192.168.2.1", "shape": "hexagon"},
    "Internal1_Host1_2": {"label": "192.168.2.2", "shape": "hexagon"},
    "Internal1_Host1_3": {"label": "192.168.2.3", "shape": "hexagon"},
    "Internal1_Segment2": {"label": "192.168.3.0/24", "shape": "diamond"},
    "Internal1_Host2_1": {"label": "192.168.3.1", "shape": "hexagon"},
    "Internal1_Host2_2": {"label": "192.168.3.2", "shape": "hexagon"},
    "Internal1_Host2_3": {"label": "192.168.3.3", "shape": "hexagon"},
    "Internal1_Host2_4": {"label": "192.168.3.4", "shape": "hexagon"},
    "Internal2_Segment": {"label": "172.16.101.0/24", "shape": "diamond"},
    "Internal2_Host1": {"label": "172.16.101.1", "shape": "hexagon"},
    "Internal2_Host2": {"label": "172.16.101.2", "shape": "hexagon"},
    "Internal2_Host3": {"label": "172.16.101.3", "shape": "hexagon"},
    "Internal_Layer2_Segment": {"label": "192.168.4.0/24", "shape": "diamond"},
    "Internal_Layer2_Host1": {"label": "192.168.4.1", "shape": "hexagon"},
    "Internal_Layer2_Host2": {"label": "192.168.4.2", "shape": "hexagon"},
    "Internal1_Segment": {"label": "172.16.100.0/24", "shape": "diamond"},
    "Internal1_Host3_1": {"label": "172.16.100.1", "shape": "hexagon"},
    "Internal1_Host3_2": {"label": "172.16.100.2", "shape": "hexagon"},
    "Router_DMZ": {"label": "Router_DMZ", "shape": "circle"},
    "Router_Layer1": {"label": "Router_Layer1", "shape": "circle"},
    "Router_Layer2": {"label": "Router_Layer2", "shape": "circle"},
    "Router_Internal1": {"label": "Router_Internal1", "shape": "circle"},
    "Router_Internal2": {"label": "Router_Internal2", "shape": "circle"},
}

edges = [
    ("Router_DMZ", "DMZ_Segment"),
    ("DMZ_Segment", "DMZ_Host"),
    ("Router_DMZ", "Router_Layer1"),
    ("Router_DMZ", "Router_Internal1"),
    ("Router_DMZ", "Router_Internal2"),
    ("Router_Layer1", "Internal1_Segment1"),
    ("Internal1_Segment1", "Internal1_Host1_1"),
    ("Internal1_Segment1", "Internal1_Host1_2"),
    ("Internal1_Segment1", "Internal1_Host1_3"),
    ("Router_Layer1", "Internal1_Segment2"),
    ("Internal1_Segment2", "Internal1_Host2_1"),
    ("Internal1_Segment2", "Internal1_Host2_2"),
    ("Internal1_Segment2", "Internal1_Host2_3"),
    ("Internal1_Segment2", "Internal1_Host2_4"),
    ("Router_Layer2", "Internal1_Segment2"),
    ("Router_Layer2", "Internal_Layer2_Segment"),
    ("Internal_Layer2_Segment", "Internal_Layer2_Host1"),
    ("Internal_Layer2_Segment", "Internal_Layer2_Host2"),
    ("Router_Internal1", "Internal1_Segment"),
    ("Internal1_Segment", "Internal1_Host3_1"),
    ("Internal1_Segment", "Internal1_Host3_2"),
    ("Router_Internal2", "Internal2_Segment"),
    ("Internal2_Segment", "Internal2_Host1"),
    ("Internal2_Segment", "Internal2_Host2"),
    ("Internal2_Segment", "Internal2_Host3"),
]

# Add nodes and edges to the graph
for node, data in nodes_with_shapes.items():
    G.add_node(node, label=data["label"], shape=data["shape"])

for edge in edges:
    G.add_edge(edge[0], edge[1])

# Define positions for the nodes
pos = {
    "Router_DMZ": (0, 0),
    "DMZ_Segment": (0, 2),
    "DMZ_Host": (0, 4),
    "Router_Layer1": (5, 0),
    "Internal1_Segment1": (5, 2),
    "Internal1_Host1_1": (4, 4),
    "Internal1_Host1_2": (5, 5),
    "Internal1_Host1_3": (6, 4),
    "Internal1_Segment2": (10, 2),
    "Internal1_Host2_1": (9, 4),
    "Internal1_Host2_2": (10, 5),
    "Internal1_Host2_3": (11, 4),
    "Internal1_Host2_4": (12, 5),
    "Router_Layer2": (8, 0),
    "Internal_Layer2_Segment": (10, -2),
    "Internal_Layer2_Host1": (9, -4),
    "Internal_Layer2_Host2": (11, -4),
    "Router_Internal1": (-5, -5),
    "Internal1_Segment": (-5, -8),
    "Internal1_Host3_1": (-6, -10),
    "Internal1_Host3_2": (-4, -10),
    "Router_Internal2": (5, -5),
    "Internal2_Segment": (5, -8),
    "Internal2_Host1": (4, -10),
    "Internal2_Host2": (6, -10),
    "Internal2_Host3": (8, -10),
}

# Draw the graph with adjusted positions to avoid overlaps and crossings
plt.figure(figsize=(22, 18))

# Draw nodes with specific shapes
for node in G.nodes:
    shape = G.nodes[node]['shape']
    nx.draw_networkx_nodes(
        G, pos, nodelist=[node], node_shape='o' if shape == 'circle' else 'h' if shape == 'hexagon' else 'd',
        node_size=3000, node_color='skyblue'
    )

# Draw edges
nx.draw_networkx_edges(G, pos, arrows=True)

# Add labels to nodes
labels = nx.get_node_attributes(G, 'label')
nx.draw_networkx_labels(G, pos, labels, font_size=10, verticalalignment='center', horizontalalignment='center')

plt.title("Network Topology")
plt.show()