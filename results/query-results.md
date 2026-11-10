# SPARQL query results

Run against the sample data after OWL 2 RL reasoning (344 asserted triples, 738 inferred).

## 01-products-in-category.rq

Q1. Every vitamin product, including products filed under narrower
categories (B vitamin, fat-soluble vitamin).
Shows: a SKOS taxonomy walked with the property path skos:broader*.

| sku | title | categoryLabel |
|---|---|---|
| B12-800 | Vitamin B12 800 mcg | B vitamin |
| D3-1000 | Vitamin D3 1,000 IU (25 mcg) | Fat-soluble vitamin |

## 02-products-for-minors.rq

Q2. Products whose target population includes minors.
Shows: filtering on a controlled vocabulary.

| sku | title | populations |
|---|---|---|
| D3-1000 | Vitamin D3 1,000 IU (25 mcg) | Adults, Minors |

## 03-all-ingredients.rq

Q3. Every ingredient of every product, active or inactive.
Shows: property inheritance. The data only uses hasActiveIngredient
and hasInactiveIngredient; after reasoning, both are also
hasIngredient, so one query finds them all.

| sku | ingredientCount | ingredients |
|---|---|---|
| ASH-600 | 2 | Ashwagandha root extract; Hypromellose (vegetable capsule) |
| B12-800 | 2 | Hypromellose (vegetable capsule); Methylcobalamin (vitamin B12) |
| D3-1000 | 2 | Sunflower oil; Cholecalciferol (vitamin D3) |
| LI-1 | 2 | Lithium orotate; Hypromellose (vegetable capsule) |
| MG-200 | 2 | Hypromellose (vegetable capsule); Magnesium glycinate |

## 04-dose-headroom.rq

Q4. Recommended vs. maximum intake, converted to mg, with the
headroom between them.
Shows: BIND, IF and arithmetic to normalize units in the query.

| sku | recommendedMg | maximumMg | headroomRatio |
|---|---|---|---|
| LI-1 | 1.0 | 1.0 | 1 |
| ASH-600 | 600.0 | 1000.0 | 1.67 |
| MG-200 | 200.0 | 350.0 | 1.75 |
| B12-800 | 0.8 | 1.6 | 2 |
| D3-1000 | 0.025 | 0.1 | 4 |

## 05-inferred-cautions.rq

Q5. Products the reasoner classified as needing a pregnancy caution
or as adult-only. No product is tagged with these classes directly.
Shows: OWL defined classes (equivalentClass + hasValue) and inference.

| sku | title | inferredClass |
|---|---|---|
| ASH-600 | Ashwagandha Root Extract 600 mg | Adult-only supplement |
| ASH-600 | Ashwagandha Root Extract 600 mg | Supplement with pregnancy caution |
| LI-1 | Lithium Orotate 1 mg | Adult-only supplement |
| LI-1 | Lithium Orotate 1 mg | Supplement with pregnancy caution |

## 06-optional-cautions.rq

Q6. All products, with any "not recommended for" population when
one exists.
Shows: OPTIONAL, so products without a caution still appear.

| sku | title | notRecommendedFor |
|---|---|---|
| ASH-600 | Ashwagandha Root Extract 600 mg | Pregnant or lactating |
| B12-800 | Vitamin B12 800 mcg |  |
| D3-1000 | Vitamin D3 1,000 IU (25 mcg) |  |
| LI-1 | Lithium Orotate 1 mg | Pregnant or lactating |
| MG-200 | Magnesium Glycinate 200 mg |  |

## 07-manufacturer-portfolio.rq

Q7. What each manufacturer makes, counted by top-level category.
Shows: an inverse property (sc:manufactures is never written in the
data; the reasoner derives it from sc:manufacturer) plus aggregation.

| manufacturer | topCategory | products |
|---|---|---|
| Example Nutrition Co. | Vitamin | 2 |
| Example Nutrition Co. | Mineral | 2 |
| Example Nutrition Co. | Herbal | 1 |

## 08-construct-schemaorg.rq

Q8. Rebuild each product as Schema.org data, ready for web markup.
Shows: CONSTRUCT, which outputs a new RDF graph instead of a table.

Built 30 Schema.org triples, saved to `results/schemaorg-export.ttl`. First product:

```turtle
<https://example.org/supplements/ASH-600> a schema:DietarySupplement ;
    schema:activeIngredient "Ashwagandha root extract" ;
    schema:brand "Example Labs" ;
    schema:countryOfOrigin "IN" ;
    schema:name "Ashwagandha Root Extract 600 mg" ;
    schema:sku "ASH-600" .
```
