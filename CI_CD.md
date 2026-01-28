# CI/CD Pipeline Documentation

This repository uses GitHub Actions for continuous integration and deployment.

## Workflows

### Test Workflow (`test.yml`)

**Trigger:** Runs on all pull requests and pushes to `main`

**What it does:**
- Tests the code across Python versions 3.10, 3.11, and 3.12
- Installs development dependencies
- Runs pytest with coverage reporting

### Publish Workflow (`publish.yml`)

**Trigger:** Runs when a version tag (e.g., `v0.1.0`, `v1.2.3`) is pushed to the repository

**What it does:**
- Builds source distribution and wheel
- Publishes the package to PyPI using trusted publishing

## How to Release a New Version

1. Update the version in `pyproject.toml`
2. Commit and push the version change: 
   ```bash
   git commit -am "Bump version to X.Y.Z"
   git push
   ```
3. Create and push a tag: 
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
4. The publish workflow will automatically run tests and publish to PyPI

## Setup Requirements

### For Publishing to PyPI

The publish workflow uses PyPI's trusted publishing feature (OIDC). To enable this:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with these settings:
   - PyPI Project Name: `polarseal`
   - Owner: `jwgwalton`
   - Repository name: `PolarSeal`
   - Workflow name: `publish.yml`
   - Environment name: (leave blank)

No API tokens are required with trusted publishing!

## Running Tests Locally

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=polarseal --cov-report=html
```
