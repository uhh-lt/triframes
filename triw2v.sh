#!/bin/bash -ex

export LANG=en_US.UTF-8 LC_COLLATE=C
set -o pipefail -x

export CLASSPATH=../watset-java/target/watset.jar
export VSO=depcc-common-triples.txt
export WEIGHT=0

for N in 5 10 30 50 100; do
  make triw2v.txt N=$N
  mv triw2v.txt "triw2v-n$N.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-n$N.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-n$N.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-n$N.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-n$N.nmpu_cross"
  set -e

  make triw2v-watset.txt N=$N
  mv triw2v-watset.txt "triw2v-watset-n$N-top-top.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-watset-n$N-top-top.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-top-top.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-watset-n$N-top-top.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-top-top.nmpu_cross"

  make triw2v-watset.txt N=$N WATSET="-l mcl -g mcl-bin -gp bin=/home/dustalov/mcl-14-137/bin/mcl"
  mv triw2v-watset.txt "triw2v-watset-n$N-mcl-mcl.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-watset-n$N-mcl-mcl.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-mcl-mcl.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-watset-n$N-mcl-mcl.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-mcl-mcl.nmpu_cross"
done

export VSO=depcc-common-triples.tsv

for N in 5 10 30 50 100; do
  make triw2v.txt N=$N
  mv triw2v.txt "triw2v-n$N-top-top-full.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-n$N-top-top-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-n$N-top-top-full.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-n$N-top-top-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-n$N-top-top-full.nmpu_cross"
  set -e

  make triw2v-watset.txt N=$N
  mv triw2v-watset.txt "triw2v-watset-n$N-top-top-full.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-watset-n$N-top-top-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-top-top-full.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-watset-n$N-top-top-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-top-top-full.nmpu_cross"

  make triw2v-watset.txt N=$N WATSET="-l mcl -g mcl-bin -gp bin=/home/dustalov/mcl-14-137/bin/mcl"
  mv triw2v-watset.txt "triw2v-watset-n$N-mcl-mcl-full.txt"
  nice groovy 'fi/eval/triframes_nmpu.groovy' -t "triw2v-watset-n$N-mcl-mcl-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-mcl-mcl-full.nmpu"
  set +e
  timeout 1m nice groovy 'fi/eval/triframes_nmpu_cross.groovy' -t "triw2v-watset-n$N-mcl-mcl-full.txt" "fi/eval/data/fn-depcc-triples.tsv.gz" | tee "triw2v-watset-n$N-mcl-mcl-full.nmpu_cross"
done
