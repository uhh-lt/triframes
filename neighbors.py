#!/usr/bin/env python

import argparse
from collections import Counter
from itertools import zip_longest

import faiss  # PYTHONPATH=/path/to/faiss
import numpy as np

from roles import triples


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


ELEMENTS = {
    'subject': lambda triple: triple.subject,
    'predicate': lambda triple: triple.predicate,
    'object': lambda triple: triple.object
}

parser = argparse.ArgumentParser()
parser.add_argument('--element', choices=ELEMENTS.keys(), required=True)
parser.add_argument('--neighbors', type=int, default=10)
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

import Pyro4

Pyro4.config.SERIALIZER = 'pickle'  # see the Disclaimer
w2v = Pyro4.Proxy(args.w2v)

spos, index = triples(args.triples, min_weight=args.min_weight)

accessor = ELEMENTS[args.element]
vocabulary = {accessor(triple) for triple in spos}
vectors = {}

for words in grouper(vocabulary, 512):
    vectors.update(w2v.words_vec(words))

X, index2word = np.empty((len(vectors), w2v.vector_size), 'float32'), {}

for i, (target, vector) in enumerate(vectors.items()):
    X[i] = vector
    index2word[i] = target

knn = faiss.IndexFlatIP(X.shape[1])
knn.add(X)

D, I = knn.search(X, args.neighbors + 1)

edges = set()

for i, (_D, _I) in enumerate(zip(D, I)):
    source = index2word[i]
    words = Counter()

    for d, j in zip(_D.ravel(), _I.ravel()):
        if i != j:
            words[index2word[j]] = d

    for target, distance in words.most_common(args.neighbors):
        edges.add((source, target, distance))

for source, target, distance in edges:
    print('%s\t%s\t%f' % (source, target, distance))
