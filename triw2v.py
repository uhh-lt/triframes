#!/usr/bin/env python

import argparse
from collections import Counter
from itertools import zip_longest

import faiss
import networkx as nx
import numpy as np
from chinese_whispers import chinese_whispers, aggregate_clusters

from roles import triples

STOP = {'i', 'he', 'she', 'it', 'they', 'you', 'this', 'we', 'them', 'their', 'us', 'my', 'those', 'who', 'what',
        'that', 'which', 'each', 'some', 'me', 'one', 'the'}


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


parser = argparse.ArgumentParser()
parser.add_argument('--neighbors', type=int, default=10)
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

import Pyro4

Pyro4.config.SERIALIZER = 'pickle'  # see the Disclaimer
w2v = Pyro4.Proxy(args.w2v)

spos, _ = triples(args.triples, min_weight=args.min_weight, build_index=False)

vocabulary = {word for triple in spos for word in (triple.subject, triple.predicate, triple.object)} - STOP

vectors = {}

for words in grouper(vocabulary, 512):
    vectors.update(w2v.words_vec(words))

spos = [triple for triple in spos if
        triple.subject in vectors and triple.predicate in vectors and triple.object in vectors]

X, index2triple = np.empty((len(spos), w2v.vector_size * 3), 'float32'), {}

for i, triple in enumerate(spos):
    X[i] = np.concatenate((vectors[triple.subject], vectors[triple.predicate], vectors[triple.object]))
    index2triple[i] = triple

knn = faiss.IndexFlatIP(X.shape[1])
knn.add(X)

D, I = knn.search(X, args.neighbors + 1)

G = nx.Graph()

maximal_distance = -1

for i, (_D, _I) in enumerate(zip(D, I)):
    source = index2triple[i]
    words = Counter()

    for d, j in zip(_D.ravel(), _I.ravel()):
        if i != j:
            words[index2triple[j]] = d

    for target, distance in words.most_common(args.neighbors):
        # FIXME: our vectors are normalized, but the distance is greater than 1
        G.add_edge(source, target, weight=distance)
        maximal_distance = distance if distance > maximal_distance else maximal_distance

for _, _, d in G.edges(data=True):
    d['weight'] = maximal_distance / d['weight']

chinese_whispers(G, weighting='top', iterations=20)
clusters = aggregate_clusters(G)

for label, cluster in sorted(aggregate_clusters(G).items(), key=lambda e: len(e[1]), reverse=True):
    print('# Cluster %d\n' % label)

    predicates = {triple.predicate for triple in cluster}
    subjects = {triple.subject for triple in cluster}
    objects = {triple.object for triple in cluster}

    print('Predicates: %s\n' % ', '.join(predicates))
    print('Subjects: %s\n' % ', '.join(subjects))
    print('Objects: %s\n' % ', '.join(objects))