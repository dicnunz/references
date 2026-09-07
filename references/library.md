# Library and ledger

The CLI uses Python 3 and its standard library. It reads `references/catalog.jsonl` plus local additions in SQLite. Missing or empty catalogs work; live discovery is performed using the host's available research tools and imported with `add`. The CLI does not fetch or pretend to inspect sources.

State lives in `$XDG_STATE_HOME/reference-work`, or `~/.local/state/reference-work`. It stays outside the installed skill and survives replacement of the library. Use an explicit stable `--state-dir` for a shared or isolated ledger. Place global flags before the subcommand. Every command runs in a transaction; selection checks and writes hold a SQLite write reservation. Share one state directory when coordinating workers. Separate state directories intentionally have separate memory.

```sh
python3 scripts/reference.py sources --project my-project
python3 scripts/reference.py sources "print" --project my-project
python3 scripts/reference.py search "sequence contrast" --project my-project
python3 scripts/reference.py inspect canonical-id
python3 scripts/reference.py inspect canonical-id --project my-project --status inspected --method image --locator 'page 2, full spread' --observation 'The narrow column remains fixed while image widths vary.' --limitation 'Binding and paper were not inspected.'
python3 scripts/reference.py select canonical-id --project my-project --property 'Stable narrow text column' --application 'Keep instructions findable beside varied examples' --adaptation 'Fixed instruction rail with variable figure widths'
python3 scripts/reference.py add discoveries.jsonl --project my-project
python3 scripts/reference.py history --project my-project
python3 scripts/reference.py audit
```

`sources [query] --project <id>` lists the offline [collections index](collections.json), matching names and route descriptions before reducing repeated neighborhood exposure. Omit the query to browse all routes. Both `sources` and `search` log the query and collection neighborhood as discovery events. Listing a route does not claim it was visited or inspected. Use the returned URL with available research tools. `--sources <path>` can supply a different collections index; entries accept `id`, `name`, `discovery_url`/`url`/`source_url`, and `route`/`description`.

`inspect` without `--status` retrieves evidence. With a status it records the operator's observation, not an automated quality verdict. `blocked` and `broken` revoke current eligibility for selection. Successful inspection needs method, locator, observation, and date. Search records discovery separately from inspection and selection. Search does not consume a work. `select` requires an inspection and records the adaptation. Previously selected works need `--reuse-reason` for another project, including user-directed reuse. Uncertain records additionally need `--identity-note` to explain duplicate treatment. Use the same project ID for revisions and related deliverables.

## Record format

Each JSONL line is an object. Required: `id`, `title`, and `source_url` as nonempty strings. Prefer the owning archive's stable object identifier with a namespace. Optional fields:

- `aliases`: verified alternate identifiers and URLs for that same work; ambiguous matches belong in `identity_matches` with `identity_status: "uncertain"`.
- `creators`: string list; `collection_id`, `collection_name`, `family`: strings. Use family for a documented series or shared lineage, not an invented taste category.
- `created`: original date as reported, including uncertainty or ranges; `uploaded`: publication/upload timestamp, or null. Neither is an inspection timestamp. Import stores `discovered_at` separately; inspections have `date`.
- `medium`, `language`, `geography`, `tags`, `applications`: source-supported medium/context and useful search vocabulary; distinguish inferred applications from factual metadata.
- `rights`: status, license URL, credit, evidence URL and evidence locator. A public URL is not permission to redistribute an image or reproduce a work.
- `preview`, `preview_source_url`: bundled preview path and original asset location where rights permit.
- `inspection`: `status`, `date`, `method`, `locator`, `observation`, and optional `application`, `limitation`. Successful status is `inspected`. Catalog evidence remains bounded by its recorded modality.

Add accepts one JSON object, a JSON array, or JSONL. Same explicit canonical ID updates the local record; preserve aliases and other fields when preparing a replacement. Exact overlapping aliases are flagged, never merged silently. Titles or similar-looking images do not prove identity. URL normalization removes fragments and trailing slashes and treats HTTP/HTTPS as equivalent, preserving queries and path case. Canonical IDs resolve explicitly; conflicting aliases require an explicit canonical ID. Selection exclusions conservatively include alias collisions.

`search` uses Unicode word overlap over relevant metadata and the latest recorded inspection. Each result includes that inspection's exact observation, locator, method and limits where recorded. A later inspection replaces the older observation for matching, including when it reports a blocked or broken source. The returned note is a retained account, not proof of a fresh visit or an unobserved modality.

Search ranks lexical relevance first, project continuity next, then past and current-result concentration by creator, family, and collection, including previously discovered collection neighborhoods. Discovery exposure influences ordering within the same word-overlap band and never excludes a work by itself. It provides no semantic model or taste ranking. Refine terms or add live discoveries when sparse metadata yields weak matches. `--limit` defaults to six and caps at 100. `audit` reports ledger coverage and identity/concentration issues; it cannot establish quality, licensing truth, or actual human inspection. Inspection statements are evidence supplied by the operator.
