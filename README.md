# PCP Fidelity Audit Lab

PCP Fidelity Audit Lab is an experimental skills plugin for reviewing how well a PCP analysis follows its specified sources and how much evidence supports its conclusion. Its audit preserves the original claim, distinguishes checks actually performed from inherited reports, and calls for both supporting and adverse controls.

## Source catalog

| Location | Contents |
| --- | --- |
| [Audit skill](plugin/skills/pcp-fidelity-audit/SKILL.md) | The user-invoked audit workflow and its limits. |
| [Governing sources](plugin/references/governing/) | Core R13, Mathematics R5, Science R11, Engineering R7 and Cryptography R8, with three conditional Core attachments. These are the editions pinned for this experiment. |
| [Proposed sources](plugin/references/proposed/) | Statistics 1.0 and Quality Assurance 1.0. Both are recorded as proposed and unadopted. |
| [Source index](plugin/references/source_snapshot.json) | Release IDs, roles, byte lengths and SHA-256 values for all ten reference documents. |
| [Plugin package](plugin/) | Both manifests, instructions and reference material from the saved 0.1.0 release. Its original [release README](plugin/README.md) records scope, authorship and the proposed comparison of delivery methods. |
| [Release manifest](releases/0.1.0.json) and [verifier](tools/verify.py) | An inventory of all sixteen package files and a repository tool for checking a checkout or release ZIP against it. |

## Verify or build the package

Use Python 3.9 or later from the repository root. The verifier uses the standard library.

```sh
python tools/verify.py
python tools/verify.py --package pcp-fidelity-audit-lab-0.1.0.zip
python tools/verify.py --zip pcp-fidelity-audit-lab-0.1.0.zip
```

The middle command writes a reproducible ZIP with the manifests at its root. If a ZIP already exists at the requested output path, a successful build replaces it. The final command checks the archive independently of the plugin working files. Each command exits with a failure if the inventory or a pinned source's bytes differ. To verify a published revision, obtain its manifest from a revision you trust.

The original 0.1.0 package was checked against the saved account release when this repository was initialized. The repository verifier is a maintenance tool added here. A successful run identifies the reviewed bytes. Evaluating an audit's conclusions still requires reading the cited evidence and testing the claim. The skill runs when explicitly invoked on a compatible host. Current source and audit-method changes can be proposed through [pull requests](https://github.com/KirtusJ/pcp-fidelity-lab/pulls).

Original PCP research direction and protocol authorship belong to Kirtus Justus. The release attributes its experimental packaging and evaluation notes to ChatGPT (OpenAI).
