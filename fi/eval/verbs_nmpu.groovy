#!/usr/bin/env groovy
import org.nlpub.watset.eval.NormalizedModifiedPurity

import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern
import java.util.zip.GZIPInputStream

import static NormalizedModifiedPurity.transform

Locale.setDefault(Locale.ROOT)

/*
 * Usage: groovy -classpath ../watset-java/target/watset.jar verbs_nmpu.groovy arguments.txt[.gz] korhonen2003.poly.txt[.gz]
 */
def options = new CliBuilder().with {
    usage = 'verbs_nmpu.groovy arguments.txt[.gz] korhonen2003.poly.txt[.gz]'

    t 'tabular format'

    parse(args) ?: System.exit(1)
}

CLUSTER = Pattern.compile('^# Cluster *(.+?)$')
PREDICATES = Pattern.compile('^Predicates: *(.+)$')

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
    clusters = new HashMap<String, Set<String>>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            clusters[id] = new HashSet<String>()
            return
        }

        matcher = PREDICATES.matcher(line)

        if (matcher.find()) {
            clusters[id].addAll(matcher.group(1).split(", "))
            return
        }
    }

    return clusters.values()
}

TAB = Pattern.compile('\t+')

def korhonen(path) {
    clusters = new ArrayList<Set<String>>()

    lines(path).each { line ->
        if (line.empty) return

        row = TAB.split(line, 3)

        words = new HashSet<>(Arrays.asList(row[2].split(' ')))

        clusters.add(words)
    }

    return clusters
}

actual = arguments(Paths.get(options.arguments()[0]))

expected = korhonen(Paths.get(options.arguments()[1]))

nmpu = new NormalizedModifiedPurity<>(transform(actual), transform(expected))
result = nmpu.get()

if (options.t) {
    printf('%.5f\t%.5f\t%.5f\t', result.precision, result.recall, result.f1Score)
} else {
    printf("nmPU/niPU/F1: %.5f\t%.5f\t%.5f\n", result.precision, result.recall, result.f1Score)
}
