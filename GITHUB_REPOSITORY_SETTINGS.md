# GitHub Repository Settings & Metadata

**Repository**: ORION-Architekt-AT
**Last Updated**: 2026-04-06

---

## Repository Topics (GitHub Tags)

Add these topics via GitHub repository settings → "Topics":

### Primary Topics
- `austrian-building-codes`
- `eurocode-5`
- `structural-engineering`
- `safety-validation`
- `ai-safety`
- `building-compliance`

### Technology Topics
- `python`
- `cpp`
- `cmake`
- `iso-26262`
- `eu-ai-act`

### Domain-Specific
- `timber-structures`
- `oib-richtlinien`
- `oenorm`
- `bsh-traeger`
- `multi-agent-systems`
- `collision-avoidance`

### Architecture & Standards
- `asil-d`
- `audit-trail`
- `blockchain`
- `cryptography`
- `sha256`

### Regional
- `austria`
- `tirol`
- `german-language`

---

## Repository Description

**Short Description** (160 chars max):
```
Austrian building compliance & safety validation system. ISO 26262 ASIL-D + EU AI Act compliant. DMACAS + BSH-Träger EC5-AT. TRL 5 production-ready.
```

**Full Description**:
```
GENESIS DUAL-SYSTEM V3.0.1 - Production-ready safety validation system for Austrian building compliance. Features DMACAS (Multi-Agent Collision Avoidance System) in C++17 and BSH-Träger EC5-AT (Structural Engineering Validation) in Python. Implements ISO 26262 ASIL-D safety principles, EU AI Act Article 12 audit trail, and ÖNORM B 1995-1-1 compliance. TRL 5 functional prototype with 7,550+ LOC and comprehensive documentation.
```

---

## Repository Settings

### General Settings

**Features to Enable**:
- ✅ Wikis (for extended documentation)
- ✅ Issues (for bug tracking and feature requests)
- ✅ Projects (for roadmap tracking)
- ✅ Discussions (for community Q&A)
- ✅ Preserve this repository (Archive on GitHub Arctic Code Vault)

**Pull Requests**:
- ✅ Allow merge commits
- ✅ Allow squash merging
- ✅ Allow rebase merging
- ✅ Automatically delete head branches

**Danger Zone**:
- ❌ **DO NOT** make repository private (keep public for open source)
- ❌ **DO NOT** archive repository (active development)

---

## Branch Protection Rules

### `main` branch

**Branch Protection Settings**:
- ✅ Require a pull request before merging
- ✅ Require approvals (1 minimum)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Require signed commits (optional but recommended)
- ✅ Include administrators

**Status Checks** (if CI/CD configured):
- Build (C++ CMake)
- Tests (Python pytest)
- Linting (Python: black, flake8, mypy; C++: clang-format)

---

## Repository Visibility

**Current**: Public
**Recommended**: Keep public for open-source collaboration

**Benefits of Public**:
- Community contributions
- Transparency for TÜV/Fraunhofer review
- Academic citations
- Industry adoption

---

## About Section

**Website**: https://github.com/Alvoradozerouno/ORION-Architekt-AT

**Tags** (same as topics above)

---

## GitHub Pages (Optional)

If you want to create a documentation website:

**Settings** → **Pages**:
- Source: Deploy from a branch
- Branch: `main` / `docs` folder
- Theme: Cayman or Architect (professional themes)

**URL**: `https://alvoradozerouno.github.io/ORION-Architekt-AT/`

---

## Social Preview Image

**Recommended Size**: 1280x640 pixels (2:1 aspect ratio)

**Suggested Design**:
- Background: Professional gradient (blue/purple)
- Logo: GENESIS ASCII art (centered)
- Text: "GENESIS DUAL-SYSTEM V3.0.1"
- Subtext: "Austrian Building Compliance & Safety Validation"
- Badges: ISO 26262 ASIL-D, EU AI Act, TRL 5

