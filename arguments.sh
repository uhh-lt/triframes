#!/bin/sh -x

export LD_PRELOAD=$HOME/OpenBLAS-0.2.20/lib/libopenblas.so.0
export VSO=depcc-common-triples.txt
export WEIGHT=0
# make neighbors-subjects.txt neighbors-predicates.txt neighbors-objects.txt

export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'select=single'"
make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
make arguments.txt
mv arguments.txt arguments-cw_nolog_single-cw_single.txt
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t 'arguments-cw_nolog_single-cw_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog_single-cw_single.nmpu'
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu_cross.groovy' -t 'arguments-cw_nolog_single-cw_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog_single-cw_single.nmpu_cross'

export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog'"
make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
make arguments.txt
mv arguments.txt arguments-cw_nolog-cw_nolog.txt
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t 'arguments-cw_nolog-cw_nolog.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog-cw_nolog.nmpu'
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu_cross.groovy' -t 'arguments-cw_nolog-cw_nolog.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog-cw_nolog.nmpu_cross'

export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'mode=nolog'"
make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
make arguments.txt
mv arguments.txt arguments-cw_nolog_single-cw_nolog.txt
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t 'arguments-cw_nolog_single-cw_nolog.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog_single-cw_nolog.nmpu'
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu_cross.groovy' -t 'arguments-cw_nolog_single-cw_nolog.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog_single-cw_nolog.nmpu_cross'

export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog:select=single'"
make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
make arguments.txt
mv arguments.txt arguments-cw_nolog-cw_nolog_single.txt
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t 'arguments-cw_nolog-cw_nolog_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog-cw_nolog_single.nmpu'
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu_cross.groovy' -t 'arguments-cw_nolog-cw_nolog_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'cw_nolog-cw_nolog_single.nmpu_cross'

export WATSET="-l mcl -g cw -gp 'mode=nolog:select=single'"
make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
make arguments.txt
mv arguments.txt arguments-mcl-cw_nolog_single.txt
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t 'arguments-mcl-cw_nolog_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'mcl-cw_nolog_single.nmpu'
nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu_cross.groovy' -t 'arguments-mcl-cw_nolog_single.txt' 'fi/eval/data/fn-depcc-triples.tsv.gz' | tee 'mcl-cw_nolog_single.nmpu_cross'
