# Catalogue of this repository

Every entry at the top of the repository, and every folder one level down in `plugin`, with one line on what it is. `tests/check_catalog.py` fails when a tracked path of that kind is missing here or a path listed here no longer exists, so this page cannot fall behind the tree. The check is PCP OS's own, taken from `pcp-os` at a pinned commit. The [README](README.md) has the longer source catalogue, with what each document is for.

"In the release" says whether the path's content is part of what a person boots or installs with PCP OS. This repository is an experimental plugin kept apart from PCP OS; none of it is in a PCP OS release.

| Path | What it is | In the release |
|---|---|---|
| `.gitattributes` | Line endings and binary marking, so the package's bytes survive a checkout. | no |
| `.github` | Continuous integration: the catalogue check. | no |
| `.gitignore` | Paths git ignores. | no |
| `CATALOG.md` | This page. | no |
| `plugin` | The plugin package of the saved 0.1.0 release: sixteen files, byte for byte. | no |
| `README.md` | What the lab is, its source catalogue and how to verify or build the package. | no |
| `releases` | The release manifest: every package file with its length and SHA-256. | no |
| `tests` | The test of the release ZIP, and this catalogue's check. | no |
| `tools` | The verifier that checks a checkout or a ZIP against the release manifest. | no |
| `plugin/.codex-plugin` | The package's manifest for a Codex host. | no |
| `plugin/references` | The ten pinned reference documents, governing and proposed, with their index. | no |
| `plugin/skills` | The audit skill. | no |
