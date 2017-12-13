#!/usr/bin/env python

import argparse
import concurrent.futures
from collections import namedtuple, OrderedDict, defaultdict

import networkx as nx

from chinese_whispers import chinese_whispers, WEIGHTING, aggregate_clusters

Cluster = namedtuple('Cluster', 'id size elements')
Triple = namedtuple('Triple', 'subject predicate object weight')


def clusters(f, header=False):
    result = OrderedDict()

    if header:
        next(f, None)

    for line in f:
        id, *tail = line.strip().split('\t', 2)

        if len(tail) == 1:
            assert int(tail[0]) == 0
            size, elements = 0, []
        else:
            size = int(tail[0])
            elements = [element for element in tail[1].split(', ') if element]

        result[id] = Cluster(id, size, elements)

    return result


def triples(f, min_weight=None, build_index=True):
    spos, index = [], defaultdict(set)

    for line in f:
        predicate, subject, object, weight = line.strip().split('\t', 3)
        predicate, *_ = predicate.rpartition('#')
        weight = float(weight)

        if (min_weight is not None and weight < min_weight) or not subject or not predicate or not object:
            continue

        spos.append(Triple(subject, predicate, object, weight))

        if build_index:
            index[predicate].add(len(spos) - 1)

    return spos, index


def traverse(*relations, **kwargs):
    def similarity(word1, word2, default=.3):
        if not kwargs['w2v'] or kwargs['w2v'] is None:
            return default

        try:
            return w2v.similarity(word1, word2)
        except KeyError:
            return default

    G = nx.Graph()

    for relation in relations:
        for _, words in relation.items():
            for source in words:
                for target, weight in words.items():
                    if source != target:
                        G.add_edge(source, target, weight=similarity(source, target))

    return G


def emit(id, w2v, cw_mode):
    synset = synsets[id]

    verbs = [word for token in synset.elements for word, *_ in (token.rpartition('.v'),) if token.endswith('.v')]

    if not verbs:
        return id, nx.Graph()

    subjects, objects = defaultdict(dict), defaultdict(dict)

    for verb in verbs:
        for i in index[verb]:
            triple = spos[i]

            subjects[triple.object][triple.subject] = triple.weight
            objects[triple.subject][triple.object] = triple.weight

    G = chinese_whispers(traverse(subjects, objects, w2v=w2v), WEIGHTING[cw_mode])

    return id, G


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cw', choices=WEIGHTING.keys(), default='nolog')
    parser.add_argument('--min-weight', type=float, default=1000.)
    parser.add_argument('--w2v', default='PYRO:w2v@localhost:9090')
    parser.add_argument('verbs', type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
    args = parser.parse_args()

    import Pyro4

    Pyro4.config.SERIALIZER = 'pickle'
    w2v = Pyro4.Proxy(args.w2v)

    synsets = clusters(args.verbs, header=True)
    spos, index = triples(args.triples, min_weight=args.min_weight)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = (executor.submit(emit, id, w2v, args.cw) for id in synsets)

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            id, G = future.result()

            print('# Synset "%s"' % id)
            print()

            if G:
                print('Verbs: %s' % ', '.join(synsets[id].elements))
                print()

                for label, words in aggregate_clusters(G).items():
                    print('%d: %s' % (label, ', '.join(words)))
                    print()
            else:
                print('No verbs.')
                print()
