#!/usr/bin/env groovy
import groovy.transform.Canonical
import groovy.transform.CompileStatic
import org.nlpub.watset.eval.NormalizedModifiedPurity

import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern
import java.util.zip.GZIPInputStream

import static NormalizedModifiedPurity.transform
import static java.util.stream.Collectors.toList
import static java.util.stream.Collectors.toSet

Locale.setDefault(Locale.ROOT)

/*
 * Usage: groovy -classpath ../watset-java/target/watset.jar triframes_nmpu.groovy arguments.txt[.gz] fn-depcc-triples.tsv[.gz]
 */
def cli = new CliBuilder(usage: 'triframes_nmpu.groovy arguments.txt[.gz] fn-depcc-triples.tsv[.gz]')

def options = cli.parse(args)

CLUSTER = Pattern.compile('^# Cluster *(\\w+?)$')
PREDICATES = Pattern.compile('^Predicates: *(.+)$')
SUBJECTS = Pattern.compile('^Subjects *(|\\(.+?\\)): *(.+)$')
OBJECTS = Pattern.compile('^Objects *(|\\(.+?\\)): *(.+)$')

@CompileStatic
@Canonical
class Frame {
    String id
    Set<String> predicates
    Set<String> subjects
    Set<String> objects
}

@CompileStatic
@Canonical
class Triple {
    String subject
    String predicate
    String object
}

def lines(path) {
    if (!path.toString().endsWith(".gz")) return Files.lines(path)

    Files.newInputStream(path).with { is ->
        new GZIPInputStream(is).with { gis ->
            new InputStreamReader(gis, StandardCharsets.UTF_8).with { reader ->
                new BufferedReader(reader).with { br ->
                    return br.lines()
                }
            }
        }
    }
}

def arguments(path) {
    clusters = new HashMap<String, Frame>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            clusters[id] = new Frame()
            clusters[id].id = id
            return
        }

        matcher = PREDICATES.matcher(line)

        if (matcher.find()) {
            clusters[id].predicates = matcher.group(1).split(", ")
            return
        }

        matcher = SUBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id].subjects = matcher.group(2).split(", ")
            return
        }

        matcher = OBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id].objects = matcher.group(2).split(", ")
        }
    }

    triples = new HashSet<Collection<Triple>>(clusters.size())

    clusters.each { _, frame ->
        cluster = new HashSet<Triple>()

        frame.predicates.each { predicate ->
            frame.subjects.each { subject ->
                frame.objects.each { object ->
                    cluster.add(new Triple(subject, predicate, object))
                }
            }
        }

        triples.add(cluster)
    }

    return triples
}

FN_CLUSTER = Pattern.compile('^# *(.+?): .*$')

def framenet(path) {
    clusters = new HashMap<String, Collection<Triple>>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = FN_CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            if (!clusters.containsKey(id)) clusters.put(id, new HashSet<Triple>())
            return
        }

        spo = line.split('\t', 3)

        clusters.get(id).add(new Triple(spo[0], spo[1], spo[2]))
    }

    return clusters.values()
}

actual = arguments(Paths.get(options.arguments()[0]))

expected = framenet(Paths.get(options.arguments()[1]))

nmpu = new NormalizedModifiedPurity<Triple>(transform(actual), transform(expected))
result = nmpu.get()

printf("Triframe nmPU = %f\n", result.precision)
printf("Triframe niPU = %f\n", result.recall)
printf("Triframe F1 = %f\n\n", result.f1Score)

def extract(triples, closure) {
    triples.stream().map { it.stream().map { closure(it) }.collect(toSet()) }.collect(toList())
}

actual_predicates = extract(actual) { triple -> triple.predicate }
expected_predicates = extract(expected) { triple -> triple.predicate }

nmpu = new NormalizedModifiedPurity<String>(transform(actual_predicates), transform(expected_predicates))
result = nmpu.get()

printf("Predicate nmPU = %f\n", result.precision)
printf("Predicate niPU = %f\n", result.recall)
printf("Predicate F1 = %f\n\n", result.f1Score)

actual_subjects = extract(actual) { triple -> triple.subject }
expected_subjects = extract(expected) { triple -> triple.subject }

nmpu = new NormalizedModifiedPurity<String>(transform(actual_subjects), transform(expected_subjects))
result = nmpu.get()

printf("Subject nmPU = %f\n", result.precision)
printf("Subject niPU = %f\n", result.recall)
printf("Subject F1 = %f\n\n", result.f1Score)

actual_objects = extract(actual) { triple -> triple.object }
expected_objects = extract(expected) { triple -> triple.object }

nmpu = new NormalizedModifiedPurity<String>(transform(actual_objects), transform(expected_objects))
result = nmpu.get()

printf("Object nmPU = %f\n", result.precision)
printf("Object niPU = %f\n", result.recall)
printf("Object F1 = %f\n", result.f1Score)
