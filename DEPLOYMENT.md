# Deployment

The repository uses GitHub Actions to generate and deploy GitHub Pages.

1. Copy the v1.2.0 finalization patch into the local repository root.
2. Replace matching files when Windows asks.
3. Delete the obsolete v1.2.0 `RELEASE_CANDIDATE` workbook from `downloads/`.
4. Review the GitHub Desktop changes.
5. Commit and push to `main`.
6. Wait for the Pages workflow to complete successfully.
7. Confirm the live header says **Final 500-record release** and the download opens the `FINAL.xlsx` workbook.
8. Submit the sitemap in Google Search Console.
9. Publish the GitHub `v1.2.0` Release.

The generated `_site` directory is intentionally excluded. GitHub Actions rebuilds it from `site/build.py` and the public CSV datasets.
