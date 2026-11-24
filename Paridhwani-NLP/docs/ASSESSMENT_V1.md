# Structured assessment v1

This is an implemented **in-process, socket-free** boundary for the Python evaluator.
It is separate from the game's strict text-only `POST /v1/dialogue/respond` contract.
No HTTP server, endpoint, credentials, automatic service attachment or live gameplay
changes are included. A future host can expose an agreed assessment route, such as
`POST /v1/assessment/evaluate`; that route is not implemented or listening here.

The [JSON schema](assessment-v1.schema.json) defines requests, successful assessments
and errors. [Fixtures](fixtures/) cover accepted, corrected, rejected and unknown-step
results. Requests carry exactly:

```json
{
  "version": 1,
  "request_id": "0123456789abcdef0123456789abcdef",
  "quest_id": "q1_3",
  "step_id": "q1_3_a",
  "learner_text": "Hesaru Meera",
  "player": {"name": "Meera"}
}
```

Successful responses echo the version, request, quest and step IDs, carry `status:
"ok"`, a 64-hex `content_revision`, and an `assessment` with exactly `outcome`,
`answer_id`, `error_category`, `correction_type`, `reaction_id`, `detected_form` and
`confidence`. Outcomes are `accepted`, `accepted_with_correction`, `not_accepted`.
Correction tips and NPC reactions are resolved from pinned content IDs. Confidence
is a heuristic, not a calibrated probability or an automatic gameplay threshold.
No response contains quest effects, choice commands, player save or word-credit
instructions. A rejected learner answer is a valid successful assessment, not a
transport error.

## Validation and errors

`AssessmentBoundary.handle_json(bytes)` returns UTF-8 JSON bytes. It rejects duplicate
keys at any level, malformed/trailing JSON, malformed UTF-8/Unicode, NaN/infinity,
bodies over 65,536 bytes, nesting over eight levels and unknown properties. Version
must be the integer token `1` (JSON Schema also considers `1.0` an integer; the
runtime deliberately requires an integer token). Limits use UTF-16 code units:
512 for nonempty learner text, 128 for IDs, 80 for the player name. Empty player
name is permitted if unknown; `player` and its `name` field remain required.
The schema's code-point `maxLength` is supplemented by `x-maxUtf16CodeUnits` and
the runtime checks. Response IDs/categories are validated against loaded content.

Errors have exactly `version`, `request_id`, `status: "error"`, `error: {"code":...}`.
Codes: `invalid_json`, `invalid_request`, `unsupported_version`, `unknown_step`,
`unsupported_step` (read/collect tasks do not use typed assessment),
`invalid_assessment` (invalid provider output), `internal_error`. Invalid/missing
request IDs produce an empty ID; otherwise errors echo the valid correlation ID.
Errors never include learner text, paths, exception messages or tokens. The boundary
does not log bodies. A host must set body limits before buffering and choose HTTP
status mapping, cancellation, deadlines, hosting/authentication and privacy policy.

`content_revision` hashes the loaded curriculum JSON and training/spelling data
snapshot; protocol version is not an evaluator build identifier. Construct the
matcher and boundary together from immutable/pinned files, recreate them on content
updates, and pin the evaluator build separately. No hot-reload is provided.

```python
from pathlib import Path
from matcher import AnswerMatcher
from assessment import AssessmentBoundary

root = Path("/absolute/path/to/Paridhwani-NLP")
matcher = AnswerMatcher(root / "data")
boundary = AssessmentBoundary(matcher)
response_bytes = boundary.handle_json(request_bytes)
```

Use `assess(request_dict)` for direct typed calls; invalid calls raise
`ContractError` with a fixed `code`. The safe wire entry point is `handle_json`.
The legacy `AnswerMatcher.evaluate` accepts empty inputs as `not_accepted`; the
wire boundary rejects empty submissions as invalid requests.

## Future Unity consumer

Use active **curriculum quest/step IDs**, not the current game display speaker or
`TeaTurn.Id`. Add a reviewed mapping from a specific authored game interaction to a
lesson. Do not attach this payload to `IDialogueTextService`: its response needs a
text `line`, and rejects assessment properties. An executable schema check against
the game's current `docs/contracts/nlp-v1.schema.json` proves that separation.

The standalone [C# consumer example](../integration/AssessmentConsumer.cs) accepts
only correlated version/quest/step/request IDs, a pinned content revision, bounded
payload and a per-step answer allowlist. It rejects duplicate/extra fields and
command properties. `TryRead` returns false for unavailable or malformed results.
It has no Unity, save, progression, socket or automatic attachment calls.

The game owner must additionally reject retired/cancelled request generations,
marshal presentation to the Unity thread, map outcome/tip/reaction IDs through its
pinned content, and validate its own current gates before choosing any authored
transition. An accepted result is evidence for that transition, not permission to
execute server commands. Keep authored choices available on timeout/error/offline.
Never award all `target_words` automatically: production, comprehension, help and
corrections need separate reviewed credit rules.

Player-name policy: formatted name answers accept arbitrary alphabetic names, up
to four tokens, excluding known task vocabulary/noise. A bare unfamiliar word is
ambiguous; it is accepted as a name only when it matches supplied `player.name`.
The historical known Arun/Aditi/Ravi bare forms remain supported. Thus `Meera`
with `player.name="Meera"` works; a bare unknown word without context remains
unaccepted. The curriculum's unconditional bare-name placeholder needs this
context clarification. This is language practice, not identity verification.

Authored literal errors take priority over generalized name/item templates for
unseen examples. Unambiguous reviewed CSV exact examples keep their labels.
Rule lexicons and input share normalization; food/drink templates expand from
`feedback.json.item_words`. Unseen negative ownership claims fail closed before
token acceptance. Character-similarity acceptance is disabled: known spelling
variants, authored forms and explicit rules are supported, not arbitrary spellings.
Script answers use reviewed exact authored forms/data; no general transliterator
or fluent-language correctness guarantee is supplied.

## Reproduce verification

From `Paridhwani-NLP`, using existing Python/pandas:

```powershell
python -I -B verification/verify.py
./verification/Verify-Consumer.ps1
```

The runner directly invokes the 26 original plain test functions and discovers
the new unittest regression methods (pytest is not required). Its JSON Schema
checks use the already-installed `jsonschema` package; this is a test dependency,
not a runtime dependency. Tests include every held-out field, every expanded
authored-policy case, negative/contradictory cases, invalid Unicode/types/limits,
correlation, response validation and saved fixtures. The C# runner reads cached
Unity compiler references but compiles only this standalone example and writes
only its own verification output. It does not launch or modify Unity/the game.

See [recorded results](../verification/RESULTS.md), raw results and preserved audit
baseline under `verification/`. All measurements are agreement with the supplied
labels/policies, not independent general language accuracy. Network/HTTP and native
Unity acceptance were not attempted; the prior loopback denial was not bypassed.