**File**: `social-preview.png` (upload via Settings → Social preview)

---

## License Badge

Already included in README.md:
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
```

Additional badges to consider:
```markdown
[![TRL](https://img.shields.io/badge/TRL-5-blue.svg)]()
[![ISO 26262](https://img.shields.io/badge/ISO_26262-ASIL--D-red.svg)]()
[![EU AI Act](https://img.shields.io/badge/EU_AI_Act-Article_12-green.svg)]()
[![GENESIS](https://img.shields.io/badge/GENESIS-V3.0.1-purple.svg)]()
```

---

## Funding (Optional)

If you want to accept sponsorships:

**Settings** → **Sponsorships**:
- Add `.github/FUNDING.yml` with sponsor links
- Options: GitHub Sponsors, Patreon, Open Collective, etc.

Example `FUNDING.yml`:
```yaml
github: [Alvoradozerouno]
custom: ["https://your-website.com/donate"]
```

---

## Security Policy

Create `.github/SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.1   | :white_check_mark: |
| 3.0.0   | :x:                |
| < 3.0   | :x:                |

## Reporting a Vulnerability

**DO NOT** report security vulnerabilities via public GitHub issues.

Instead, please report them via:
- Email: security@your-domain.com
- GitHub Security Advisories (private)

We aim to respond within 48 hours.
```

---

## Code of Conduct

Create `.github/CODE_OF_CONDUCT.md`:

Use GitHub's default template or create custom:
- **Settings** → **Moderation** → **Code of conduct** → "Set up a code of conduct"

---

## Issue Templates

Create `.github/ISSUE_TEMPLATE/`:

1. **bug_report.md** - For bug reports
2. **feature_request.md** - For feature requests
3. **question.md** - For questions

---

## Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings

## Related Issues
<!-- Reference issues: Fixes #123 -->
```

---

## GitHub Actions (CI/CD)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  build-cpp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: sudo apt-get install -y cmake g++ libssl-dev
      - name: Build
        run: |
          cd cpp_core
          mkdir -p build && cd build
          cmake .. -DBUILD_TESTS=ON
          make
      - name: Test
        run: cd cpp_core/build && ctest --output-on-failure

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint
        run: |
          black --check bsh_ec5_at/
          flake8 bsh_ec5_at/
      - name: Type check
        run: mypy bsh_ec5_at/
      - name: Test
        run: pytest tests/ -v --cov
```

---

## Recommended GitHub Apps

Install these via GitHub Marketplace:

1. **CodeQL** - Security scanning (free for public repos)
2. **Dependabot** - Dependency updates (built-in)
3. **GitHub Actions** - CI/CD (built-in)
4. **All Contributors** - Recognize contributors

---

## README Badges to Add

Additional badges for professional appearance:

```markdown
[![Build Status](https://github.com/Alvoradozerouno/ORION-Architekt-AT/workflows/CI/badge.svg)](https://github.com/Alvoradozerouno/ORION-Architekt-AT/actions)
[![codecov](https://codecov.io/gh/Alvoradozerouno/ORION-Architekt-AT/branch/main/graph/badge.svg)](https://codecov.io/gh/Alvoradozerouno/ORION-Architekt-AT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://alvoradozerouno.github.io/ORION-Architekt-AT/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## Next Steps

1. **Immediately**:
   - Add topics via GitHub Settings → Topics
   - Update repository description
   - Enable Wikis, Issues, Discussions

2. **Soon** (Q2 2026):
   - Create issue templates
   - Set up GitHub Actions CI/CD
   - Create social preview image
   - Add security policy

3. **Later** (Q3 2026):
   - Set up GitHub Pages for documentation
   - Consider GitHub Sponsors if community grows
   - Get DOI from Zenodo for academic citations

---

**Version**: 1.0.0
**Status**: Recommendations Ready
**Last Updated**: 2026-04-06
