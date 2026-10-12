<!-- Title: Conventional Commits in English, for example "fix(toolcall): kimi_k3 parser name for vLLM 0.31". See CONTRIBUTING.md. -->

## What and why

<!-- Two or three lines: what changes and why. Lead with the result. -->

Closes #

## Source

<!-- Parser, flag or metric names: link the engine source or docs at a release tag, not main. Write "none" if not applicable. -->

## Checklist

- [ ] Commit messages follow [the seven rules](https://cbea.ms/git-commit/) and the Conventional Commits prefix from CONTRIBUTING.md
- [ ] English and Russian skills changed in pairs (`roofline-x` and `roofline-x-ru`); `roofline-toolbox` has no Russian copy
- [ ] `python3 .github/scripts/check.py` passes
- [ ] A changed script or profile was run: output of `task doctor`, `task smoke-toolcall` or `task bench` is below, or the reason it could not be run
- [ ] The PR is linked to an issue, or it is a one-line fix that needs none
