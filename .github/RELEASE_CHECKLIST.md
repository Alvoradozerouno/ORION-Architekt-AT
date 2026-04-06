# Release Checklist

Use this checklist when preparing a new GENESIS release.

## Pre-Release (1 week before)

### Code Quality
- [ ] All tests passing (Python + C++)
- [ ] No critical bugs in issue tracker
- [ ] Code coverage >85%
- [ ] Security scan clean (CodeQL)
- [ ] Performance benchmarks stable

### Documentation
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated in:
  - [ ] bsh_ec5_at/src/bsh_träger_v3.py
  - [ ] cpp_core/include/dmacas_types.hpp
  - [ ] CITATION.cff
  - [ ] README.md
  - [ ] GENESIS_README.md
- [ ] API documentation up to date
- [ ] Migration guide (if breaking changes)

### Legal & Compliance
- [ ] License headers on all new files
- [ ] CONTRIBUTORS.md updated
- [ ] No proprietary code included
- [ ] Export control compliance checked

### Testing
- [ ] Deterministic verification (20 identical runs)
- [ ] Cross-platform testing (Linux, macOS, Windows)
- [ ] Python versions tested (3.10, 3.11, 3.12)
- [ ] C++ compilers tested (GCC, Clang, MSVC)

## Release Day

### Version Control
- [ ] Create release branch: `release/vX.Y.Z`
- [ ] Update version in all files
- [ ] Commit: "Prepare release vX.Y.Z"
- [ ] Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push: `git push origin vX.Y.Z`

### GitHub Release
- [ ] Go to Releases → Draft new release
- [ ] Select tag vX.Y.Z
- [ ] Title: "GENESIS vX.Y.Z - [Name]"
- [ ] Description from CHANGELOG.md
- [ ] Attach build artifacts:
  - [ ] Source code (auto)
  - [ ] Compiled binaries (if applicable)
  - [ ] Documentation PDF

### Communication
- [ ] Announce on GitHub Discussions
- [ ] Post on LinkedIn (company page)
- [ ] Email announcement to pilot users
- [ ] Update website
- [ ] Notify academic collaborators

### Zenodo DOI
- [ ] Trigger Zenodo release
- [ ] Verify DOI created
- [ ] Update CITATION.cff with DOI
- [ ] Update README badges with DOI

### Post-Release
- [ ] Merge release branch to main
- [ ] Update develop branch
- [ ] Close milestone
- [ ] Create next milestone
- [ ] Archive old documentation versions

## Version Numbering

**Semantic Versioning (SemVer):**
- MAJOR.MINOR.PATCH (e.g., 3.0.1)

**When to increment:**
- MAJOR: Breaking changes, API incompatibility
- MINOR: New features, backward compatible
- PATCH: Bug fixes, documentation updates

**Examples:**
- 3.0.0 → 3.0.1: Bug fixes
- 3.0.1 → 3.1.0: New BSH material support
- 3.1.0 → 4.0.0: DMACAS API redesign

## Release Names

Use Austrian mountains for release names:
- v3.0.0: "Großglockner"
- v3.0.1: "Wildspitze"
- v3.1.0: "Weißkugel"
- v4.0.0: "Großvenediger"

## Emergency Hotfix

If critical bug found after release:
1. Create hotfix branch from tag
2. Fix bug
3. Increment PATCH version
4. Tag and release immediately
5. Announce hotfix clearly

## Rollback Plan

If release has critical issues:
1. Revert to previous stable tag
2. Document issues in GitHub
3. Communicate to all users
4. Fix in develop branch
5. Re-release as new PATCH version
