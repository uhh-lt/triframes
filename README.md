# Triframes: Unsupervised Semantic Frame Induction using Triclustering

We use dependency triples automatically extracted from a Web-scale corpus to perform unsupervised semantic frame induction. We cast the frame induction problem as a *triclustering* problem that is a generalization of clustering for *triadic* data. Our replicable benchmarks demonstrate that the proposed graph-based approach, **Triframes**, shows state-of-the art results on this task on a FrameNet-derived dataset and performing on par with competitive methods on a verb class clustering task.

## Prerequisites

* Linux
* Python ≥ 3.3 ([Anaconda](https://www.anaconda.com/) is recommended)
* Java ≥ 8
* Groovy ≥ 2.4
* [Faiss](https://github.com/facebookresearch/faiss)
* [Gensim](https://radimrehurek.com/gensim/)
* [Watset](https://github.com/nlpub/watset-java) (can be installed by `make watset.jar`)
* [Chinese Whispers](https://github.com/nlpub/chinese-whispers-python) for Python

## Running Triframes

Triframes inputs a set of dependency triples and outputs a set of triframes. The data is processed in two steps. First, a word embedding model is used to create a triple graph. Then, a fuzzy graph clustering algorithm, Watset, is used to extract triple communities representing triframes.

The input data used in our experiments can be obtained using the `make data` command. Our default input file, `vso-1.3m-pruned-strict.csv`, has four fields: verb, subject, object, weight. Loading the whole file can take a lot of memory, so our scripts support specifying a threshold using the `WEIGHT` environment variable. In our experiments, it is set to zero.

Since Triframes uses word embeddings, it is reasonable to download a model. In our experiments, we used the standard [Google News](https://code.google.com/archive/p/word2vec/) embeddings. In case you do not have them, it is possible to download them using `GoogleNews-vectors-negative300.bin`. There are two ways of specifying which word embeddings Triframes should use:

1. Passing the `W2V=/path/to/embeddings.bin` environment variable to each `make` invocation.
2. Serving the word vectors via [Word2Vec-Pyro4](https://github.com/nlpub/word2vec-pyro4). This requires passing the `PYRO=PYRO:…@…:9090` environment to each `make` invocation. It is *much* faster than loading the Word2Vec data on every run.

In case nothing is set, Triframes falls back to `PYRO=PYRO:w2v@localhost:9090`.

### Triframes with Watset

* `WEIGHT=10000 VSO=vso-1.3m-pruned-strict.csv make triw2v-watset.txt`

### Triframes Chinese Whispers

* `WEIGHT=10000 VSO=vso-1.3m-pruned-strict.csv make triw2v.txt`

## Running Baselines

* Triadic k-Means: `WEIGHT=10000 K=10 make trikmeans.txt`
* Triadic Spectral Clustering: `WEIGHT=10000 K=10 make trispectral.txt`
* Singletons: `make depcc-common-triples-full-singleton.tsv`
* Whole: `make depcc-common-triples-full-whole.tsv`

## Extraction of the evalution dataset based on the sentences annotated using the framenet roles

Assuming the command is launched on the ltcpu3 server: 

- Extract the data from the XML files:

```shell
$ ./fi/eval/extract_xml_framenet_roles.py /home/panchenko/verbs/frames/framenet/fndata-1.7/lu_fulltext/ fi/eval/roles-xml2.csv
```

- Extract the data from the parsed CoNLL files:

```shell
$ ./fi/eval/extract_conll_framenet_roles.py /home/panchenko/verbs/frames/parsed_framenet-1.0/collapsed_dependencies/lu_fulltext_merged/ fi/eval/output/ > fi/eval/output/paths.txt
```

## Downloads

Our data are available to download on the [Releases](https://github.com/uhh-lt/triframes/releases) page.

## Citation

* [Ustalov, D.](https://github.com/dustalov), [Panchenko, A.](https://github.com/alexanderpanchenko), [Kutuzov, A.](https://github.com/akutuzov), [Biemann, C.](https://www.inf.uni-hamburg.de/en/inst/ab/lt/people/chris-biemann.html), [Ponzetto, S.P.](https://dws.informatik.uni-mannheim.de/en/people/professors/profdrsimonepaoloponzetto/): [Unsupervised Semantic Frame Induction using Triclustering](https://aclweb.org/anthology/P18-2010). In: Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). pp. 55–62. Association for Computational Linguistics, Melbourne, VIC, Australia (2018)

```latex
@inproceedings{Ustalov:18:acl,
  author    = {Ustalov, Dmitry and Panchenko, Alexander and Kutuzov, Andrei and Biemann, Chris and Ponzetto, Simone Paolo},
  title     = {{Unsupervised Semantic Frame Induction using Triclustering}},
  booktitle = {Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)},
  year      = {2018},
  pages     = {55--62},
  address   = {Melbourne, VIC, Australia},
  publisher = {Association for Computational Linguistics},
  url       = {https://aclweb.org/anthology/P18-2010},
  language  = {english},
}
```
