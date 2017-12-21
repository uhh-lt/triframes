#!/usr/bin/env python

import argparse
from collections import defaultdict
from itertools import combinations
from statistics import mean

import Pyro4
import networkx as nx

from roles import triples, similarity

parser = argparse.ArgumentParser()
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

for node in G:
    sp_index[(node.subject, node.predicate)].add(node)
    po_index[(node.predicate, node.object)].add(node)
    so_index[(node.subject, node.object)].add(node)

for index in (sp_index, po_index, so_index):
    for subset in index.values():
        for source, target in combinations(subset, 2):
            G.add_edge(source, target)

for source, target in G.edges_iter():
    weight = mean((
        similarity(w2v, source.subject, target.subject),
        similarity(w2v, source.predicate, target.predicate),
        similarity(w2v, source.object, target.object)
    ))

    source_str = '|'.join((source.subject, source.predicate, source.object))
    target_str = '|'.join((target.subject, target.predicate, target.object))

    print('%s\t%s\t%f' % (source_str, target_str, weight))
