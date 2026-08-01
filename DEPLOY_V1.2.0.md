# Finalize v1.2.0

## Copy

Copy everything inside the finalization-patch folder into:

`Documents\GitHub\lititzbmx-public-knowledge-register`

Choose **Replace the files in the destination**.

Then delete:

`downloads\Lititz_BMX_Public_Knowledge_Register_Ephemera_v1.2.0_RELEASE_CANDIDATE.xlsx`

## GitHub Desktop

**Summary**

`Finalize v1.2.0 public release`

**Description**

`Removes deployment-candidate language, publishes the final v1.2.0 workbook filename, and refreshes release metadata and checksums without changing the 500-record dataset.`

Commit to `main`, push origin, and wait for the newest Pages workflow to turn green.

## Live verification

- Header says `Final 500-record release`.
- Homepage still shows 500 Source Records, 490 Canonical Objects, 335 Price Observations, 69 Public Claims, and 20 Validation checks.
- The workbook button downloads `Lititz_BMX_Public_Knowledge_Register_Ephemera_v1.2.0_FINAL.xlsx`.
- `EPH-0500`, `PKR-CLM-017`, category routes, Sources, Validation, and the sitemap still open.

After those checks pass, submit the sitemap and publish the GitHub `v1.2.0` Release.
