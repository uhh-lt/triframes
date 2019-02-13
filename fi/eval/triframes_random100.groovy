#!/usr/bin/env groovy

import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Paths
import java.util.regex.Pattern
import java.util.zip.GZIPInputStream

/*
 * Copyright 2019 Dmitry Ustalov
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

/*
 * Usage: groovy -classpath ../watset-java/target/watset.jar triframes_nmpu.groovy arguments.txt[.gz] fn-depcc-triples.tsv[.gz]
 */
def options = new CliBuilder().with {
    usage = 'triframes_random100.groovy arguments.txt[.gz]'

    s args: 1, 'seed'

    parse(args) ?: System.exit(1)
}

CLUSTER = Pattern.compile('^# Cluster *(.+?)$')
PREDICATES = Pattern.compile('^Predicates: *(.+)$')
SUBJECTS = Pattern.compile('^Subjects *(|\\(.+?\\)): *(.+)$')
OBJECTS = Pattern.compile('^Objects *(|\\(.+?\\)): *(.+)$')

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
    clusters = [:]

    id = null

    lines(path).each { line ->
        if (line.empty) return

        matcher = CLUSTER.matcher(line)

        if (matcher.find()) {
            id = matcher.group(1)
            clusters[id] = [verbs: new LinkedHashSet(), subjects: new LinkedHashSet<>(), objects: new LinkedHashSet<>()]
            return
        }

        matcher = PREDICATES.matcher(line)

        if (matcher.find()) {
            clusters[id]['verbs'].addAll(matcher.group(1).split(", "))
            return
        }

        matcher = SUBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id]['subjects'].addAll(matcher.group(2).split(", "))
            return
        }

        matcher = OBJECTS.matcher(line)

        if (matcher.find()) {
            clusters[id]['objects'].addAll(matcher.group(2).split(", "))
            return
        }
    }

    return clusters
}

triframes = arguments(Paths.get(options.arguments()[0]))

sample = triframes.grep { it.value.values().flatten().size() > 3 }

System.err.printf('%d non-trivial frames found%n', sample.size())

printf('id\tvote\tsubjects\tverbs\tobjects%n')

random = new Random(options.s ? Integer.valueOf(options.s) : 1337)

sample.with { Collections.shuffle(it, random); it }.take(100).each {
    printf('%s\t\t%s\t%s\t%s%n',
            it.key,
            it.value['subjects'].join(', '),
            it.value['verbs'].join(', '),
            it.value['objects'].join(', '))
}
