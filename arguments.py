#!/usr/bin/env python

import argparse

from collections import defaultdict, Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity as sim

from roles import triples, clusters

parser = argparse.ArgumentParser()
parser.add_argument('--min-weight', type=float, default=1000.)
parser.add_argument('triples', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('subjects', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('predicates', type=argparse.FileType('r', encoding='UTF-8'))
parser.add_argument('objects', type=argparse.FileType('r', encoding='UTF-8'))
args = parser.parse_args()

spos, predicate_index = triples(args.triples, min_weight=args.min_weight)
subjects, predicates, objects = clusters(args.subjects), clusters(args.predicates), clusters(args.objects)

D = []

for dataset in (subjects, predicates, objects):
    for cluster in dataset.values():
        D.append({element: 1 for element in cluster.elements})

v = Pipeline([('dict', DictVectorizer()), ('tfidf', TfidfTransformer())])
v.fit(D)

del D

subject_index, object_index = defaultdict(set), defaultdict(set)

for cluster in subjects.values():
    for element in cluster.elements:
        subject_index[element].add(cluster.id)

for cluster in objects.values():
    for element in cluster.elements:
        object_index[element].add(cluster.id)

for cluster in predicates.values():
    predicate_triples = {spos[id] for predicate in cluster.elements for id in predicate_index[predicate]}

    subject_ctx = Counter([triple.subject for triple in predicate_triples])
    object_ctx = Counter([triple.object for triple in predicate_triples])

    subject_space = {id for subject in subject_ctx for id in subject_index[subject]}
    object_space = {id for object in object_ctx for id in object_index[object]}

    subject_sim = Counter({id: sim(v.transform(subject_ctx), v.transform({element: 1 for element in subjects[id].elements})).item(0) for id in subject_space})
    object_sim = Counter({id: sim(v.transform(object_ctx), v.transform({element: 1 for element in objects[id].elements})).item(0) for id in object_space})

    print('# Cluster %s\n' % cluster.id)
    print('Predicates: %s' % ', '.join(cluster.elements))

    for id, cosine in subject_sim.most_common(1):
        print('Subjects: %s' % ', '.join(subjects[id].elements))

    for id, cosine in object_sim.most_common(1):
        print('Objects: %s' % ', '.join(objects[id].elements))

    print('')

    pass
