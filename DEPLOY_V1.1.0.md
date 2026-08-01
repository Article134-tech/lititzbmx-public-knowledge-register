# Deploy the v1.1.0 Branded Release Candidate

Do not deploy the earlier working-census or unbranded candidate packages.

1. Extract this package.
2. Copy all files and folders into the local `lititzbmx-public-knowledge-register` repository.
3. Replace files when prompted.
4. Commit summary: `Deploy branded v1.1.0 register`
5. Commit description: `Publishes the audited 250-record release candidate with LBS-004 branding, product navigation, mobile cards, breadcrumbs, inspectable metrics, accessible search, and correction routes.`
6. Push origin and wait for the Pages workflow to finish green.
7. Complete the live checks in `docs/BRANDED-PREDEPLOYMENT-TEST-REPORT.md`.
8. Submit the sitemap and publish the v1.1.0 GitHub Release only after live checks pass.
