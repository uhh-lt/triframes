#!/usr/bin/env python

import argparse
import concurrent.futures
from collections import defaultdict, Counter

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity as sim
from sklearn.pipeline import Pipeline

from roles import triples, clusters

parser = argparse.ArgumentParser()
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('subjects', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('predicates', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('objects', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

import functools

print = functools.partial(print, flush=True)

spos, predicate_index = triples(args.triples, min_weight=args.min_weight)
subjects, predicates, objects = clusters(args.subjects), clusters(args.predicates), clusters(args.objects)

D = []

for dataset in (subjects, objects):
    for cluster in dataset.values():
        D.append({element: 1 for element in cluster.elements})

v = Pipeline([('dict', DictVectorizer()), ('tfidf', TfidfTransformer())])
X = v.fit_transform(D)

del D

subject_index, object_index = defaultdict(set), defaultdict(set)
subject_vec, object_vec = {}, {}

for i, cluster in enumerate(subjects.values()):
    for element in cluster.elements:
        subject_index[element].add(cluster.id)

    subject_vec[cluster.id] = i

for i, cluster in enumerate(objects.values()):
    for element in cluster.elements:
        object_index[element].add(cluster.id)

    object_vec[cluster.id] = len(subject_vec) + i


def emit(id):
    cluster = predicates[id]

    predicate_triples = {spos[id] for predicate in cluster.elements for id in predicate_index[predicate]}

    subject_ctx = Counter([triple.subject for triple in predicate_triples])
    object_ctx = Counter([triple.object for triple in predicate_triples])

    subject_space = {id for subject in subject_ctx for id in subject_index[subject]}
    object_space = {id for object in object_ctx for id in object_index[object]}

    subject_sim = Counter({id: sim(v.transform(subject_ctx), X[subject_vec[id]]).item(0) for id in subject_space})
    object_sim = Counter({id: sim(v.transform(object_ctx), X[object_vec[id]]).item(0) for id in object_space})

    return cluster.id, subject_sim.most_common(1), object_sim.most_common(1)


with concurrent.futures.ProcessPoolExecutor() as executor:
    futures = (executor.submit(emit, id) for id in predicates)

    for future in concurrent.futures.as_completed(futures):
        id, subject_match, object_match = future.result()

        cluster = predicates[id]

        print('# Cluster %s\n' % cluster.id)
        print('Predicates: %s' % ', '.join(cluster.elements))

        for subject_id, cosine in subject_match:
            print('Subjects (sim = %.4f): %s' % (cosine, ', '.join(subjects[subject_id].elements)))

        for object_id, cosine in object_match:
            print('Objects (sim = %.4f): %s' % (cosine, ', '.join(objects[object_id].elements)))

        print('')
