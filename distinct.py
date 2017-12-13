#!/usr/bin/env python

import argparse
from collections import defaultdict
from operator import itemgetter

import Pyro4
import networkx as nx

from chinese_whispers import WEIGHTING, chinese_whispers
from roles import triples

Pyro4.config.SERIALIZER = 'pickle'

parser = argparse.ArgumentParser()
parser.add_argument('--cw', choices=WEIGHTING.keys(), default='nolog')
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

spos, _ = triples(args.triples, min_weight=args.min_weight, build_index=False)

w2v = Pyro4.Proxy(args.w2v)

G_s, G_p, G_o = nx.Graph(name='Subjects'), nx.Graph(name='Predicates'), nx.Graph(name='Objects')

sp_index, po_index, so_index = defaultdict(set), defaultdict(set), defaultdict(set)
sp_inverted, po_inverted, so_inverted = defaultdict(set), defaultdict(set), defaultdict(set)

for triple in spos:
    G_s.add_node(triple.subject, triple=triple)
    G_p.add_node(triple.predicate, triple=triple)
    G_o.add_node(triple.object, triple=triple)

    sp_index[triple].add((triple.subject, triple.predicate))
    po_index[triple].add((triple.predicate, triple.object))
    so_index[triple].add((triple.subject, triple.object))

    sp_inverted[(triple.subject, triple.predicate)].add(triple)
    po_inverted[(triple.predicate, triple.object)].add(triple)
    so_inverted[(triple.subject, triple.object)].add(triple)

def similarity(word1, word2, default=.3):
    try:
        return w2v.similarity(word1, word2)
    except KeyError:
        return default

for node in G_s:
    for feature in po_index[G_s.node[node]['triple']]:
        for triple in po_inverted[feature]:
            if triple.subject != node:
                G_s.add_edge(node, triple.subject, weight=similarity(node, triple.subject))

for node in G_p:
    for feature in so_index[G_p.node[node]['triple']]:
        for triple in so_inverted[feature]:
            if triple.predicate != node:
                G_p.add_edge(node, triple.predicate, weight=similarity(node, triple.predicate))

for node in G_o:
    for feature in sp_index[G_o.node[node]['triple']]:
        for triple in sp_inverted[feature]:
            if triple.object != node:
                G_o.add_edge(node, triple.object, weight=similarity(node, triple.object))

chinese_whispers(G_s, WEIGHTING['nolog'])
chinese_whispers(G_p, WEIGHTING['nolog'])
chinese_whispers(G_o, WEIGHTING['nolog'])

roles_s, roles_p, roles_o = defaultdict(set), defaultdict(set), defaultdict(set)

for node in G_s:
    roles_s[G_s.node[node]['label']].add(node)

for node in G_p:
    roles_p[G_p.node[node]['label']].add(node)

for node in G_o:
    roles_o[G_o.node[node]['label']].add(node)

for label, verbs in sorted(roles_p.items(), key=itemgetter(1), reverse=True):
    print('# Cluster %d' % label)
    print()

    print('Verbs: %s' % ', '.join(verbs))
    print()

    subjects = {G_p.node[verb]['triple'].subject for verb in verbs}
    subjects_clusters = {G_s.node[subject]['label'] for subject in subjects}

    for label in subjects_clusters:
        print('Role s%d: %s' % (label, ', '.join(roles_s[label])))
        print()

    objects = {G_p.node[verb]['triple'].object for verb in verbs}
    objects_clusters = {G_o.node[object]['label'] for object in objects}

    for label in objects_clusters:
        print('Role o%d: %s' % (label, ', '.join(roles_o[label])))
        print()
