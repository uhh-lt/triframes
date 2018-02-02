#!/bin/sh -x

export LD_PRELOAD=$HOME/OpenBLAS-0.2.20/lib/libopenblas.so.0
export WEIGHT=0

make neighbors-subjects.txt neighbors-predicates.txt neighbors-objects.txt

for setup in triples triples-prepless; do
  export VSO=depcc-common-$setup.tsv

  export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog_single-single-$setup.txt
  GOLD=fn-common-$setup.tsv
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog-nolog-$setup.txt
  GOLD=fn-common-$setup.tsv
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'mode=nolog'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog_single-nolog-$setup.txt
  GOLD=fn-common-$setup.tsv
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog:select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog-nolog_single-$setup.txt
  GOLD=fn-common-$setup.tsv
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l mcl -g cw -gp 'mode=nolog:select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-mcl-nolog_singl-$setup.txt
  GOLD=fn-common-$setup.tsv
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"
done
