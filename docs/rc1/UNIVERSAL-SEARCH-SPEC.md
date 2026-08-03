> **Historical supporting record — superseded for current release status.** This document records an earlier checkpoint and is retained for audit history. Current authority: `V2.0.0-FINAL-PREDEPLOYMENT-QA.md`, `V2.0.0-RELEASE-AUTHORIZATION.md`, and `V2.0.0-DOCUMENTATION-CLEANUP-QA.md`.

# Lititz BMX Public Knowledge Register — Universal Search Specification

**Release target:** v2.0.0  
**Index candidate:** RC1  
**Frozen corpus:** 1,010 Source Records  
**Index entries:** 3,879

## Purpose

Provide one persistent public search that works across six governed layers without exposing hidden build-time fields.

## Indexed layers

| Layer | Entries | Primary destination |
|---|---:|---|
| Source Records | 1,010 | `/records/EPH-####/` |
| Canonical Objects | 1,000 | `/objects/` anchors |
| Price Observations | 717 | `/prices/` anchors |
| Public Claims | 69 | `/claims/PKR-CLM-###/` |
| Registered Sources | 73 | `/sources/SRC-###/` |
| Chronology | 1,010 | `/chronology/` anchors |

## Searchable public fields

ID, title, brand or promoter, year and date text, object type, primary category, geography, public status, public summary or limitation, source identity, and public source domain.

The index excludes normalized duplicate keys, internal-only implementation fields, copied historical page content, and personal contact details.

## Required behavior

1. One search field in the shared site header and on the register landing page.
2. Case-insensitive and diacritic-insensitive matching.
3. Exact ID matches rank first.
4. Multiple query terms use AND matching.
5. Results are grouped or filterable by the six governed layers.
6. Each result displays its layer, stable ID, title, short public context, status, and destination.
7. Keyboard support: focusable field, Escape to clear/close, arrow-key result movement, Enter to open.
8. Accessible live result count and explicit empty-state text.
9. Results must not depend on network APIs after the static index has loaded.
10. Search must preserve the existing correction and evidence pathways rather than creating unsupported summaries.

## RC1 smoke tests

```json
{
  "EPH-1010": {
    "count": 3,
    "top_ids": [
      "EPH-1010",
      "OBJ-1000",
      "CHR-1010"
    ]
  },
  "Harry Leary": {
    "count": 28,
    "top_ids": [
      "OBJ-0275",
      "OBJ-0570",
      "OBJ-0247",
      "OBJ-0167",
      "OBJ-0611"
    ]
  },
  "Mongoose": {
    "count": 183,
    "top_ids": [
      "OBJ-0034",
      "OBJ-0035",
      "OBJ-0882",
      "OBJ-0036",
      "OBJ-0612"
    ]
  },
  "Bicross": {
    "count": 197,
    "top_ids": [
      "OBJ-0996",
      "OBJ-0921",
      "OBJ-0877",
      "OBJ-0865",
      "OBJ-0824"
    ]
  },
  "France": {
    "count": 315,
    "top_ids": [
      "OBJ-0824",
      "OBJ-0804",
      "OBJ-0825",
      "OBJ-0893",
      "OBJ-0949"
    ]
  }
}
```

## Performance target

The compressed static index should load once, then filter locally. Initial page rendering must remain usable before the search index finishes loading. Large result sets should be progressively rendered rather than injected all at once.
