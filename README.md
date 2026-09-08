# References

A Codex skill and searchable reference library for creative work. It records which sources were inspected and how they informed the result.

[Browse the library](https://dicnunz.github.io/references/library.html) · [Compare the artifacts](https://dicnunz.github.io/references/evidence/comparison/index.html) · [Read the evidence](evidence/report.md)

The package contains **120 inspected works across 24 collections**, **1,165 searchable records**, and **56 image previews**. The six-pair evaluation found specific improvements and regressions; it does **not establish an overall advantage**. Source notes identify exactly what was inspected and what remains unverified.

## Install

Requires Python 3.9 or newer. The helper uses only the standard library and needs no API key.

```sh
git clone https://github.com/dicnunz/references.git ~/.codex/skills/reference-work
```

Alternatively, copy this repository into your agent's skill directory, retaining `SKILL.md`, `agents`, `scripts`, `references`, and `assets`. Start a new Codex task so it can discover the skill, then invoke:

```text
$reference-work Create a printable guide for this exhibition using the supplied text.
```

The skill works with ordinary available browsing and production tools. It does not install providers or perform paid generation.

```sh
cd ~/.codex/skills/reference-work
python3 scripts/reference.py sources "construction" --project my-project
python3 scripts/reference.py search "repetition rhythm" --project my-project
```

[Library commands](references/library.md) cover discovery, inspection, selection, identity, and state controls. Use stable project IDs for continuity; unrelated projects exclude previously adopted known works unless a specific reuse reason is recorded.

## Update and history

History lives outside the installation, at `$XDG_STATE_HOME/reference-work` or `~/.local/state/reference-work`. Back up that directory. Updating this repository with `git pull --ff-only` preserves the ledger. Use `--state-dir` for a different explicit location. The [installation audit](evidence/installation.md) verified history survives package replacement, with its environment limits documented.

## Evidence and rights

The [evidence report](evidence/report.md) includes every initial comparison, blind critiques, physical and temporal verification limits, library concentration, and recorded usage. [Development sources](references/development.md) explain the package's own reference process. [Plumbing checks](scripts/check_plumbing.py) verify mechanics, not creative quality.

Original code and authored instructions are [MIT licensed](LICENSE). Third-party works retain their own rights; consult [attributions](ATTRIBUTIONS.md) and per-record evidence. Link-only works are not bundled copies. Audio has a separately labeled, unauditioned [discovery supplement](evidence/audio.html).

The browser library is named Mnemosyne, after [Warburg’s image panels](https://warburg.sas.ac.uk/library-collections/warburg-institute-archive/archive-collections/verknupfungszwang/mnemosyne-atlas). Its board and list views share the same source records and inspection notes.
