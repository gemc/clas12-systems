# GitHub Actions workflows

This directory contains the CI, deployment, release, and maintenance workflows for the CLAS12 GEMC systems.
The [GEMC workflow guide][src-workflows] is the authoritative description of the complete
`pygemc -> src -> clas12-systems` dependency chain.

## Deployment paths

A change made directly in this repository follows this path:

```text
clas12-systems push to main
  -> Test
  -> Deploy
  -> Binary Tarballs
```

A new GEMC deployment rebuilds the derived CLAS12 images even when this repository has no new commit:

```text
gemc/src Deploy
  -> API dispatch of Test after gemc/src deploy
  -> reusable jobs from Test
  -> Deploy
  -> Binary Tarballs
```

`Deploy` accepts only successful, same-repository runs on `main` with one of these workflow/event pairs:

- `Test` with a `push` event.
- `Test after gemc/src deploy` with a `workflow_dispatch` event.

The compatibility workflow can also be run from the Actions page. A successful manual run on `main` is
deployment-authorized and therefore rebuilds the CLAS12 images.

## Build, test, and deployment workflows

- [`test.yml`](test.yml) — **Test**
  - Trigger: pull requests, merge queue runs, pushes to `main`, tag pushes, and `workflow_call`.
  - Effect: builds and tests the CLAS12 systems inside the supported GEMC image matrix.
  - Downstream: `Deploy` only for a successful push to `main`.
- [`test_after_src.yml`](test_after_src.yml) — **Test after gemc/src deploy**
  - Trigger: API or manual `workflow_dispatch`; the upstream dispatcher selects `main`.
  - Effect: calls the reusable jobs in `test.yml` against freshly deployed GEMC images.
  - Downstream: `Deploy` after success.
- [`deploy.yml`](deploy.yml) — **Deploy**
  - Trigger: completion of either approved Test workflow on `main`.
  - Effect: builds per-architecture CLAS12 images, publishes manifests to GHCR, and summarizes the matrix.
  - Downstream: `Binary Tarballs` after completion.
- [`binary_tarballs.yml`](binary_tarballs.yml) — **Binary Tarballs**
  - Trigger: completion of `Deploy`.
  - Effect: after a successful same-repository deployment, smoke-tests the published image matrix.
- [`sanitize.yml`](sanitize.yml) — **Sanitize**
  - Trigger: pull requests plus pushes to `main` and `v*` tags.
  - Effect: runs the sanitizer matrix and uploads sanitizer logs.
- [`pr-docker-image.yml`](pr-docker-image.yml) — **PR Docker Image**
  - Trigger: pull request open, update, reopen, and close events.
  - Effect: publishes an AlmaLinux preview image for an open PR and deletes it when the PR closes.

## Detector comparison workflows

- [`clas12_geo_compare.yml`](clas12_geo_compare.yml) — **Clas12 Geo Comparison**
  - Trigger: non-Markdown pull requests and pushes to `main`, or manual dispatch.
  - Effect: compares generated GEMC3 geometry and materials with the `clas12Tags` reference databases.
- [`hipo_histos_compare.yml`](hipo_histos_compare.yml) — **HIPO Histos Comparison**
  - Trigger: relevant detector/plugin paths on pull requests and pushes to `main`, or manual dispatch.
  - Effect: compares GEMC3 digitized HIPO output with rolling `clas12Tags` references.
  - Publication: non-PR runs update the rolling `histo-gemc3` release assets.

## Release, documentation, and maintenance workflows

- [`macos_tarball.yml`](macos_tarball.yml) — **macOS CLAS12 Systems Tarball**
  - Trigger: daily at 07:00 UTC or manual dispatch.
  - Effect: builds and tests against the GEMC and Geant4 macOS tarballs, then updates the selected release.
- [`dev_release.yml`](dev_release.yml) — **Nightly Dev Release**
  - Trigger: daily at 01:44 UTC or manual dispatch.
  - Effect: moves the `dev` tag and updates the development prerelease.
- [`doxygen.yml`](doxygen.yml) — **Doxygen**
  - Trigger: non-Markdown pushes to any branch or manual dispatch.
  - Effect: builds documentation and deploys GitHub Pages from `main`.
- [`codeql.yml`](codeql.yml) — **CodeQL Advanced**
  - Trigger: pushes and pull requests plus the Friday 02:20 UTC schedule.
  - Effect: performs security analysis for the configured languages.
- [`cleanup.yml`](cleanup.yml) — **Cleanup old artifacts and GHCR images**
  - Trigger: daily at 03:00 UTC or manual dispatch, with a dry-run option.
  - Effect: removes expired artifacts, stale managed image tags, and unreferenced child manifests.
- [`rerun_failed_matrix.yml`](rerun_failed_matrix.yml) — **Retry Failed Matrix Jobs**
  - Trigger: completion of Test, Sanitize, Deploy, Binary Tarballs, or the macOS tarball workflow.
  - Effect: on attempt 1, retries failed jobs only when the run failed or timed out and at least half of the
    counted matrix jobs succeeded.

## Cross-repository contracts

These names and paths are interfaces, not cosmetic labels:

- `gemc/src` dispatches the file `test_after_src.yml`; renaming it requires changing
  `gemc/src/.github/workflows/trigger_c12s_tests.yml`.
- `Deploy` matches the exact workflow names `Test` and `Test after gemc/src deploy`.
- `test_after_src.yml` calls `test.yml` through `workflow_call`; keep the shared build matrix in `test.yml`.
- The cross-repository `CLAS12_SYSTEMS_PAT` secret is owned by `gemc/src`, not by this repository.

## Permissions and published state

Most workflows default to read-only repository access. Publishing jobs elevate only the permissions they need:

- Deploy and PR preview jobs write GHCR packages.
- Release workflows write release assets and tags.
- Documentation deployment writes GitHub Pages.
- Cleanup can delete Actions artifacts and managed GHCR package versions.
- Retry uses `actions: write` to rerun failed jobs.

Treat changes to these jobs as changes to external published state.

## Concurrency, retries, and skipped runs

Long-running workflows use concurrency groups with `cancel-in-progress: true`, so a newer run for the same ref
or source run can cancel older work.

GitHub creates a `workflow_run` workflow before evaluating its job-level `if`. Consequently,
`Retry Failed Matrix Jobs` appears as skipped after successful watched workflows. This is expected. Failed
Deploy runs can similarly create a gated Binary Tarballs run. The normal and GEMC-triggered successful
deployment paths do not create skipped Deploy or Binary Tarballs runs.

## Safe workflow changes

When changing a cross-repository workflow filename or displayed `name`:

1. Add the new target workflow first.
2. Update every caller and `workflow_run.workflows` list.
3. Remove the old entry point only after the callers are deployed.
4. Keep the same-repository, branch, conclusion, workflow-name, and event checks on privileged workflows.
5. Validate YAML, line wrapping, and `git diff --check` before pushing.

For coordinated changes to this chain, publish `clas12-systems` before `src`, and `src` before `pygemc`.

[src-workflows]: https://github.com/gemc/src/blob/main/.github/workflows/README.md
