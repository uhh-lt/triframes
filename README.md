# Frame Induction for JOIN-T

## Extraction of roles and frames from the SVO triples 

```shell
$ ./roles.py --cw=log --min-weight=1000 ../verb-clusters/framenet-childfree.tsv vso-1.3m-pruned-strict.csv | tee roles.txt
```

```shell
$ ./multimodal.py --min-weight=1000 vso-1.3m-pruned-strict.csv | tee multimodal.txt
```

```shell
$ ./distinct.py --cw=log --min-weight=1000 vso-1.3m-pruned-strict.csv | tee distinct.txt
```

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
