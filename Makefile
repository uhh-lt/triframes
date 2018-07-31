export LANG=en_US.UTF-8
export LC_COLLATE=C
export CLASSPATH=$(PWD)/watset.jar

VSO ?= vso-1.3m-pruned-strict.csv
WEIGHT ?= 10

-include Makefile.local

triframes: triw2v.txt triw2v-watset.txt

N ?= 10

.PHONY: triw2v.txt
triw2v.txt:
	nice ./triw2v.py -n=$(N) --min-weight=$(WEIGHT) $(VSO) > $@

.PHONY: trihosg.txt
trihosg.txt:
	nice ./trihosg.py -n=$(N) fi/hosg/300-10/{word,context,relation}-matrix fi/hosg/counts.gz > $@

WATSET ?= -l cw -lp 'mode=top' -g cw -gp 'mode=top'

.PHONY: triw2v-watset.txt
triw2v-watset.txt:
	nice ./triw2v.py -n=$(N) --min-weight=$(WEIGHT) --pickle $(@:txt=pkl) $(VSO)
	nice groovy ./triw2v_watset.groovy $(WATSET) $(@:txt=pkl) > $@

.PHONY: trihosg-watset.txt
trihosg-watset.txt:
	nice ./trihosg.py -n=$(N) --pickle $(@:txt=pkl) fi/hosg/300-10/{word,context,relation}-matrix fi/hosg/counts.gz
	nice groovy ./triw2v_watset.groovy $(WATSET) $(@:txt=pkl) > $@

K ?= 10

.PHONY: trikmeans.txt
trikmeans.txt:
	nice ./triclustering.py --method=kmeans -k=$(K) --min-weight=$(WEIGHT) $(VSO) > $@

.PHONY: trispectral.txt
trispectral.txt:
	nice ./triclustering.py --method=spectral -k=$(K) --min-weight=$(WEIGHT) $(VSO) > $@

.PHONY: tridbscan.txt
tridbscan.txt:
	nice ./triclustering.py --method=dbscan --min-weight=$(WEIGHT) $(VSO) > $@

STOP=(i|he|she|it|they|you|this|we|them|their|us|my|those|who|what|that|which|each|some|me|one|the)

fn-depcc-triples-prepless.tsv:
	grep -viP '(^$(STOP)|$(STOP)$$)' fn-depcc-triples.tsv > $@

depcc-common-triples-prepless.tsv:
	grep -viP '\t$(STOP)' depcc-common-triples.tsv > $@

depcc-common-singleton.tsv:
	gawk -f ./baseline-singleton.awk depcc-common-triples.tsv > $@

depcc-common-whole.tsv:
	gawk -f ./baseline-whole.awk depcc-common-triples.tsv > $@

lda-frames.txt:
	./lda-frames.py ../verb-clusters/lda-frames/data/bnc-export/{frames,roles,verbs}.txt > $@

clean:
	rm -rf __pycache__
	rm -fv *.txt *-watset.tsv
	rm -fv *.nmpu *.nmpu_cross

watset.jar:
	rm -fv $@
	curl -Lo "$@" https://github.com/nlpub/watset-java/releases/download/2.0.0-beta9/watset.jar

data: depcc-common-triples-full.tsv fn-depcc-triples-full.tsv

depcc-common-triples-full.tsv:
	zcat fi/eval/data/$@.gz > $@

fn-depcc-triples-full.tsv:
	zcat fi/eval/data/$@.gz > $@
