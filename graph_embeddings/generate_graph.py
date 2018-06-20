import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from nxviz.plots import CircosPlot
import numpy as np

lines_to_read = 100

def extract_connections(df, node):
    array = np.full((len(df.index.values), 2), node, dtype=int)
    array[:, 1] = np.array(df.index.values)
    return tuple(map(tuple, array))

#read data
df = pd.read_csv("vso-1.3m-pruned-strict.csv", delimiter="\t", header=None,  nrows=lines_to_read)
df.columns = ['verb', 'subject', 'object', 'score']
df = df.reset_index()

#init graph
G=nx.Graph()
edges = []

#add vertices
print("Adding vertices...")
for index, row in df.iterrows():
    G.add_node(index, verb=row['verb'], subject=row['subject'], object=row['object'])
print("Done")

#add edges
print("Adding edges...")
for node in G.nodes():
    print("Analyzing node: ", node)
    # verb-subject co-occurrences
    sub = df.loc[(df['verb'] == G.node[node]['verb']) & (df['subject'] == G.node[node]['subject'])]
    if len(sub.index) > 1:
        edges += extract_connections(sub, node)

    # subject-object co-occurrences
    sub = df.loc[(df['subject'] == G.node[node]['subject']) & (df['object'] == G.node[node]['object'])]
    if len(sub.index) > 1:
        edges += extract_connections(sub, node)
G.add_edges_from(edges)
print("Done")

# graph info
print ("nodes: ", G.number_of_nodes())
print ("edges: ", G.number_of_edges())

#save graph
nx.write_adjlist(G, "triframes.adjlist")

#plot graph
c = CircosPlot(G, node_labels=True)
c.draw()
plt.show()


