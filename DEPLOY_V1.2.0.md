# Deploy v1.2.0

## Copy

Extract this package to a short path such as `C:\LBX`.

Copy everything inside the `LBX-v1.2.0-500` folder into:

`Documents\GitHub\lititzbmx-public-knowledge-register`

Choose **Replace the files in the destination**.

## GitHub Desktop

**Summary**

`Deploy v1.2.0 500-record register`

**Description**

`Publishes the audited 500-record register with category browsing, full-dataset filters, sorting, progressive loading, mobile navigation, corrected evidence-source actions, and 20 release-gate checks.`

Commit to `main`, push origin, and wait for the newest Pages workflow to turn green.

## Live verification

Hard-refresh the public site, then verify:

- Homepage shows 500 Source Records, 490 Canonical Objects, 335 Price Observations, 69 Public Claims, and 20 Validation checks.
- `/records/` initially shows 25 records and can load 25 more.
- Search for `EPH-0500` returns exactly one record.
- Category filter `Catalogs and product literature` returns 103 records.
- `/records/EPH-0500/` includes both the register record and original-source action.
- `/claims/PKR-CLM-017/` shows 73 recurring-campaign candidates.
- `/categories/catalogs-product-literature/` shows 103 records.
- `/sources/SRC-065/` opens the October 1983 source route.
- `/validation/` shows 20 passing checks.
- Mobile menu, search, filters, record cards, and claim evidence cards remain readable with no horizontal scrolling.
- `/sitemap.xml` loads and contains the new v1.2.0 routes.

After those checks pass, submit the sitemap in Google Search Console and publish the GitHub `v1.2.0` Release.
