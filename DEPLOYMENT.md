# v2.0.0 Controlled Deployment

**Deployment authorization:** APPROVED BY KYLE A. HUFFMAN — AUGUST 2, 2026  
**Public site changed by this package:** No

## Exact deployment behavior

A push to `main` triggers `.github/workflows/pages.yml`, runs `python site/build.py`, uploads `_site/`, and deploys the GitHub Pages artifact.

## Pre-push sequence

1. Open the repository in GitHub Desktop.
2. Confirm the repository is `Article134-tech/lititzbmx-public-knowledge-register` and the checked-out branch is `main`.
3. Click **Fetch origin** and confirm there are no incoming changes.
4. Create and publish the rollback branch described in `ROLLBACK-PLAN.md` from the untouched current `main` branch.
5. Switch back to `main`.
6. Extract the authorized deployment ZIP into a separate folder.
7. Copy the **contents inside** the extracted deployment folder into the repository root. Do not add an extra wrapper folder.
8. Allow matching project files to replace their older versions.
9. Review GitHub Desktop's changed-files list. Confirm there are no unrelated changes or deletions.
10. Commit with: `Release Public Knowledge Register v2.0.0`
11. Push origin.

## Live verification after push

Wait for the Pages workflow to complete successfully, then verify:

1. Homepage and the public v2.0.0 release strip.
2. Desktop and phone-width layout.
3. Archive, YouTube, Spotify, Facebook, GitHub, and Donate buttons.
4. Universal Search and the curated Harry Leary; GT, Dyno, Auburn, Robinson; Diamond Back; catalog; advertisement; publication-run; and price entrances.
5. `EPH-0541` opens the indexed source at page 2.
6. `EPH-0604` states pages 77–78 and opens at page 77.
7. `EPH-0602` states that the exact page remains unresolved.
8. Validation page links to the final v2.0.0 QA and release authorization—not RC1 as current authority.
9. Data and download pages.
10. `sitemap.xml`, `robots.txt`, the 404 page, and browser console/network status.

If a release-blocking fault appears, stop further changes and follow `ROLLBACK-PLAN.md` to revert the deployment commit.
