# .github

## Reusable Workflow Example

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

## References

- [Creating workflow templates for your organization](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates)
- [Reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
