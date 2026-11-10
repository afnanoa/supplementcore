"""Run the supplementCore pipeline: reason, validate, query.

    pip install rdflib owlrl pyshacl
    python run.py

Writes everything it finds to results/.
"""
from pathlib import Path

import owlrl
from pyshacl import validate
from rdflib import Graph

ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

ONTOLOGY = ROOT / "ontology" / "supplementcore.ttl"
SHAPES = ROOT / "shapes" / "supplementcore-shapes.ttl"
GOOD_DATA = ROOT / "data" / "sample-products.ttl"
BAD_DATA = ROOT / "data" / "invalid-products.ttl"


def load(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g


def shacl_check(data_path, label):
    data = load(ONTOLOGY, data_path)
    shapes = load(SHAPES)
    conforms, _, text = validate(
        data,
        shacl_graph=shapes,
        inference="rdfs",       # lets shapes see subclasses and subproperties
        advanced=True,          # enables the SHACL-SPARQL constraints
        allow_warnings=True,
    )
    out = RESULTS / f"validation-{label}.txt"
    out.write_text(text)
    print(f"SHACL {label}: {'conforms' if conforms else 'violations found'} -> {out.name}")
    return conforms


def to_markdown(result):
    cols = [str(v) for v in result.vars]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in result:
        cells = []
        for v in row:
            if v is None:
                cells.append("")
            else:
                s = str(v)
                if s.startswith("https://example.org/supplements/"):
                    s = s.rsplit("/", 1)[-1]
                cells.append(s.replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    # 1. Validate: the sample data should pass, the broken data should not.
    shacl_check(GOOD_DATA, "sample-products")
    shacl_check(BAD_DATA, "invalid-products")

    # 2. Reason: add everything the OWL 2 RL rules can infer.
    g = load(ONTOLOGY, GOOD_DATA)
    before = len(g)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    print(f"Reasoning: {before} triples asserted, {len(g) - before} inferred")

    # 3. Query.
    report = ["# SPARQL query results", "",
              f"Run against the sample data after OWL 2 RL reasoning "
              f"({before} asserted triples, {len(g) - before} inferred).", ""]
    for q in sorted((ROOT / "queries").glob("*.rq")):
        text = q.read_text()
        comment = "\n".join(l[2:] for l in text.splitlines() if l.startswith("# "))
        result = g.query(text)
        report += [f"## {q.name}", "", comment, ""]
        if result.type == "CONSTRUCT":
            out = Graph()
            out.bind("schema", "https://schema.org/")
            for t in result:
                out.add(t)
            ttl = out.serialize(format="turtle")
            (RESULTS / "schemaorg-export.ttl").write_text(ttl)
            report += [f"Built {len(out)} Schema.org triples, saved to "
                       "`results/schemaorg-export.ttl`. First product:", "",
                       "```turtle", ttl.split("\n\n")[1].strip(), "```", ""]
        else:
            report += [to_markdown(result), ""]
        print(f"Query {q.name}: done")
    (RESULTS / "query-results.md").write_text("\n".join(report))


if __name__ == "__main__":
    main()
