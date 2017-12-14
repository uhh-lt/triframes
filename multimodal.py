#!/usr/bin/env python

import argparse
from collections import defaultdict
from statistics import mean

import Pyro4
import networkx as nx

from chinese_whispers import chinese_whispers, WEIGHTING, aggregate_clusters
from roles import triples, similarity

parser = argparse.ArgumentParser()
parser.add_argument('--cw', choices=WEIGHTING.keys(), default='nolog')
parser.add_argument('--min-weight', type=float, default=-0.)
parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

spos, _ = triples(args.triples, min_weight=args.min_weight, build_index=False)

Pyro4.config.SERIALIZER = 'pickle'
w2v = Pyro4.Proxy(args.w2v)

G = nx.Graph(name='Multimodal')

G.add_nodes_from(spos)

sp_index, po_index, so_index = defaultdict(set), defaultdict(set), defaultdict(set)
sp_inverted, po_inverted, so_inverted = defaultdict(set), defaultdict(set), defaultdict(set)

for node in G:
    sp_index[node].add((node.subject, node.predicate))
    po_index[node].add((node.predicate, node.object))
    so_index[node].add((node.subject, node.object))

    sp_inverted[(node.subject, node.predicate)].add(node)
    po_inverted[(node.predicate, node.object)].add(node)
    so_inverted[(node.subject, node.object)].add(node)

for node in G:
    this = {node}

    G.add_edges_from((node, neighbor) for pair in sp_index[node] - this for neighbor in sp_inverted[pair] if node != neighbor)
    G.add_edges_from((node, neighbor) for pair in po_index[node] - this for neighbor in po_inverted[pair] if node != neighbor)
    G.add_edges_from((node, neighbor) for pair in so_index[node] - this for neighbor in so_inverted[pair] if node != neighbor)

for source, target in G.edges_iter():
    G.edge[source][target]['weight'] = mean((
        similarity(w2v, source.subject, target.subject),
        similarity(w2v, source.predicate, target.predicate),
        similarity(w2v, source.object, target.object)
    ))

chinese_whispers(G, WEIGHTING[args.cw])

for label, cluster in sorted(aggregate_clusters(G).items(), key=lambda e: len(e[1]), reverse=True):
    print('# Cluster %d' % label)
    print()

    for triple in cluster:
        print('%s\t%s\t%s' % (triple.subject, triple.predicate, triple.object))

    print()
