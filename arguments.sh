#!/bin/bash -x

export LANG=en_US.UTF-8 LC_COLLATE=C
set -o pipefail -e

export WEIGHT=0

for setup in triples-prepless; do
  export VSO=depcc-common-$setup.tsv
  GOLD=fn-depcc-$setup.tsv

  make neighbors-subjects.txt neighbors-predicates.txt neighbors-objects.txt

  export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog_single-single-$setup
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog-nolog-$setup
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog:select=single' -g cw -gp 'mode=nolog'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog_single-nolog-$setup
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l cw -lp 'mode=nolog' -g cw -gp 'mode=nolog:select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-nolog-nolog_single-$setup
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"

  export WATSET="-l mcl -g cw -gp 'mode=nolog:select=single'"
  make neighbors-objects-watset.tsv neighbors-predicates-watset.tsv neighbors-subjects-watset.tsv
  make arguments.txt
  DATA=arguments-mcl-nolog_single-$setup
  mv arguments.txt $DATA.txt
  nice groovy -classpath ../watset-java/target/watset.jar 'fi/eval/triframes_nmpu.groovy' -t "$DATA.txt" "$GOLD" | tee "$DATA.nmpu"
done
