# Deployment Instructions

## What this package does

This repository package uses a GitHub Actions workflow to generate every public claim, record, source, object, price, chronology, validation, data, and download page. The generated site is deployed to GitHub Pages.

This avoids GitHub's browser limit of 100 uploaded files at one time while still creating all stable URLs embedded in the workbook.

## Upload

1. Extract `Lititz_BMX_Public_Knowledge_Register_v1.0.0_GitHub_Deployment.zip`.
2. Open the extracted deployment folder.
3. In the GitHub repository, select **Add file → Upload files**.
4. Drag **all files and folders inside the deployment folder** into the upload area. Do not upload the outer ZIP as the repository contents.
5. Confirm the upload list includes `.github`, `data`, `docs`, `downloads`, `site`, and the root Markdown/JSON files.
6. Commit message: `Deploy Lititz BMX Public Knowledge Register v1.0.0`
7. Commit directly to the `main` branch.

## Enable GitHub Pages

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Return to the **Actions** tab.
4. Open the `Deploy Lititz BMX Public Knowledge Register` workflow.
5. Confirm the build and deploy jobs complete successfully.

The public address will be:

`https://article134-tech.github.io/lititzbmx-public-knowledge-register/`

## Verify before creating the release

Test:

- `/claims/PKR-CLM-001/`
- `/records/EPH-0001/`
- `/objects/index.html#OBJ-0001`
- `/prices/index.html#BM-PRICE-0001`
- `/sources/SRC-001/`
- `/chronology/index.html#CHR-001`
- `/validation/`
- `/downloads/Lititz_BMX_Ephemera_Sequence_v0.6-v1.0_Release_Package.zip`

## Create GitHub Release v1.0.0

After the site is verified:

1. Select **Releases → Create a new release**.
2. Choose **Create new tag** and enter `v1.0.0`.
3. Target: `main`.
4. Release title: `Lititz BMX Public Knowledge Register — Ephemera v1.0.0`
5. Paste the contents of `RELEASE_NOTES_v1.0.0.md`.
6. Attach the final workbook and the authoritative sequence ZIP from `downloads/`.
7. Publish the release.
