# Contributing to Roofline

[По-русски](CONTRIBUTING.ru.md)

Issues and pull requests are welcome. The fastest fix is an outdated parser, flag or metric name: run `task doctor` and open an issue with its output.

## Issues

Search the [open issues](https://github.com/lenialno/roofline/issues) first, then pick a template:

| Template | When | Label |
|---|---|---|
| Bug | a task or script fails, or a skill gives advice that does not work | `bug`, `needs triage` |
| Outdated parser, flag or metric | `task doctor` or your engine shows a name in the tables no longer exists | `outdated` |
| Documentation | wrong or missing text in a skill, README or `docs/roadmap-ru` | `documentation` |
| Proposal | a new skill, task, model family or profile | `enhancement`, `needs triage` |
| Question | how to do something with Roofline | `question` |

Remove internal hostnames, paths, API keys and prompts from any output you paste.

## Layout

| Path | Contents |
|---|---|
| `skills/roofline*/SKILL.md` | skills; each English skill has a Russian copy with the `-ru` suffix |
| `skills/*/references/` | tables the skills read: parsers, flags, metrics, clients |
| `skills/roofline-toolbox/` | shared Taskfile, scripts and launch profiles; English only |
| `agents/` | Claude Code subagent `incident-investigator` |
| `docs/roadmap-ru/` | Russian translation of the roadmap.sh Inference Engineering map |
| `.claude-plugin/plugin.json` | plugin manifest; it has no `version` on purpose, installs follow commits |
| `.github/scripts/` | repository checks (`check.py`) and the weekly drift check (`drift.sh`) |

## Local checks

Run before you push, CI runs the same:

```bash
python3 .github/scripts/check.py
npx -y @anthropic-ai/claude-code@latest plugin validate .
DISABLE_TELEMETRY=1 npx -y skills@latest add . --list
task --list
```

`check.py` verifies skill frontmatter, EN and RU skill pairs, relative links and typography. The plugin validator prints one warning about the missing `version`; that is expected.

## Rules for content

- Change English and Russian skills in pairs, in the same pull request.
- Take parser, flag and metric names from the engine source or docs at a release tag, and link that tag in the pull request. Never from memory.
- Write the checked engine versions into the table header, for example "checked against vLLM 0.31.0 and SGLang 0.5.21".
- A new or changed profile passes `task health && task smoke-toolcall && task bench` on real hardware before merge. Paste the output into the pull request.
- Scripts stay stdlib only: `python3` and `bash`, no pip installs. Python runs with `-I`.
- Prose has no em or en dashes, no arrows and only straight quotes. `check.py` enforces this.
- Lead with the result, then the details. Short sentences, concrete numbers.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) in English, following [the seven rules](https://cbea.ms/git-commit/): imperative mood, subject up to 72 characters, no trailing period, the body says what and why.

| Type | For |
|---|---|
| `feat` | a new skill, task, script or profile |
| `fix` | a wrong name, broken script, wrong number |
| `docs` | README, skill wording, translation |
| `ci` | workflows and repository checks |
| `chore` | everything else |

Scope is the skill without the `roofline-` prefix or an area: `feat(toolbox): task doctor`, `fix(toolcall): kimi_k3 parser name`, `docs(roadmap-ru): hardware chapter`.

## Pull requests

1. For a new skill, task or a large change, open a Proposal first.
2. One topic per pull request. Open it as a draft while you work.
3. Title in the same format as a commit. Fill in the template: what and why, linked issue, source tag, checklist.
4. CI must be green. Squash merge, the title becomes the commit on `main`.

## License

By contributing you agree that your work is released under the [MIT license](LICENSE).
