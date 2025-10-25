# Release Process

This document describes how to create and publish a new release of OptiRide.

## Quick Start

### Creating a Release

OptiRide uses automated releases via GitHub Actions. To create a new release:

```bash
# 1. Create a patch release (0.1.0 -> 0.1.1)
make release-patch

# OR create a minor release (0.1.0 -> 0.2.0)
make release-minor

# OR create a major release (0.1.0 -> 1.0.0)
make release-major

# 2. Update CHANGELOG.md with the new version

# 3. Commit and create tag
make release-tag

# 4. Push to trigger automated release
git push origin main
git push origin v<version>
```

The GitHub Actions workflow will automatically:
- Validate code quality (lint, format, type-check)
- Run full test suite
- Build distribution packages (wheel + sdist)
- Create GitHub Release with changelog
- Publish to PyPI

## Detailed Process

### Step 1: Pre-Release Checks

Before creating a release, ensure everything is ready:

```bash
# Run all quality checks and tests
make release-check
```

This will:
- ✅ Run `ruff` linting and formatting checks
- ✅ Run `mypy` type checking
- ✅ Run full test suite with coverage
- ✅ Build distribution packages
- ✅ Validate package with `twine check`

### Step 2: Version Bump

Choose the appropriate version bump based on [Semantic Versioning](https://semver.org/):

- **Patch** (0.1.0 → 0.1.1): Bug fixes, documentation updates
- **Minor** (0.1.0 → 0.2.0): New features, backward-compatible changes
- **Major** (0.1.0 → 1.0.0): Breaking changes

```bash
# Patch release
make release-patch

# Minor release
make release-minor

# Major release
make release-major
```

This will:
1. Run `release-check` to validate everything
2. Bump version in `pyproject.toml`
3. Display next steps

### Step 3: Update CHANGELOG.md

Add a new section at the top of `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature A
- New feature B

### Changed
- Improvement C
- Improvement D

### Fixed
- Bug fix E
- Bug fix F

### Deprecated
- Deprecated feature G

### Removed
- Removed feature H

### Security
- Security fix I
```

**Template:**
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- List new features

### Changed
- List changes to existing functionality

### Fixed
- List bug fixes
```

### Step 4: Create and Push Tag

```bash
# Create tag locally
make release-tag

# This will:
# 1. Commit version bump and changelog
# 2. Create annotated git tag v<version>
# 3. Display push instructions

# Push to GitHub to trigger release
git push origin main
git push origin v<version>
```

### Step 5: Automated Release (GitHub Actions)

Once the tag is pushed, GitHub Actions will automatically:

1. **Validate** (`validate` job):
   - Run linting with ruff
   - Run type checking with mypy
   - Run full test suite

2. **Build** (`build` job):
   - Build wheel and source distribution
   - Check packages with twine
   - Upload artifacts

3. **Create GitHub Release** (`github-release` job):
   - Extract changelog for this version
   - Create release on GitHub
   - Attach wheel and source distribution files

4. **Publish to PyPI** (`publish-pypi` job):
   - Publish to PyPI using trusted publishing
   - Package becomes available at https://pypi.org/project/optiride/

## PyPI Configuration

### First-Time Setup

1. **Create PyPI Account**:
   - Go to https://pypi.org/account/register/
   - Verify your email

2. **Configure Trusted Publishing** (recommended):
   - Go to https://pypi.org/manage/account/publishing/
   - Add new publisher:
     - PyPI Project Name: `optiride`
     - Owner: `romainberthet`
     - Repository: `optiride`
     - Workflow: `release.yml`
     - Environment: `pypi`

3. **OR Create API Token** (alternative):
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope limited to `optiride` project
   - Add to GitHub Secrets as `PYPI_API_TOKEN`

### Test PyPI (for testing)

For release candidates, use Test PyPI:

```bash
# Tag with -rc suffix
git tag v0.1.0-rc1
git push origin v0.1.0-rc1

# Workflow will detect -rc and publish to TestPyPI
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ optiride
```

## Manual Release (Emergency Only)

If GitHub Actions is down or there's an issue:

```bash
# 1. Build package
make clean build

# 2. Check package
make check-build

# 3. Test on TestPyPI first
make publish-test

# 4. Verify it works
pip install --index-url https://test.pypi.org/simple/ optiride

# 5. Publish to PyPI
make publish
```

## Release Checklist

Use this checklist for each release:

- [ ] All tests passing locally (`make test-cov`)
- [ ] Code quality checks pass (`make quality`)
- [ ] CHANGELOG.md updated with new version
- [ ] Version bumped in `pyproject.toml`
- [ ] All changes committed
- [ ] Tag created (`make release-tag`)
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow completed successfully
- [ ] GitHub Release created with correct changelog
- [ ] Package published to PyPI
- [ ] Package installable: `pip install optiride==<version>`
- [ ] Post-release announcement (optional)

## Hotfix Releases

For urgent bug fixes on a released version:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/0.1.1 v0.1.0

# 2. Fix the bug and commit
git commit -m "Fix critical bug X"

# 3. Bump version
make release-patch

# 4. Update CHANGELOG.md

# 5. Create tag
make release-tag

# 6. Push
git push origin hotfix/0.1.1
git push origin v0.1.1

# 7. Merge back to main
git checkout main
git merge hotfix/0.1.1
git push origin main
```

## Rollback

If a release has issues:

```bash
# 1. Delete the tag
git tag -d v<version>
git push origin :refs/tags/v<version>

# 2. Delete the GitHub Release (manual via GitHub UI)

# 3. Yank the PyPI release (if published)
# Go to https://pypi.org/manage/project/optiride/releases/
# Click "Options" -> "Yank release"

# 4. Fix issues and create new patch release
```

## Versioning Guidelines

OptiRide follows [Semantic Versioning](https://semver.org/):

**MAJOR.MINOR.PATCH**

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New features, backward-compatible
- **PATCH** (0.0.1): Bug fixes, backward-compatible

**Pre-release versions:**
- `v1.0.0-alpha.1`: Alpha release
- `v1.0.0-beta.1`: Beta release
- `v1.0.0-rc.1`: Release candidate

## Troubleshooting

### GitHub Actions Fails

1. Check the logs at: https://github.com/romainberthet/optiride/actions
2. Common issues:
   - Tests failing: Fix tests and create new patch
   - Build fails: Check `pyproject.toml` syntax
   - PyPI publish fails: Check credentials/tokens

### PyPI Upload Fails

- **Error: File already exists**: Version already published, bump version
- **Error: Invalid credentials**: Check `PYPI_API_TOKEN` in GitHub Secrets
- **Error: Invalid package**: Run `twine check dist/*` locally

### Tag Already Exists

```bash
# Delete local tag
git tag -d v<version>

# Delete remote tag
git push origin :refs/tags/v<version>

# Create new tag
make release-tag
```

## Support

For questions about releases:
- Open an issue: https://github.com/romainberthet/optiride/issues
- Email: berthet.romain3@gmail.com
