#!/usr/bin/env groovy

Locale.setDefault(Locale.ROOT)

@Grab('org.apache.commons:commons-csv:1.6')
import org.apache.commons.csv.CSVParser
import static org.apache.commons.csv.CSVFormat.EXCEL

@Grab('org.dkpro.statistics:dkpro-statistics-agreement:2.1.0')
import org.dkpro.statistics.agreement.coding.*
import org.dkpro.statistics.agreement.distance.NominalDistanceFunction

import java.nio.file.Paths

items = [:]
subjects = [:]
verbs = [:]
objects = [:]

args.eachWithIndex { filename, rater ->
    Paths.get(filename).withReader { reader ->
        csv = new CSVParser(reader, EXCEL.withHeader().withDelimiter('\t' as char))

        for (record in csv.iterator()) {
            if (!(item   = record.get('id')))   continue
            if (!(answer = record.get('vote'))) continue
            if (!(subjectsList = record.get('subjects'))) continue
            if (!(verbsList = record.get('verbs'))) continue
            if (!(objectsList = record.get('objects'))) continue

            if (!items.containsKey(item)) items[item] = [:]

            items[item][rater] = answer.equalsIgnoreCase('1')
            subjects[item] = subjectsList
            verbs[item] = verbsList
            objects[item] = objectsList
        }
    }
}

def aggregate(answers) {
    answers.sort().inject([:]) { counts, _, vote ->
        counts[vote] = counts.getOrDefault(vote, 0) + 1
        counts
    }
}

def major(answers) {
    winner = aggregate(answers).max { it.value }
    [winner.key, winner.value]
}

good = items.grep {
    (winner, count) = major(it.value)
    winner && count == it.value.size()
}.collectEntries()

System.err.println('Unanimously good: ' + good.size())

bad = items.grep {
    (winner, count) = major(it.value)
    !winner && count == it.value.size()
}.collectEntries()

System.err.println('Unanimously bad: ' + bad.size())

System.err.println('Clash: ' + (items.size() - good.size() - bad.size()))

study = new CodingAnnotationStudy(args.size())

items.each { item, answers ->
    study.addItemAsArray(answers.inject(new Boolean[args.size()]) { array, rater, answer ->
        array[rater] = answer
        array
    })
}

percent = new PercentageAgreement(study)
System.err.printf('PercentageAgreement: %f %%%n', percent.calculateAgreement() * 100)

alphaNominal = new KrippendorffAlphaAgreement(study, new NominalDistanceFunction())
System.err.printf('KrippendorffAlphaAgreement: %f%n', alphaNominal.calculateAgreement())

fleissKappa = new FleissKappaAgreement(study)
System.err.printf('FleissKappaAgreement: %f%n', fleissKappa.calculateAgreement())

randolphKappa = new RandolphKappaAgreement(study)
System.err.printf('RandolphKappaAgreement: %f%n', randolphKappa.calculateAgreement())

printf('id\tclass\tvotes1\tvotes0\tsubjects\tverbs\tobjects%n')

items.sort { good.containsKey(it.key) ? 2 : bad.containsKey(it.key) ? 1 : 0 }.each {
    counts = aggregate(it.value)

    printf('%s\t%s\t%d\t%d\t%s\t%s\t%s%n',
            it.key,
            good.containsKey(it.key) ? 'good' : bad.containsKey(it.key) ? 'bad' : 'clash',
            counts.getOrDefault(true, 0),
            counts.getOrDefault(false, 0),
            subjects[it.key],
            verbs[it.key],
            objects[it.key],
    )
}
