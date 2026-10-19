# .github

Shared GitHub Actions workflows and default community health files
(`SECURITY.md`) for every repository under this account. Every job writes a
report to the run's step summary.

## Reusable Workflow Example

### Build and push to ghcr.io registry

Publishes a multi-platform image to `ghcr.io/<owner>/<repo>`. Create
.github/workflows/build-and-push-image.yml file:
```yaml
name: Build and push image

on:
  push:
    tags: ['*']
  workflow_dispatch:

jobs:
  build-and-push-image:
    permissions:
      contents: read
      packages: write
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
```

### Custom image name, tags and build arguments

`image-name` overrides the default `<owner>/<repo>` path, `enable-semver-tags`
turns off the built-in semver rules so `additional-tags` can define a different
shape, and `build-args` is passed straight through to the Dockerfile:
```yaml
jobs:
  build-and-push-image:
    permissions:
      contents: read
      packages: write
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
    with:
      image-name: chenwei791129/yourip
      enable-semver-tags: false
      additional-tags: |
        type=semver,pattern=v{{version}}
        type=raw,value=alpine,enable={{is_default_branch}}
      build-args: |
        BASE_IMAGE=php
        IMAGE_VERSION=8.4.10-alpine3.22
```

Other inputs: `enable-branch-tag`, `enable-latest-tag`, `context`, `platforms`
(default `linux/amd64,linux/arm64`) and `runs-on`.

### Building an image variant from another Dockerfile

`file` selects a Dockerfile other than `<context>/Dockerfile`. Call the workflow
once per variant, and give each variant's tags a per-rule `suffix=` so they do not
collide with the default image:
```yaml
jobs:
  build-fat:
    permissions:
      contents: read
      packages: write
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
    with:
      file: Dockerfile.fat
      enable-branch-tag: false
      enable-latest-tag: false
      enable-semver-tags: false
      additional-tags: |
        type=semver,pattern={{version}},suffix=-fat
        type=raw,value=fat,enable={{is_default_branch}}
```

Images are pushed to ghcr.io only — Docker Hub support was removed deliberately,
so no registry secrets are needed beyond the automatic `GITHUB_TOKEN`.

### Signing the published image

`sign-image: true` keylessly signs the pushed digest with cosign. The calling job
must additionally grant `id-token: write`, which cosign exchanges for an
ephemeral certificate from the sigstore community Fulcio instance:
```yaml
jobs:
  build-and-push-image:
    permissions:
      contents: read
      packages: write
      id-token: write    # cosign keyless signing
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
    with:
      sign-image: true
```

Signing is skipped on `pull_request`, where nothing is pushed. `cosign-version`
pins the cosign release to install (default `v3.1.3`).

### Trivy vulnerability scan

Create .github/workflows/trivy.yml file:
```yaml
name: Trivy Security Scan

on:
  pull_request:
    branches:
      - main
  schedule:
    - cron: "17 6 * * 1"
  workflow_dispatch:

jobs:
  trivy:
    permissions:
      contents: read           # checkout the repository
      security-events: write   # upload SARIF results to the Security tab
    uses: chenwei791129/.github/.github/workflows/trivy-scan.yml@main
    with:
      scanners: vuln
      severity: HIGH,CRITICAL
      upload-sarif: true
```

`upload-sarif: true` runs an extra non-failing pass and uploads the SARIF
report to the Security tab. The calling job must grant `security-events: write`,
and private repositories additionally need GitHub Advanced Security.

SARIF uploads use category `trivy-<scan-type>` by default (for example,
`trivy-fs` and `trivy-image`), so repository and image scans from the same
calling workflow do not overwrite one another. Existing callers need no changes.
The optional string input `category` overrides this value; omitting it or passing
an empty string uses the default. It only affects SARIF uploads, not the gating
scan or job summary.

When calling the workflow more than once with the same scan type (for example,
two images, or separate vulnerability and secret scans), give each call a
unique, stable category:

```yaml
    with:
      scan-type: image
      scan-ref: ghcr.io/owner/app:latest
      upload-sarif: true
      category: trivy-image-app
```

After adopting this change, verify the distinct analysis categories in the
caller's Security tab after a scheduled or manual run. The initial category
change may leave the old analysis visible; review it separately rather than
assuming the new category removes historical results.

### Trivy secret scan

Create .github/workflows/secret-scan.yml file:
```yaml
name: Secret Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  trivy:
    permissions:
      contents: read
    uses: chenwei791129/.github/.github/workflows/trivy-scan.yml@main
    with:
      scanners: secret
      severity: CRITICAL,HIGH
```

### release-please

Runs [release-please](https://github.com/googleapis/release-please-action) and
exposes its outputs so build/upload jobs can chain on them. Create
.github/workflows/release-please.yml file:
```yaml
name: Release

on:
  push:
    branches: [main]

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

jobs:
  release-please:
    permissions:
      contents: write        # create the release and tag
      issues: write          # label the release PR
      pull-requests: write   # open/update the release PR
    uses: chenwei791129/.github/.github/workflows/release-please.yml@main
    with:
      release-type: go

  build:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created == 'true' }}
    runs-on: ubuntu-26.04
    steps:
      - run: echo "Building ${{ needs.release-please.outputs.tag_name }}"
```

Leave `release-type` empty to use the repository's `release-please-config.json`
and `.release-please-manifest.json` (manifest mode). `target-branch` is needed
only when the default branch is not the one that triggered the workflow (e.g.
`master`). Pass `secrets: { token: ${{ secrets.MY_RELEASE_PLEASE_TOKEN }} }`
when the branch is protected or when the created release must trigger other
workflows; the default `GITHUB_TOKEN` cannot do either.

Outputs: `release_created`, `tag_name`, `version`, `sha`, `html_url`,
`upload_url`, `prs_created`, `pr`.

### Go test

Create .github/workflows/go-test.yml file:
```yaml
name: Test

on:
  push:
    branches-ignore: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    permissions:
      contents: read
    uses: chenwei791129/.github/.github/workflows/go-test.yml@main
```

Inputs: `go-version-file` (default `go.mod`), `working-directory`, `test-args`
(default `./...`; `-count=1` is always added), `vet` (run `go vet` first),
`cache` and `runs-on`.

## References

- [Creating workflow templates for your organization](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates)
- [Reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
