> **Historical supporting record — superseded for current release status.** This document records an earlier checkpoint and is retained for audit history. Current authority: `V2.0.0-FINAL-PREDEPLOYMENT-QA.md`, `V2.0.0-RELEASE-AUTHORIZATION.md`, and `V2.0.0-DOCUMENTATION-CLEANUP-QA.md`.

# Site-Build Handoff

## Authoritative public repository

- Repository: `https://github.com/Article134-tech/lititzbmx-public-knowledge-register`
- Public site: `https://article134-tech.github.io/lititzbmx-public-knowledge-register/`
- Current stable public release: v1.2.0 — 500 Source Records
- v2.0.0 state: offline Release Candidate 1; no deployment authorized

## Current repository structure to preserve

The current main branch exposes the top-level `data`, `docs`, `downloads`, and `site` directories, along with release documentation and a root release manifest. The v2.0.0 build should be an offline overlay against that structure, not a replacement with an unrelated repository layout.

## RC1 inputs for the site generator

- `data/ephemera-register-v2.0.0.csv`
- `data/canonical-objects-v2.0.0.csv`
- `data/price-observations-v2.0.0.csv`
- `data/source-register-v2.0.0.csv`
- `data/source-usage-v2.0.0.csv`
- `data/chronology-v2.0.0.csv`
- `data/public-claims-v2.0.0.csv`
- `data/claim-items-v2.0.0.csv`
- `data/category-register-v2.0.0.csv`
- `data/universal-search-index-v2.0.0-rc1.json`

## Next build pass

1. Obtain or export the current repository main branch as a local source snapshot.
2. Build the v2.0.0 overlay offline from the frozen RC1 datasets.
3. Generate all routes and aggregate pages.
4. Implement Universal Search using the RC1 index.
5. Run route, parity, accessibility, mobile, performance, and rights-boundary tests.
6. Package the tested overlay without changing the public v1.2.0 deployment.
