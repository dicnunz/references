# Local installation audit

Observed 2026-09-07 with codex-cli 0.147.0. Offline helper installation, invocation, and history persistence passed after fixing the test invocation's write permissions. This does not evaluate creative quality or prove isolation from globally installed skills.

## Installation and execution

Copied the complete package into a newly created project at `work/install-audit/project/.agents/skills/reference-work`. Read the README, library guide, and `codex exec --help`. No skill files were edited during the smoke test. A separate `work/install-audit/private-state` directory held the ledger. Neither HOME nor CODEX_HOME was changed.

From the audit project, the agent used:

```sh
python3 .agents/skills/reference-work/scripts/reference.py --state-dir ../private-state search rhythm --project install-smoke
python3 .agents/skills/reference-work/scripts/reference.py --state-dir ../private-state inspect cleveland:150880
python3 .agents/skills/reference-work/scripts/reference.py --state-dir ../private-state select cleveland:150880 --project install-smoke --property 'A cream central figure dominates a circular medallion while smaller pale figures repeat in bands and oval compartments on a wine-red ground.' --application 'Give a hypothetical two-color printed ornament study a clear focal emblem and a rhythmic supporting border within a limited palette.' --adaptation 'Print one large light figure inside a central circle on a dark-red field, then repeat smaller light figures at a reduced scale in an outer band of oval compartments.'
python3 .agents/skills/reference-work/scripts/reference.py --state-dir ../private-state history --project install-smoke
```

The first Codex invocation used `--ignore-user-config --ephemeral --skip-git-repo-check`. It inherited a read-only sandbox: inspection/history reads succeeded, while search and select correctly failed on database writes. The agent also initially resolved the relative state path from the skill folder, then corrected its working directory. No selection was falsely reported.

One retry addressed that concrete harness failure:

```sh
codex exec --ignore-user-config --ephemeral --skip-git-repo-check \
  --sandbox workspace-write --add-dir "$PWD/work/install-audit/private-state" \
  --color never --json -C work/install-audit/project \
  -o work/install-audit/codex-final-retry.txt - \
  < work/install-audit/prompt.txt \
  > work/install-audit/codex-events-retry.jsonl \
  2> work/install-audit/codex-stderr-retry.log
```

The retry exited successfully. Search returned catalog results, inspect retrieved the existing image observation, select wrote event 13 for `cleveland:150880`, and history returned that event. The agent preserved the recorded limitation that a damaged-fragment photograph cannot reconstruct the garment or establish the figures' meanings. No new visual inspection was claimed. This was a hypothetical ledger exercise, not an artifact-quality test.

## Replacement and persistence

Removed only the audit's installed copy and recopied the package into the same location. The newly copied helper returned event 13 from the external state directory. Database SHA-256 before and after replacement was identical: `b64b9110666bb079771c0280e37baebb95d754600bcd11f6fd139bbec1748880`. No SQLite files were present inside the installed package. This verifies replacement of the package preserves separately stored history; it does not test migration between different database schema versions.

## Isolation and measured limits

- This was a fresh project-local installation, not a clean operating-system account. Global skills remained visible. Codex reported skill descriptions shortened to fit its skills-context budget. The smoke agent did not read those other skills.
- `--ignore-user-config` skips the main user configuration; authentication remains available. `--ephemeral` suppresses session persistence, not all host configuration or tool visibility.
- No model or reasoning setting was explicitly supplied. The effective model and effort were not independently measured, so this audit makes no model-specific claim.
- Measured JSONL usage: initial failed attempt 206,346 input tokens, 177,408 cached input, 1,628 output, 429 reasoning output; successful retry 191,481 input, 159,872 cached input, 1,313 output, 364 reasoning output. These are CLI-reported totals and are not cost estimates. Global skill context limits interpretability of overhead.
- The helper completed without browser calls, live research, third-party Python packages, or an optional-provider API key. Provider-outage simulation was not performed.
- Host stderr included model-cache and state-database warnings; execution still completed. Raw logs remain in the private audit workspace and are not bundled here.
