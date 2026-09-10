# Find, inspect, and export a prompt

Use the optional local command when browsing the catalog is slower than searching.
It uses Python's standard library, makes no network requests, and never executes a
prompt or a scoring engine. The Markdown files remain usable directly.

## Find the right artifact

From the repository root:

```bash
python3 _tooling/toolkit.py list sanctions --kind prompt
python3 _tooling/toolkit.py list --category compliance
python3 _tooling/toolkit.py list --kind framework --json
```

All query terms must match; searches cover titles, metadata, and content. Results carry
stable repository-relative IDs. Use the full ID if a basename is ambiguous. Prompts,
standalone payloads, and runnable frameworks are different artifact kinds. A framework
result points to its methodology and reproduction command; it is not a paste payload.

## Inspect or try a prompt

```bash
python3 _tooling/toolkit.py show prompts/compliance/entity-risk-assessment
python3 _tooling/toolkit.py show prompts/compliance/entity-risk-assessment --demo
```

The first command emits the canonical prompt block. The second fills it using the
registered fictional demonstration inputs. Neither runs an assistant. Replace the demo
with appropriately authorized inputs when using the method; demo results do not
establish production accuracy.

## Make an attachment with provenance

```bash
python3 _tooling/toolkit.py assemble prompts/compliance/entity-risk-assessment --with-base --output build/entity-prompt.md
python3 _tooling/toolkit.py assemble prompts/compliance/entity-risk-assessment --with-base --json --output build/entity-manifest.json
```

The Markdown export combines one prompt and BASE into one attachment while preserving
the two-source contract. The JSON export is a reproducibility envelope containing the
payload and manifest; it is useful for comparison or archiving. Source hashes attest
bytes, not whether the methodology is correct or a model used every instruction.

Outputs are created exclusively: an existing destination is refused. Choose a new
filename for a later version. Keep private inputs and generated analysis outside the
public repository. Only the public instruction export belongs in this build workflow.

To verify a saved JSON envelope against the checkout that produced it:

```bash
python3 _tooling/toolkit.py verify build/entity-manifest.json
python3 _tooling/toolkit.py verify build/entity-manifest.json --json
```

Verification rebuilds the payload from its catalog ID and compares the content,
source hashes, sizes, mode, and remaining placeholders. It rejects altered payloads
even if their hashes have been recomputed, and does not follow source paths supplied
by the envelope. Demo values and their source hash come from the same bytes. Toolkit
sources cannot be symbolic links, including links into ignored local material.

A later source revision may legitimately fail verification; retain the source commit
with the export and check out that revision to reproduce it. Hashes and reconstruction
establish consistency with this checkout, not authenticity, current applicability, or
the quality of an assistant's conclusions. Verification reads files and emits its result;
it neither executes the payload nor modifies the envelope.

To reject an attachment exceeding an exact character budget:

```bash
python3 _tooling/toolkit.py assemble prompts/compliance/entity-risk-assessment --with-base --max-chars 120000
```

Character and byte counts are exact; token counts are four-characters-per-token
estimates. They are not a tokenizer measurement and do not guarantee fit in any
assistant. Reserve room for the user's inputs and the response. A rejected export
requires a smaller valid selection or a larger supported context; nothing is truncated.

## Check a change before sharing

```bash
python3 _tooling/check.py
python3 _tooling/check.py --full
```

The first command runs Python content, generation, navigation, and regression gates.
The full command also reproduces registered engine evidence and reference data.
Kotlin parity and presentation preservation remain separate jobs because they require
their declared runtimes. A green structural check does not validate model-generated
analytical conclusions. Apply the [quality standard](../methodology/output-quality-standards.md)
and inspect [engine evidence](../frameworks/EVIDENCE.md) for the specific intended use.
