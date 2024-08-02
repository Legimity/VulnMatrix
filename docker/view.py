import networkx as nx
import matplotlib.pyplot as plt

# Redefine the nodes and edges with shapes for routers and hosts, and correct the connection for Router_Layer2
G = nx.DiGraph()

# Define the nodes with shapes
nodes_with_shapes = {
    "dmz_router": {"label": "Router_DMZ", "shape": "circle"},
    "office_router": {"label": "Router_Office", "shape": "circle"},
    "dev_router": {"label": "Router_Dev", "shape": "circle"},
    "dmz_switch": {"label": "Switch_DMZ", "shape": "diamond"},
    "office_switch": {"label": "Switch_Office", "shape": "diamond"},
    "dev_switch": {"label": "Switch_Dev", "shape": "diamond"},
    "website": {"label": "Website", "shape": "hexagon"},
    "dmz_db": {"label": "DMZ_DB", "shape": "hexagon"},
    "mail_server": {"label": "Mail_Server", "shape": "hexagon"},
    "office_pc1": {"label": "Office_PC1", "shape": "hexagon"},
    "office_pc2": {"label": "Office_PC2", "shape": "hexagon"},
    "code_repo": {"label": "Code_Repo", "shape": "hexagon"},
    "dev_db": {"label": "Dev_DB", "shape": "hexagon"},
    "test_machine": {"label": "Test_Machine", "shape": "hexagon"},
}

edges = [
    ("dmz_router", "dmz_switch"),
    ("dmz_switch", "website"),
    ("dmz_switch", "dmz_db"),
    ("dmz_switch", "mail_server"),
    ("office_router", "office_switch"),
    ("office_switch", "office_pc1"),
    ("office_switch", "office_pc2"),
    ("dev_router", "dev_switch"),
    ("dev_switch", "code_repo"),
    ("dev_switch", "dev_db"),
    ("dev_switch", "test_machine"),
]

# Add nodes and edges to the graph
for node, data in nodes_with_shapes.items():
    G.add_node(node, label=data["label"], shape=data["shape"])

for edge in edges:
    G.add_edge(edge[0], edge[1])

# Define positions for the nodes
pos = {
    "dmz_router": (0, 0),
    "dmz_switch": (0, 2),
    "website": (-1, 4),
    "dmz_db": (0, 4),
    "mail_server": (1, 4),
    "office_router": (5, 0),
    "office_switch": (5, 2),
    "office_pc1": (4, 4),
    "office_pc2": (6, 4),
    "dev_router": (10, 0),
    "dev_switch": (10, 2),
    "code_repo": (9, 4),
    "dev_db": (10, 4),
    "test_machine": (11, 4),
}

# Draw the graph with adjusted positions to avoid overlaps and crossings
plt.figure(figsize=(10, 8))

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