#!/usr/bin/awk -f

BEGIN {
  FS = "\t";

  if (length(S) == 0) {
    print "The S threshold is not specified; using no threshold." > "/dev/stderr";
  }

  if (length(O) == 0) {
    print "The O threshold is not specified; using no threshold." > "/dev/stderr";
  }
}

/^# Cluster/ {
  cluster = $0;
  next;
}

/^Predicates/ {
  predicates = $0;
  next;
}

/^Subjects \(sim =/ {
  subjects = $0;
  match($0, /\(sim = ([[:digit:]]+\.[[:digit:]]+)\)/, groups);
  subject = groups[1];
  next;
}

/^Objects \(sim =/ {
  objects = $0;
  match($0, /\(sim = ([[:digit:]]+\.[[:digit:]]+)\)/, groups);
  object = groups[1];
  next;
}

(length(S) == 0 || subject >= S) && (length(O) == 0 || object >= O) {
  print cluster ORS ORS predicates ORS subjects ORS objects ORS;
  cluster = predicates = subjects = objects = subject = object = "";
}
