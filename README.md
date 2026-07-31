# Lititz BMX Public Knowledge Register — Ephemera v1.0.0

A claim-visible public register of BMX ephemera, sources, chronology, price observations, and supporting evidence maintained by Lititz BMX.

## Public register

**Website:** https://article134-tech.github.io/lititzbmx-public-knowledge-register/

The site is generated from the repository's CSV data on every push to `main`. Each public claim exposes its counting rule, itemized support, limitations, source pathway, and correction route.

## Release metrics

| Register layer | Count |
|---|---:|
| Source records | 61 |
| Canonical objects | 51 |
| Price observations | 38 |
| Registered sources | 57 |
| Public claim definitions | 57 |
| Claim-item relationships | 521 |
| Chronology rows | 61 |
| Validation checks passing | 14 / 14 |

## Downloads

- [Final claim-visible workbook](downloads/Lititz_BMX_Public_Knowledge_Register_Ephemera_v1.0.0_FINAL.xlsx)
- [Authoritative v0.6–v1.0 ephemera sequence package](downloads/Lititz_BMX_Ephemera_Sequence_v0.6-v1.0_Release_Package.zip)
- [Release checksums](downloads/Lititz_BMX_Public_Knowledge_Register_v1.0.0_SHA256SUMS.txt)

## Evidence chain

`CLAIM → ITEM → EVIDENCE / SOURCE → LIMITATION / STATUS → CORRECTION`

The public user can move from an aggregate claim to the exact records counted, then inspect the source route, confidence, limitations, rights treatment, duplicate decision, and correction pathway.

## Repository structure

- `data/` — public CSV datasets used to generate the site
- `downloads/` — release workbooks, authoritative sequence package, and checksums
- `docs/VALIDATION-REPORT.md` — release-gate validation report
- `site/build.py` — dependency-free static-site generator
- `.github/workflows/pages.yml` — GitHub Pages build and deployment workflow
- `.github/ISSUE_TEMPLATE/record-correction.yml` — structured public correction form

## Rights boundary

The repository preserves metadata, citations, original descriptive text, and public URLs. It does **not** reproduce protected historical scans, catalog pages, advertisements, flyers, publication pages, or BMXMuseum source imagery.

See [RIGHTS.md](RIGHTS.md).

## Corrections

Use the repository's **Record correction** issue form. Please identify the affected Claim ID, record or object ID, proposed correction, and supporting public source.

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).

## Release state

**FINAL WORKBOOK RELEASE**  
Data locked July 30, 2026. Workbook-wide release audit completed July 31, 2026.
