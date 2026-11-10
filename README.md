# supplementCore: an ontology for dietary supplement product data

supplementCore models dietary supplement products (what they are, what is in them, how much to take, and who should avoid them) so that both people and machines can use the data. It has four parts:

| Part | File | What it does |
|---|---|---|
| Ontology (OWL) | [`ontology/supplementcore.ttl`](ontology/supplementcore.ttl) | Defines the classes and properties and what they mean |
| Validation rules (SHACL) | [`shapes/supplementcore-shapes.ttl`](shapes/supplementcore-shapes.ttl) | Sets what a complete, correct product record must contain |
| Sample data (RDF) | [`data/`](data/) | Five valid sample products, plus two broken records for testing |
| Queries (SPARQL) | [`queries/`](queries/) | Eight queries that answer real catalog questions |

Results from running everything are in [`results/`](results/).

## Background

This project grew out of a course project at the University of Illinois Urbana-Champaign (Metadata Theory and Practice, Spring 2023). A classmate and I designed [supplementCore as an 18-element XML metadata schema](https://publish.illinois.edu/dietarysupplements/) built on Schema.org and Dublin Core. Here I rebuild it as a linked-data model. The original was an XML Schema, which checks the format of individual records. This version adds an ontology that a reasoner can infer new facts from, SHACL rules that check records, and SPARQL queries over the data.

## Design

**Aligned to existing vocabularies.** Classes and properties map to Schema.org (`schema:Product`, `schema:brand`, `schema:manufacturer`, …) and Dublin Core, so the data can be exported as standard web markup (query 8).

**A category taxonomy in SKOS.** Categories form a hierarchy: *Vitamin › B vitamin*, *Mineral › Trace mineral*, *Herbal › Adaptogen*. A product is filed under its most specific category. Queries walk up the hierarchy with `skos:broader*`, so a search for *Vitamin* also finds B-vitamin products.

**Property inheritance.** `hasActiveIngredient` and `hasInactiveIngredient` are both sub-properties of `hasIngredient`. Data is entered with the specific property, and a query for `hasIngredient` returns both kinds (query 3).

**Inverse properties.** `manufacturer` and `manufactures` are inverses. The data only says which company makes a product; the reasoner works out the other direction (query 7).

**Defined classes.** `PregnancyCautionSupplement` and `AdultOnlySupplement` are defined by their conditions (`owl:equivalentClass` with `owl:hasValue`). No product is tagged with them. The reasoner classifies products automatically (query 5).

**Doses as structured values.** A dose is a node with an amount and a unit (`g`, `mg` or `mcg`), not a text string. That lets rules and queries convert units and compare doses.

### Ontology vs. validation rules

The OWL ontology says what things *mean*; it works on an open-world basis, so a missing brand is not an error to OWL. The SHACL shapes say what a *publishable record* must contain, closed-world, and flag what's missing or wrong. The shapes carry over the cardinalities from the original data dictionary (for example, exactly one brand and SKU, one to three categories) and add rules that plain SHACL can't express, written as SPARQL constraints:

- The recommended intake must not be higher than the maximum intake, after converting both to mg.
- A category must come from the supplementCore category scheme, not a free-text tag.

## Validation results

The five sample products pass. The two broken records in [`data/invalid-products.ttl`](data/invalid-products.ttl) contain eight planted errors, and validation catches all eight ([full report](results/validation-invalid-products.txt)):

| Record | Error caught |
|---|---|
| TUR-BAD | Recommended intake (2,000 mg) is higher than maximum intake (500 mg) |
| TUR-BAD | No brand |
| TUR-BAD | Category "Superfood" is not in the category scheme |
| TUR-BAD | Country of origin "USA" is not a two-letter ISO code |
| zn-bad | Dose unit "IU" is not g, mg or mcg |
| zn-bad | Target population "pregnant" is outside the allowed list |
| zn-bad | SKU has lower-case letters |
| zn-bad | No record date |

## Queries

| Query | Question | Technique |
|---|---|---|
| [01](queries/01-products-in-category.rq) | Which products are vitamins, at any level? | Property path `skos:broader*` |
| [02](queries/02-products-for-minors.rq) | Which products are meant for minors? | Controlled-vocabulary filter, `GROUP_CONCAT` |
| [03](queries/03-all-ingredients.rq) | What are all the ingredients of each product? | Inferred super-property, `COUNT` |
| [04](queries/04-dose-headroom.rq) | How far apart are recommended and maximum doses? | `BIND`, `IF`, unit conversion |
| [05](queries/05-inferred-cautions.rq) | Which products need a pregnancy caution or are adult-only? | Reasoner-inferred classes |
| [06](queries/06-optional-cautions.rq) | List every product, with cautions where they exist | `OPTIONAL` |
| [07](queries/07-manufacturer-portfolio.rq) | What does each manufacturer make, by category? | Inferred inverse property, `GROUP BY` |
| [08](queries/08-construct-schemaorg.rq) | Export products as Schema.org data | `CONSTRUCT` |

See the [results of all eight queries](results/query-results.md).

## Run it yourself

Requires Python 3.9 or later.

```bash
pip install -r requirements.txt
python run.py
```

`run.py` validates both data files with SHACL, runs the OWL 2 RL reasoner, then runs every query and writes the output to `results/`.

You can also open `ontology/supplementcore.ttl` in [Protégé](https://protege.stanford.edu/), run a reasoner, and see the inferred classes in the class hierarchy.

## Note on the data

The brands and companies in the sample data ("Example Labs", "Example Nutrition Co.") are fictional, and the doses and safety notes are sample values for demonstrating the model. They are not health guidance.

---

Afnan Mathew · [LinkedIn](https://www.linkedin.com/in/afnan-mathew)
