# GitHub Actions Release Setup

This guide explains how to configure GitHub repository for automated releases.

## Prerequisites

1. GitHub repository: `romainberthet/optiride`
2. PyPI account: https://pypi.org
3. Maintainer access to the repository

## Configuration Steps

### 1. PyPI Trusted Publishing (Recommended)

This is the most secure method and doesn't require storing API tokens.

1. **Go to PyPI Publishing Settings**:
   - Visit: https://pypi.org/manage/account/publishing/
   - Login with your PyPI credentials

2. **Add GitHub Publisher**:
   - Click "Add a new pending publisher"
   - Fill in the form:
     ```
     PyPI Project Name: optiride
     Owner: romainberthet
     Repository name: optiride
     Workflow name: release.yml
     Environment name: pypi
     ```
   - Click "Add"

3. **Create GitHub Environment**:
   - Go to: https://github.com/romainberthet/optiride/settings/environments
   - Click "New environment"
   - Name: `pypi`
   - Add protection rules (optional):
     - ✅ Required reviewers (for extra safety)
     - ✅ Wait timer: 0 minutes
   - Click "Save"

4. **First Release**:
   - The first time you push a tag, the PyPI project will be created automatically
   - Subsequent releases will publish to the existing project

### 2. API Token Method (Alternative)

If you prefer using API tokens instead of trusted publishing:

1. **Create PyPI API Token**:
   - Go to: https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Token name: `optiride-github-actions`
   - Scope: "Entire account" (for first release) or "Project: optiride" (for subsequent releases)
   - Click "Add token"
   - **IMPORTANT**: Copy the token immediately (starts with `pypi-`)

2. **Add Token to GitHub Secrets**:
   - Go to: https://github.com/romainberthet/optiride/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the token (e.g., `pypi-AgEIcHlwaS5vcmc...`)
   - Click "Add secret"

3. **Update Workflow** (if using token instead of trusted publishing):
   - Edit `.github/workflows/release.yml`
   - In the `publish-pypi` job, uncomment the `password` line:
     ```yaml
     - name: Publish to PyPI
       uses: pypa/gh-action-pypi-publish@release/v1
       with:
         password: ${{ secrets.PYPI_API_TOKEN }}  # Uncomment this line
     ```

### 3. Test PyPI (Optional, for testing)

For testing releases before publishing to production PyPI:

1. **Create Test PyPI API Token**:
   - Go to: https://test.pypi.org/manage/account/token/
   - Create token similar to step 2 above
   - Token name: `optiride-github-actions-test`

2. **Add to GitHub Secrets**:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Test PyPI token

3. **Create TestPyPI Environment**:
   - Go to: https://github.com/romainberthet/optiride/settings/environments
   - Create environment named: `testpypi`

### 4. Verify Setup

1. **Check GitHub Secrets**:
   - Go to: https://github.com/romainberthet/optiride/settings/secrets/actions
   - You should see:
     - ✅ `PYPI_API_TOKEN` (if using token method)
     - ✅ `TEST_PYPI_API_TOKEN` (if using Test PyPI)

2. **Check GitHub Environments**:
   - Go to: https://github.com/romainberthet/optiride/settings/environments
   - You should see:
     - ✅ `pypi` environment
     - ✅ `testpypi` environment (optional)

3. **Check Workflow Permissions**:
   - Go to: https://github.com/romainberthet/optiride/settings/actions
   - Under "Workflow permissions":
     - ✅ Select "Read and write permissions"
     - ✅ Check "Allow GitHub Actions to create and approve pull requests"
   - Click "Save"

## Testing the Release Workflow

### Dry Run (No actual release)

```bash
# Run workflow checks locally
make release-check
```

### Test Release to Test PyPI

```bash
# Create a release candidate
git tag v0.1.0-rc1
git push origin v0.1.0-rc1

# This will:
# - Run all validations
# - Build packages
# - Publish to Test PyPI (if configured)
# - NOT create GitHub Release
# - NOT publish to production PyPI
```

Verify installation from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ optiride
```

### Full Release Test

```bash
# Create a test version
git tag v0.0.1-test
git push origin v0.0.1-test

# Check GitHub Actions:
# - https://github.com/romainberthet/optiride/actions
```

This will trigger the full workflow. You can delete the release afterward:
- Delete tag: `git push origin :refs/tags/v0.0.1-test`
- Delete release: Go to Releases page and delete manually

## Monitoring Releases

### GitHub Actions Dashboard

Monitor workflow runs:
- https://github.com/romainberthet/optiride/actions/workflows/release.yml

### GitHub Releases

View published releases:
- https://github.com/romainberthet/optiride/releases

### PyPI Dashboard

View published packages:
- https://pypi.org/project/optiride/
- https://test.pypi.org/project/optiride/ (Test PyPI)

## Security Best Practices

1. **Use Trusted Publishing** (preferred over API tokens)
2. **Limit Token Scope** to specific project if using tokens
3. **Enable Environment Protection Rules** for production releases
4. **Require Reviews** for release deployments (optional but recommended)
5. **Rotate Tokens** periodically if using API tokens
6. **Monitor Release Activity** via GitHub Actions logs

## Troubleshooting

### "Invalid or non-existent authentication information"

**Cause**: PyPI credentials not configured or invalid

**Solutions**:
1. Verify `PYPI_API_TOKEN` secret is set correctly
2. Regenerate token on PyPI and update secret
3. Ensure token has correct project scope

### "File already exists"

**Cause**: Version already published to PyPI

**Solutions**:
1. Bump version number (you cannot overwrite existing versions)
2. Use a different version number

### "Workflow does not have permission to create releases"

**Cause**: Workflow permissions not configured

**Solutions**:
1. Go to Repository Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Save changes

### "Environment protection rules failed"

**Cause**: Environment protection rules blocking deployment

**Solutions**:
1. Check environment settings at Settings → Environments → pypi
2. Approve deployment if required reviewers are configured
3. Wait for timer if wait timer is configured

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review PyPI project settings
3. Consult GitHub Actions documentation: https://docs.github.com/en/actions
4. PyPI Publishing documentation: https://docs.pypi.org/trusted-publishers/

---

**Last Updated**: 2025-10-25
**Maintained By**: Romain BERTHET (berthet.romain3@gmail.com)
