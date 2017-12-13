# Frame Induction for JOIN-T

```shell
$ ./roles.py --cw=log --min-weight=1000 ../verb-clusters/framenet-childfree.tsv vso-1.3m-pruned-strict.csv | tee roles.txt
```

```shell
$ ./multimodal.py --min-weight=1000 vso-1.3m-pruned-strict.csv | tee multimodal.txt
```

```shell
$ ./distinct.py --cw=log --min-weight=1000 vso-1.3m-pruned-strict.csv | tee distinct.txt
```
