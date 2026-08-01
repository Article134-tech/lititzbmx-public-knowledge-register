# Deployment

The repository uses GitHub Actions to generate and deploy GitHub Pages.

1. Copy the contents of this package into the local repository root.
2. Replace existing files when Windows asks.
3. Review the GitHub Desktop changes.
4. Commit and push to `main`.
5. Wait for the Pages workflow to complete successfully.
6. Verify the live routes listed in `DEPLOY_V1.2.0.md`.
7. Submit the sitemap only after live desktop and mobile checks pass.
8. Publish the GitHub `v1.2.0` Release after the sitemap check.

The generated `_site` directory is intentionally excluded from this package. GitHub Actions rebuilds it from `site/build.py` and the public CSV datasets.
