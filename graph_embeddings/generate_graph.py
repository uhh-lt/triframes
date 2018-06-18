import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from nxviz.plots import CircosPlot

lines_to_read = 55

#read data
df = pd.read_csv("vso-1.3m-pruned-strict.csv", delimiter="\t", header=None,  nrows=lines_to_read)
df.columns = ['verb', 'subject', 'object', 'score']

#init graph
G=nx.Graph()
vertices = []
edges = []

#add vertices
for index, row in df.iterrows():
    G.add_node(index, verb=row['verb'], subject=row['subject'], object=row['object'])

#add edges
for node in G.nodes():
    # verb-subject co-occurrences
    sub = df.loc[(df['verb'] == G.node[node]['verb']) & (df['subject'] == G.node[node]['subject'])]
    for index, row in sub.iterrows():
        if (index != node):
            edges.append((node, index))

    #subject-object co-occurrences
    sub = df.loc[(df['subject'] == G.node[node]['subject']) & (df['object'] == G.node[node]['object'])]
    for index, row in sub.iterrows():
        if (index != node):
            edges.append((node, index))

G.add_edges_from(edges)

# graph info
print ("nodes: ", G.number_of_nodes())
print ("edges: ", G.number_of_edges())

#save graph
nx.write_adjlist(G, "triframes.adjlist")

#plot graph
c = CircosPlot(G, node_labels=True)
c.draw()
plt.show()

