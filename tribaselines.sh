#!/bin/bash -ex

export LANG=en_US.UTF-8 LC_COLLATE=C
set -o pipefail -x

export CLASSPATH=../watset-java/target/watset.jar
export VSO=depcc-common-triples.txt
export WEIGHT=0

for K in 10 150 500 1500 3000; do
  make K=$K trikmeans.txt
  mv trikmeans.txt trikmeans-k$K.txt
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "trikmeans-k$K.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "trikmeans-k$K.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "trikmeans-k$K.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "trikmeans-k$K.nmpu_cross"
  set -e
done

for K in 10 150 500; do
  make K=$K trispectral.txt
  mv trispectral.txt trispectral-k$K.txt
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "trispectral-k$K.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "trispectral-k$K.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "trispectral-k$K.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "trispectral-k$K.nmpu_cross"
  set -e
done

make tridbscan.txt
nice groovy 'fi/eval/triframes_nmpu.groovy' -t "tridbscan.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "tridbscan.nmpu"
timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "tridbscan.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "tridbscan.nmpu_cross"
