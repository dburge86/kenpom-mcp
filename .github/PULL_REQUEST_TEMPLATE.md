## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
<!-- Put an 'x' in the boxes that apply -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Test coverage improvement
- [ ] Performance improvement

## Related Issues
<!-- Link related issues here using #issue_number -->
Fixes #
Related to #

## Changes Made
<!-- Provide a bullet-point list of specific changes -->
-
-
-

## Testing
<!-- Describe the tests you ran to verify your changes -->

### Test Coverage
- [ ] Added new tests for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

### Test Commands Run
```bash
# Example:
uv run pytest tests/
uv run ruff check src/ tests/
```

### Test Results
```
# Paste test output here
```

## Documentation
- [ ] Updated README.md (if needed)
- [ ] Updated CLAUDE.md (if needed)
- [ ] Added/updated docstrings
- [ ] Created/updated ADR (for architectural changes)

## Checklist
<!-- Put an 'x' in all boxes that apply -->
- [ ] My code follows the project's code style (ruff)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] I have not committed any credentials or secrets
- [ ] I have updated the documentation accordingly
- [ ] Pre-commit hooks pass (`uv run pre-commit run --all-files`)

## Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->

## Additional Notes
<!-- Any additional information reviewers should know -->

## Breaking Changes
<!-- If this is a breaking change, describe the migration path for users -->

---

**Before submitting:**
1. Run `uv run pytest tests/` - all tests must pass
2. Run `uv run ruff check src/ tests/` - no linting errors
3. Run `uv run ruff format src/ tests/` - code properly formatted
4. Verify no secrets/credentials in your changes
