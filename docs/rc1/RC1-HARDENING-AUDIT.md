> **Historical supporting record — superseded for current release status.** This document records an earlier checkpoint and is retained for audit history. Current authority: `V2.0.0-FINAL-PREDEPLOYMENT-QA.md`, `V2.0.0-RELEASE-AUTHORIZATION.md`, and `V2.0.0-DOCUMENTATION-CLEANUP-QA.md`.

# Lititz BMX Public Knowledge Register — v2.0.0 Release Candidate 1

**Status:** PASS — data freeze and export hardening  
**Public deployment:** NO  
**Stable public release:** v1.2.0 — 500 Source Records  
**Frozen v2 baseline:** 1,010 Source Records through EPH-1010  
**Data lock:** August 2, 2026

## Completed in RC1

- Converted the 1,010-record workbook from Working Checkpoint 08 to Release Candidate 1 language.
- Froze expansion and reserved EPH-1011 until the release gate closes.
- Replaced active v1.2 CSV filenames in Public Claims counting rules and source-dataset paths with v2.0.0 filenames.
- Exported nine governed public CSV datasets from the frozen workbook.
- Built a six-layer Universal Search index with **3,879 unique entries**.
- Created controlled review queues for **28 open records**, **235 recurring candidates**, and **20 reviewed duplicate-source occurrences**.
- Created the inventory for **1,010 required permanent Source Record routes**.
- Added an in-workbook Release Gate control sheet.
- Re-imported the exported workbook and confirmed zero formula errors, zero stale Working Checkpoint 08 labels, and zero stale active `v1.2.csv` references.
- Preserved the public v1.2.0 deployment without modification.

## Frozen governed totals

| Layer | Total |
|---|---:|
| Source Records | 1,010 |
| Provisional Canonical Objects | 1,000 |
| Price Observations | 717 |
| Registered Sources | 73 |
| Public Claims | 69 |
| Claim Items | 9,109 |
| Chronology rows | 1,010 |
| Primary Categories | 10 |
| Existing data-validation checks | 20/20 PASS |

## Universal Search RC1

| Layer | Entries |
|---|---:|
| Source Records | 1,010 |
| Canonical Objects | 1,000 |
| Price Observations | 717 |
| Public Claims | 69 |
| Registered Sources | 73 |
| Chronology | 1,010 |
| **Total** | **3,879** |

Exact layer/ID duplication: **0**.

## Release blockers still open

- Review all 28 open or unresolved records for public wording risk.
- Prioritize the highest-risk items from the 235-record recurring-candidate queue.
- Generate and test all 1,010 permanent record routes and aggregate pages.
- Implement the Universal Search interface using the RC1 index.
- Complete site/workbook parity, accessibility, mobile, and performance testing.
- Build the final site overlay, release notes, rollback package, and deployment verification packet.

## Integrity

**Workbook SHA-256:** `467d41982fb7b420293ead2fb18e345ba1b2bacfe80b5f29828e5fc5b0adcc54`

The next governed phase is **RC2 offline site generation and Universal Search UI**. Research expansion remains frozen.
