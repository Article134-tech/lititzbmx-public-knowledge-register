> **Historical supporting record — superseded for current release status.** This document records an earlier checkpoint and is retained for audit history. Current authority: `V2.0.0-FINAL-PREDEPLOYMENT-QA.md`, `V2.0.0-RELEASE-AUTHORIZATION.md`, and `V2.0.0-DOCUMENTATION-CLEANUP-QA.md`.

# v2.0.0 Release-Gate Checklist

## A. Frozen data baseline

- [x] Freeze Source Records at EPH-1010.
- [x] Preserve all existing stable IDs.
- [x] Reconcile 1,010 Source Records, 1,000 provisional Canonical Objects, 717 Price Observations, 73 sources, 69 claims, 9,109 Claim Items, and 1,010 Chronology rows.
- [x] Convert active public dataset filenames from v1.2 to v2.0.0.
- [x] Export public CSV tables from the frozen workbook.

## B. Research-risk triage

- [ ] Review all 28 open or unresolved records.
- [ ] Review release-risk recurring candidates from the 235-record disclosed queue.
- [x] Preserve the ten reviewed duplicate groups without deleting source occurrences.
- [ ] Confirm no public wording overstates image-dependent, translated, or page-layout evidence.

## C. Static site generation

- [ ] Generate 1,010 permanent Source Record routes.
- [ ] Regenerate Canonical Objects, Price Observations, Public Claims, Sources, Chronology, and Category views.
- [ ] Preserve every v1.2.0 public route.
- [ ] Confirm every evidence and correction action resolves correctly.

## D. Universal Search

- [x] Build the six-layer RC1 index.
- [x] Validate 3,879 unique layer/ID entries.
- [x] Run ID, person, brand, publication, and geography smoke queries.
- [ ] Implement the accessible search interface.
- [ ] Test grouped results, filters, keyboard operation, empty states, and progressive rendering.

## E. Accessibility, mobile, and performance

- [ ] Validate heading structure and landmark labels.
- [ ] Validate keyboard focus order and visible focus.
- [ ] Validate form labels and live result announcements.
- [ ] Validate contrast and zoom behavior.
- [ ] Test narrow Android and iPhone viewport widths.
- [ ] Test desktop browsers and hard refresh behavior.
- [ ] Benchmark initial load, index load, search response, and progressive rendering.

## F. Release packaging and deployment

- [x] Create RC1 workbook, data exports, review queues, search index, manifest, and checksums.
- [ ] Add the offline site overlay to the release candidate.
- [ ] Complete workbook/site parity report.
- [ ] Create final release notes and changelog.
- [ ] Preserve a rollback copy of v1.2.0.
- [ ] Deploy once after every blocking gate passes.
- [ ] Verify the live homepage, search, representative records, sources, claims, categories, mobile layout, and downloadable assets.
- [ ] Create the GitHub v2.0.0 release only after live verification.
