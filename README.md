# .github

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

Images are pushed to ghcr.io only — Docker Hub support was removed deliberately,
so no registry secrets are needed beyond the automatic `GITHUB_TOKEN`.

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

## References

- [Creating workflow templates for your organization](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates)
- [Reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
