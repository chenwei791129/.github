# .github

## Reusable Workflow Example

### Build and push to ghcr.io registry
Create .github/workflows/build-and-push-image.yml file:
```yaml
name: Build and push image

on:
  workflow_dispatch:

jobs:
  build-and-push-image:
    permissions:
      contents: read
      packages: write
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
```

### include Docker Hub registry
```yaml
name: Build and push image

on:
  workflow_dispatch:

jobs:
  build-and-push-image:
    permissions:
      contents: read
      packages: write
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
    with:
      dockerhub-repository: your-dockerhub-username/your-repository
      additional-tags: |
        type=raw,value=custom-tag
        type=raw,value=custom-tag2
```

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
