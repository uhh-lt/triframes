#!/usr/bin/awk -f

BEGIN {
    FS = OFS = "\t";
}

{
    print "# Cluster " $1;

    for (i = 1; i <= split($3, triples, /, /); i++) {
        sep = "";

        for (j = 1; j <= split(triples[i], elements, "|"); j++) {
            printf("%s", sep elements[j])
            sep = "\t";
        }

        print "";
    }

    print "";
}
