> **Historical supporting record — superseded for current release status.** This document records an earlier checkpoint and is retained for audit history. Current authority: `V2.0.0-FINAL-PREDEPLOYMENT-QA.md`, `V2.0.0-RELEASE-AUTHORIZATION.md`, and `V2.0.0-DOCUMENTATION-CLEANUP-QA.md`.

# Branded Predeployment Test Report — v1.1.0

**Status:** PASS — ready for GitHub Pages deployment and live smoke testing  
**Date:** August 1, 2026  
**Data lock:** August 1, 2026

## Release contents

- 250 Source Records
- 240 provisional Canonical Objects
- 101 Price Observations
- 60 Registered Sources
- 58 Public Claims
- 1,910 Claim Items
- 250 Chronology rows
- 15 of 15 release-gate checks passing

## Brand verification

- Official file: `Lititz-BMX-Logo-White-Tire-White-Lettering.png`
- SHA-256: `d685e1e971c9c37af2b914fe1f291f6c94986282a0ab47b0f18ba3f5c3188775`
- Dimensions: 446 × 532 pixels
- Mode: RGBA with transparency
- Prohibited alterations detected: 0
- Lititz BMX is the primary brand; the register title is subordinate.
- The approved logo is used in the masthead and footer with proportional scaling and no crop, glow, shadow, recoloring, outline, or reconstruction.

## Structural and route QA

- Generated HTML pages: 380
- Sitemap URLs: 379
- Duplicate sitemap URLs: 0
- `404.html` entries in sitemap: 0
- Permanent record routes present: 250 of 250
- Permanent claim routes present: 58 of 58
- Permanent source routes present: 60 of 60
- Broken generated internal links or anchors: 0
- Duplicate HTML element IDs: 0
- Escaped literal anchor markup on public indexes: 0
- Homepage inspectable metric cards: 8

Full machine-readable results: `BRANDED-PREDEPLOYMENT-QA.json`.

## Browser and interaction QA

Playwright rendered the generated HTML, CSS, and JavaScript at desktop and mobile viewport sizes. Because outbound browser navigation is blocked in the test sandbox, generated routes were validated separately through the structural link audit.

Passed checks include:

- branded desktop homepage and navigation;
- current-page navigation state;
- original 446 × 532 logo dimensions after load;
- skip link as the first keyboard focus and successful focus transfer to main content;
- claim identity and reconciliation presentation;
- direct correction action;
- records search count, match highlighting, Reset, and restored count;
- EPH-0051 and EPH-0250 headings and breadcrumbs;
- mobile menu visibility, expanded state, Escape-to-close, and 44-pixel-plus touch target;
- mobile table-to-card transformation and visible field labels;
- mobile record-detail presentation;
- browser console errors: 0;
- page JavaScript errors: 0.

Full machine-readable results: `BROWSER-INTERACTION-QA.json`.

## Visual review captures

- `qa-screenshots/home-desktop.png`
- `qa-screenshots/claim-detail-desktop.png`
- `qa-screenshots/records-mobile.png`
- `qa-screenshots/record-detail-mobile.png`

A mobile search-field flex-basis defect discovered during visual review was corrected before this report was finalized. The corrected mobile field now renders at normal control height and exposes the first result card within the opening viewport.

## Live-only release checks

After GitHub Actions deploys the package, verify:

1. Homepage, official logo, grouped navigation, and all eight metric links.
2. Mobile menu behavior in an actual phone browser and any in-app browser used for sharing.
3. `/records/`, `/records/EPH-0051/`, and `/records/EPH-0250/`.
4. `/claims/PKR-CLM-001/`, `/sources/SRC-015/`, and `/validation/`.
5. Workbook and CSV downloads.
6. `sitemap.xml`, `robots.txt`, and browser console/network status.
7. 200% and 400% zoom plus a VoiceOver or TalkBack spot check.

The sitemap and GitHub Release should be published only after these live checks pass.
