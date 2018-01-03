#!/usr/bin/env python

import argparse
import sys
from collections import Counter
from itertools import zip_longest

import faiss # PYTHONPATH=/path/to/faiss
import networkx as nx
import numpy as np

from roles import triples


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

spos, index = triples(args.triples, min_weight=args.min_weight)

subjects = {triple.subject for triple in spos}
vectors = {}

for words in grouper(subjects, 512):
    vectors.update(w2v.words_vec(words))

X, index2word = np.empty((len(vectors), w2v.vector_size), 'float32'), {}

for j, (target, vector) in enumerate(vectors.items()):
    X[j] = vector
    index2word[j] = target

knn = faiss.IndexFlatIP(X.shape[1])
knn.add(X)

y = np.array([w2v.word_vec('people')])

D, I = knn.search(X, args.neighbors + 1)

G = nx.Graph()

for i, (_D, _I) in enumerate(zip(D, I)):
    source = index2word[i]
    words = Counter()

    for d, j in zip(_D.ravel(), _I.ravel()):
        if i != j:
            words[index2word[j]] = d

    for target, distance in words.most_common(args.neighbors):
        G.add_edge(source, target, weight=distance)

nx.write_weighted_edgelist(G, sys.stdout, delimiter='\t')
