#!/usr/bin/env python

import argparse
from itertools import zip_longest

import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans, SpectralClustering, DBSCAN

from roles import triples

STOP = {'i', 'he', 'she', 'it', 'they', 'you', 'this', 'we', 'them', 'their', 'us', 'my', 'those', 'who', 'what',
        'that', 'which', 'each', 'some', 'me', 'one', 'the'}


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


METHODS = {
    'kmeans': KMeans,
    'spectral': SpectralClustering,
    'dbscan': DBSCAN
}

parser = argparse.ArgumentParser()
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
parser.add_argument('--method', choices=METHODS.keys(), default='kmeans')
parser.add_argument('-k', type=int, default=10)
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

clustering = METHODS[args.method](n_jobs=-2) if args.method == 'dbscan' else METHODS[args.method](n_clusters=args.k, n_jobs=-2)
clusters = clustering.fit_predict(X)

frames = defaultdict(set)

for i, cluster in enumerate(clusters):
    frames[int(cluster)].add(index2triple[i])

for label, cluster in frames.items():
    print('# Cluster %d\n' % label)

    predicates = {triple.predicate for triple in cluster}
    subjects = {triple.subject for triple in cluster}
    objects = {triple.object for triple in cluster}

    print('Predicates: %s' % ', '.join(predicates))
    print('Subjects: %s' % ', '.join(subjects))
    print('Objects: %s\n' % ', '.join(objects))
