# v1.2.0 Rollback Plan

Before the v2.0.0 commit, create and publish a GitHub Desktop branch named:

`rollback-v1.2.0-pre-v2.0.0`

Create it from the current `main` branch before copying any v2.0.0 files. Then switch back to `main` and make the v2.0.0 commit.

If the live release has a blocking fault:

1. In GitHub Desktop, open the History tab on `main`.
2. Right-click the v2.0.0 commit and choose **Revert changes in commit**.
3. Push the revert commit.
4. Confirm the Pages workflow restores the previous public state.

The published rollback branch is an additional preserved copy of the complete pre-v2.0.0 repository state.
