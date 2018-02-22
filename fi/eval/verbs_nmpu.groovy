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
    p 'percentage format'

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

def arguments(path, expected) {
    lexicon = expected.flatten().toSet()

    clusters = new HashMap<String, Set<String>>()

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            return
        }

        matcher = PREDICATES.matcher(line)

        if (matcher.find()) {
            words = matcher.group(1).split(", ").grep(lexicon).toSet()
            if (!words.isEmpty()) clusters[id] = words
            return
        }
    }

    return clusters.values()
}

expected = korhonen(Paths.get(options.arguments()[1]))

actual = arguments(Paths.get(options.arguments()[0]), expected)

nmpu = new NormalizedModifiedPurity<>(transform(actual), transform(expected))
result = nmpu.get()

format = options.p ? '%.2f\t%.2f\t%.2f\n' : '%.5f\t%.5f\t%.5f\n'

nmpu = result.precision * (options.p ? 100 : 1)
nipu = result.recall * (options.p ? 100 : 1)
f1 = result.f1Score * (options.p ? 100 : 1)

if (options.t) {
    printf(format, nmpu, nipu, f1)
} else {
    printf('nmPU/niPU/F1: ' + format, nmpu, nipu, f1)
}
