# Evidence report

Reference Work provides a usable inspected library and durable reference history. This experiment **does not establish an overall creative advantage**. Specific gains were offset by regressions and repeated visual defaults.

## What was evaluated

Six briefs were frozen before implementation: invitation, causal explanation, finding aid, booking interaction, timed noticing experience, and printable construction. The last two were withheld from the implementation owner until the candidate was frozen. Thirteen artifacts were built in fresh agent contexts: six skill/baseline pairs plus Anthropic frontend-design on the booking brief. All received the same per-brief content, output constraints, tools, and 180-second builder allowance. Baselines could research. Shared Chrome was reserved for subsequent coordinator verification in every arm.

No per-arm model or reasoning override was supplied. Host configuration recorded `gpt-6-astra` and `low`; effective per-call settings were not independently audited. Global skill descriptions were available in the environment. “Baseline” means no experimental skill injected, not a model with every ambient instruction removed. Context isolation was explicit and scoped, not enforced by filesystem permissions.

Two fresh critics reviewed anonymous development outputs; two additional fresh critics reviewed held-out outputs. They opened actual images and print renders, read briefs, and used external craft exemplars. Interaction checks came from the independent coordinator, who knew arm identities. Timed work ran through the full elapsed minute with state captures; critics did not assess continuous video or audio. Some external exemplar images were inaccessible, and each critique records that limitation.

The procedure follows the [Gauntlet Loop](https://somethingbig.ai/gauntlet-loop) and [skill-versus-baseline comparison](https://somethingbig.ai/skills-upgrade): build artifacts, keep critics independent, preserve mixed findings. No numerical taste grades were used.

## Findings

| Brief | Observed comparison | Consequential limitation |
|---|---|---|
| B01 invitation | Skill’s 48-button grid gives repetitive work a stronger commemorative structure. One critic preferred baseline overall; the other was mixed. | Skill puts free admission and what to bring below the long mobile illustration. |
| B02 lock explanation | Both critics prefer baseline’s separate matched-water-level stage before departure. | Skill compresses prerequisite and open-gate state, leaving prose to explain the causal order. |
| B03 finding aid | Mixed: skill’s desktop quick index gives answers directly; baseline puts locating controls earlier on mobile. | Skill retains “ARRANGED BY ID” after oldest-first sorting and buries the map on mobile. |
| B04 booking | Mixed: skill exposes eligibility and status choices clearly; baseline explains the local action more precisely. | Both retain an introductory block above mobile confirmation. All pass tested validation and edit paths. |
| B04 popular skill | Mixed: Reference Work has the clearer initial input flow; frontend-design has useful allocation feedback and a compact mobile confirmation. | Comparator’s allocation illustration follows the save button on mobile. No overall superiority established. |
| B05 timed marsh, held out | Both critics prefer baseline’s more substantial scene and illustrated reading mode. | Baseline distorts its SVG on mobile; skill’s scene is slight and returning from reading leaves a stale “No timer” footer before starting. |
| B06 paper tent, held out | Both critics prefer skill’s cleaner finished label and clear numbered end-view assembly. | Baseline’s perspective faces overlap misleadingly. Neither was physically assembled. |

[Open all artifacts and evidence](comparison/index.html). Read the independent [development A](comparison/critic-a.md), [development B](comparison/critic-b.md), [held-out A](comparison/heldout-critic-a.md), and [held-out B](comparison/heldout-critic-b.md) critiques.

No repair round was run. Existing guidance already asks for alternate states, required sizes, hierarchy, and task fit. The development sample did not isolate a specific missing mechanism that an added instruction would demonstrably repair. The candidate was retained with its defects and unproven benefit; held-out findings did not change it. The [selection record](comparison/final-candidate.md), [brief hashes](comparison/briefs/manifest.json), and [frozen candidate hashes](comparison/candidate-r0.sha256.json) preserve that boundary.

## Functional and physical checks

The booking matrix rejected wet pieces and both incompatible firing/status combinations, preserved entered name/allocation, confirmed both valid firings, and returned populated edit forms. Keyboard activation and reload-clears behavior were exercised. Finding-aid records and brass/oldest/West-2 results matched the supplied data. Tested mobile pages had no horizontal overflow at 390 pixels.

Both timed versions reached completion, paused without advancing elapsed progress, restarted, and exposed all four observations immediately in reading mode. Reduced-motion branches were inspected in source; OS/browser emulation was not performed. This limits claims about experienced motion quality.

Both paper nets are contiguous 80 × 130 mm, with three 80 × 40 mm panels and an 80 × 10 mm tab. Print exports are one A4 page. PDF-vector calibration bars measure 49.994 mm, reflecting minor browser rounding. Physical printer scaling, paper, adhesive, and stability remain untested. Each artifact directory retains screenshots, print PDF where relevant, and scoped checks.

## Reference reuse and range

The six treatment builders adopted six different sources: a Rijksmuseum printed game sheet, River Wey Trust lock text, a Yale finding aid, GOV.UK check-answers HTML/text, a Monet reproduction, and a Nicky Case pattern-making article. There was no repeated adopted work or creator in those logs. Each trial used an isolated ledger for comparison fairness, so the sequence does not test shared-history exclusion by itself.

Different sources did **not** produce broad visual range. Cream paper, dark serif headings, thin rules, small uppercase annotations, and muted green/brown accents recur across both arms. Construction and information ordering varied more than visual vocabulary. The helper’s separate plumbing checks verify known-identity reuse exclusion and project continuity; those checks cannot establish aesthetic diversity.

## Library and access limits

The release contains 1,165 records and 120 inspected works across 24 collections, with five inspected works per collection. Inspection modes: 55 images, 50 texts, 14 browser interactions, and one text/image work. Fifty-six licensed image previews are bundled. Four Smithsonian collections share a parent institution. The larger catalog remains concentrated: Art Institute and Cleveland supply 900 records, 77.3%. English is the most recorded text language; Japanese and French have substantive samples. Some Japanese extraction was garbled and notes explicitly limit their observations to legible passages.

The collection spans ancient objects and contemporary 2026 publications, but it is not comprehensive. No source was fully auditioned as audio or inspected as a complete timed video. A playable [NASA audio discovery supplement](audio.html) is included without an inspection claim. Interactive source notes describe observed states, not full-game or full-simulation evaluation. 283 catalog records lack named creators; no seed record has a verified family field. Unknown cross-collection identities remain uncertain. These gaps limit repetition controls until enriched during use. [Machine-readable audit](library-audit.json).

## Installation, usage, and release scope

The standard-library helper passed offline search, discovery rotation, inspection gates, known alias handling, continuity, reuse exclusion, rollback, concurrency, and durable-history checks. A fresh project-local Codex install successfully invoked it after correcting the smoke test’s initial read-only sandbox. Recopied package files preserved the external ledger byte-for-byte. Global skills remained visible, so this was not a clean operating-system or fully isolated skill environment. [Installation evidence](installation.md).

Builder logs report roughly two to three minutes per artifact, all within the 180-second allowance. [Recorded build times](comparison/builder-usage.json) are self-recorded wall time, not token or cost measurements. Per-trial model-call usage was not captured. The installation report includes actual CLI token totals where available.

The released instructions/helpers match the frozen candidate. Distribution additions are the public library, evidence, attribution, audio discovery supplement, and repaired rights-evidence paths. These additions were not injected into the trial builders. Original code/instructions are MIT; third-party assets retain separate [attribution and rights](../ATTRIBUTIONS.md). [Pinned upstream versions](upstream-versions.json).
