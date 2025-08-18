# .github

## Reusable Workflow Example

reuse build-and-push-image.yml
```yaml
name: Build and push image

on:
  workflow_call:

jobs:
  build-and-push-image:
    uses: chenwei791129/.github/.github/workflows/build-and-push-image.yml@main
```

## References

- [Creating workflow templates for your organization](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates)
- [Reusing workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
