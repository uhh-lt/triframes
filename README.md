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

