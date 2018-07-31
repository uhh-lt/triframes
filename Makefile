export LANG=en_US.UTF-8
export LC_COLLATE=C
export CLASSPATH=$(PWD)/watset.jar

VSO ?= vso-1.3m-pruned-strict.csv
WEIGHT ?= 10

-include Makefile.local

all: roles.txt multimodal.txt distinct.txt

.PHONY: roles.txt
roles.txt:
	nice ./roles.py --cw=log --min-weight=$(WEIGHT) ../verb-clusters/framenet-childfree.tsv $(VSO) | tee roles.txt

.PHONY: multimodal.txt
multimodal.txt:
	nice ./multimodal.py --cw=log --min-weight=$(WEIGHT) $(VSO) | tee multimodal.txt

.PHONY: distinct.txt
distinct.txt:
	nice ./distinct.py --cw=log --min-weight=$(WEIGHT) $(VSO) | tee distinct.txt

.PHONY: multimodal-watset.txt
multimodal-watset.txt:
	nice ./multimodal-graph.py --min-weight=$(WEIGHT) $(VSO) > multimodal-graph.txt
	nice java -jar ../watset-java/target/watset.jar -i multimodal-graph.txt -o multimodal-watset.tsv watset -l cw -lp mode=nolog -g cw
	nice ./multimodal-pretty.awk multimodal-watset.tsv > multimodal-watset.txt

.PHONY: neighbors-subjects.txt
neighbors-subjects.txt:
	PYTHONPATH=../faiss nice ./neighbors.py --element=subject --min-weight=$(WEIGHT) $(VSO) >neighbors-subjects.txt
	sort -o neighbors-subjects.txt neighbors-subjects.txt

.PHONY: neighbors-predicates.txt
neighbors-predicates.txt:
	PYTHONPATH=../faiss nice ./neighbors.py --element=predicate --min-weight=$(WEIGHT) $(VSO) >neighbors-predicates.txt
	sort -o neighbors-predicates.txt neighbors-predicates.txt

.PHONY: neighbors-objects.txt
neighbors-objects.txt:
	PYTHONPATH=../faiss nice ./neighbors.py --element=object --min-weight=$(WEIGHT) $(VSO) >neighbors-objects.txt
	sort -o neighbors-objects.txt neighbors-objects.txt

.PHONY: neighbors-subjects-watset.tsv
neighbors-subjects-watset.tsv:
	nice java -jar ../watset-java/target/watset.jar -i neighbors-subjects.txt -o neighbors-subjects-watset.tsv watset -l cw -lp mode=nolog -g cw

.PHONY: neighbors-predicates-watset.tsv
neighbors-predicates-watset.tsv:
	nice java -jar ../watset-java/target/watset.jar -i neighbors-predicates.txt -o neighbors-predicates-watset.tsv watset -l cw -lp mode=nolog -g cw

.PHONY: neighbors-objects-watset.tsv
neighbors-objects-watset.tsv:
	nice java -jar ../watset-java/target/watset.jar -i neighbors-objects.txt -o neighbors-objects-watset.tsv watset -l cw -lp mode=nolog -g cw

.PHONY: arguments.txt
arguments.txt:
	nice ./arguments.py --min-weight=$(WEIGHT) $(VSO) neighbors-subjects-watset.tsv neighbors-predicates-watset.tsv neighbors-objects-watset.tsv > arguments.txt

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
