# Lititz BMX Public Knowledge Register

**Release:** 1.0.0-rc1  
**Status:** Branded release candidate  
**Target:** `Article134-tech/lititzbmx-docs/lititzbmx-public-knowledge-register/`  
**Branch:** `main`

This package turns the v1.8 evidence schema into a branded, human-readable Lititz BMX interface.

## Public interface

- Branded Lititz BMX header, navigation and footer
- Approved parent-brand hierarchy
- Searchable, filterable register queue
- Itemized catalogs, advertisements, flyers and historical price observations
- Evidence-controlled chronology
- Sources, rights and corrections framework
- Permission-free recovery queue
- Four complete evidence pages: Felicia Stancil GT, JMC Racing, 1990 Haro catalog and Ashtabula reference 5027

## Brand asset

The site references the existing approved parent-repository asset:

`/brand-assets/logos/Lititz-BMX-Logo-Black-Tire-Black-Lettering.png`

Expected SHA-256:

`a2c2b873ded262cc4d448d042ea88b74b5cc96957705d5b6a8f6815329d94506`

The logo is not recreated, recolored, cropped or modified by this package. A plain-text fallback appears only when the site is previewed outside the target repository and the parent asset cannot resolve.

## Deployment boundary

This package adds only the new `public-knowledge-register/` folder. It does not replace or modify existing repository files. Root README integration should occur in a separate commit after the deployed folder is verified.

See `DEPLOYMENT-INSTRUCTIONS.md` for the exact GitHub Desktop handoff.
