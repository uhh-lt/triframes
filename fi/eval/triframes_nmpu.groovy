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

Locale.setDefault(Locale.ROOT)

/*
 * Usage: groovy -classpath ../watset-java/target/watset.jar triframes_nmpu.groovy arguments.txt[.gz] fn-depcc-triples.tsv[.gz]
 */
def options = new CliBuilder().with {
    usage = 'triframes_nmpu.groovy arguments.txt[.gz] fn-depcc-triples.tsv[.gz]'

    t 'tabular format'

    parse(args) ?: System.exit(1)
}

CLUSTER = Pattern.compile('^# Cluster *(.+?)$')
PREDICATES = Pattern.compile('^Predicates: *(.+)$')
SUBJECTS = Pattern.compile('^Subjects *(|\\(.+?\\)): *(.+)$')
OBJECTS = Pattern.compile('^Objects *(|\\(.+?\\)): *(.+)$')

@CompileStatic
@Canonical
class Element {
    String type
    String word
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
    clusters = new HashMap<String, Set<Element>>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            clusters[id] = new HashSet<Element>()
            return
        }

        matcher = PREDICATES.matcher(line)

        if (matcher.find()) {
            clusters[id].addAll(matcher.group(1).split(", ").collect { new Element('predicate', it) })
            return
        }

        matcher = SUBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id].addAll(matcher.group(2).split(", ").collect { new Element('subject', it) })
            return
        }

        matcher = OBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id].addAll(matcher.group(2).split(", ").collect { new Element('object', it) })
            return
        }
    }

    return clusters.values()
}

FN_CLUSTER = Pattern.compile('^# *(.+?): .*$')

def framenet(path) {
    clusters = new HashMap<String, Set<Element>>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = FN_CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            if (!clusters.containsKey(id)) clusters.put(id, new HashSet<Element>())
            return
        }

        spo = line.split('\t', 3)

        clusters.get(id).add(new Element("subject", spo[0]))
        clusters.get(id).add(new Element("predicate", spo[1]))
        clusters.get(id).add(new Element("object", spo[2]))
    }

    return clusters.values()
}

actual = arguments(Paths.get(options.arguments()[0]))

expected = framenet(Paths.get(options.arguments()[1]))

nmpu = new NormalizedModifiedPurity<Element>(transform(actual), transform(expected))
result = nmpu.get()

if (options.t) {
    printf('%.5f\t%.5f\t%.5f\t', result.precision, result.recall, result.f1Score)
} else {
    printf("Triframe  nmPU/niPU/F1: %.5f\t%.5f\t%.5f\n", result.precision, result.recall, result.f1Score)
}

def extract(frames, type) {
    frames.collect { frame -> frame.grep { (it.type == type) } }
}

actual_predicates = extract(actual, 'predicate')
expected_predicates = extract(expected, 'predicate')

nmpu = new NormalizedModifiedPurity<String>(transform(actual_predicates), transform(expected_predicates))
result = nmpu.get()

if (options.t) {
    printf('%.5f\t%.5f\t%.5f\t', result.precision, result.recall, result.f1Score)
} else {
    printf("Predicate nmPU/niPU/F1: %.5f\t%.5f\t%.5f\n", result.precision, result.recall, result.f1Score)
}

actual_subjects = extract(actual, 'subject')
expected_subjects = extract(expected, 'subject')

nmpu = new NormalizedModifiedPurity<String>(transform(actual_subjects), transform(expected_subjects))
result = nmpu.get()

if (options.t) {
    printf('%.5f\t%.5f\t%.5f\t', result.precision, result.recall, result.f1Score)
} else {
    printf("Subject   nmPU/niPU/F1: %.5f\t%.5f\t%.5f\n", result.precision, result.recall, result.f1Score)
}

actual_objects = extract(actual, 'object')
expected_objects = extract(expected, 'object')

nmpu = new NormalizedModifiedPurity<String>(transform(actual_objects), transform(expected_objects))
result = nmpu.get()

if (options.t) {
    printf('%.5f\t%.5f\t%.5f\n', result.precision, result.recall, result.f1Score)
} else {
    printf("Object    nmPU/niPU/F1: %.5f\t%.5f\t%.5f\n", result.precision, result.recall, result.f1Score)
}
