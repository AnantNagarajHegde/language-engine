# Assessment fixes: verification recorded 29 October 2026

All work is in working files. No `git add`, commit, push, branch switch or submodule
pointer update was performed. `git -C language-engine status --short` was denied
access to `paridhwani/.git/modules/language-engine`; it was not bypassed or retried.
Consequently existing index state cannot be reported. A hash comparison before
editing found no differences between the audited sources/data/content/tests and
the saved audit snapshot. No Unity gameplay files were edited.

## Changes

- `src/normalizer.py`, `src/structural_rules.py`: normalize explicit rule lexicons
  through the same function as learner input. Canonical long-vowel words now match
  after normalization. This is a representation fix, not a relaxed acceptance test.
- `src/authored_policy.py` (new), `src/matcher.py`: load authored literals, explicit
  error cases, correction types and bounded name/item templates from pinned lesson
  content. Preserve reviewed exact CSV examples and their labels. Apply specified
  global English/Hindi diagnostics to unmatched inputs and preserve mixed answers
  with Kannada target words. Remove all character-similarity promotion and stacked
  evaluator monkey-patches; retain the existing narrow output corrections in one
  explicit call. Unseen negative ownership claims fail closed.
- `src/assessment.py` (new): versioned strict socket-free request/result boundary,
  input/output validation, fixed error codes and correlation/content revision.
- `docs/assessment-v1.schema.json`, `docs/fixtures/`, `docs/ASSESSMENT_V1.md` (new):
  machine-readable contracts, saved accepted/corrected/rejected/error exchanges and
  ownership/mapping/hosting handoff. This is distinct from text-only dialogue v1.
- `integration/AssessmentConsumer.cs` (new): standalone consumer requiring current
  IDs, revision and answer allowlist. No game commands, saves or Unity API calls.
- `tests/test_assessment_regressions.py`, `verification/policy_cases.py`,
  `verification/verify.py`, `verification/Verify-Consumer.ps1` (new): executable
  regressions and reports. `README.md` links the new workflow; `requirements.txt`
  declares JSON Schema verification dependency. No packages were installed.
- `.gitignore` (new): excludes Python caches and consumer compiler products.

Curriculum JSON, CSV expected labels and all five original test modules are
unchanged. Retained baseline and result artifacts are review evidence, not new
training examples. The file manifest is `verification/changed-files.json`.

## Before/after measurements

| Check | Audit baseline | After fixes |
|---|---:|---:|
| Original plain test functions | 26/26 | 26/26 |
| New unittest methods | — | 10/10 |
| Held-out outcome agreement | 163/178 | 178/178 |
| Held-out all-five-field agreement | 157/178 | 178/178 |
| Training outcome agreement | 681/681 | 681/681 |
| Training all-five-field agreement | 680/681 | 680/681 |
| Authored-policy agreement without player context | 136/210 | 209/210 |
| Authored-policy agreement with explicit unfamiliar bare-name context | — | 210/210 |

Five fields are outcome, answer ID, error category, correction type and reaction
ID. Every original label is retained. The outstanding training metadata mismatch
is R00855 (`ALL/ALL`, `what`): supplied label `unclear`, actual `english_only`.
This is a preexisting policy/data ambiguity; it was not relabelled to make results
perfect. The single no-context authored case is bare `Meera`; both formatted
`Nanna hesaru Meera` and bare `Meera` with `player.name="Meera"` pass. Unknown bare
words cannot reliably be distinguished from names, so missing-context behavior is
explicitly fail-closed rather than broad acceptance of nonsense. Context can also
disambiguate a real name that overlaps task vocabulary (e.g. Anna).

All 171 step-specific held-out examples (seven `ALL/ALL` rows excluded) passed
assessment envelope/ID/result validation and socket-free JSON serialization.
JSON Schema checks passed for those responses and all eight saved fixture objects
(179 objects). An executable check using the **current game** schema confirms
assessment responses are rejected by its text-only dialogue contract; they must
use a separate consumer.

Standalone C# compilation and execution passed for three accepted/corrected/
rejected fixtures and ten invalid scenarios: retired request, wrong quest/step,
wrong revision, foreign answer, error envelope, duplicate/extra command fields,
malformed envelope and a wrong version type. Compilation emitted CS1701 for the
cached Unity System.Text.Json/netstandard references; execution passed using the
supplied .NET runtime. This is not native Unity/IL2CPP or Player acceptance.

## Critical reproductions now protected

- `Kaapi beku`, `Dayavittu keeli ellide?`, `Nanage oota beku`, `Oota eshtu?`
  and their held-out variants now receive the original expected fields.
- All authored food/drink item expansions and name/correction patterns are checked.
- The exact Kannada `e_nimage` error stays rejected rather than being promoted at
  0.889 similarity. Unknown near-spellings are not accepted by similarity.
- Contradictory requests, wrong pronouns, missing/invalid names, unsupported items,
  mixed ownership/negation and gibberish have negative regressions. The tests do
  not just assert acceptance of positive examples.
- English-only and Hindi feedback and Somanna's English reaction are checked
  across all 14 typed-response steps; mixed `Thank you dhanyavada` stays accepted.
- Strict wire tests cover malformed Unicode/JSON, duplicates, null/extra fields,
  wrong types/version/IDs, UTF-16 limits, unknown/non-response steps, invalid provider
  results, NaN/bool confidence, sanitization and saved fixtures.

## Reproduce

From `Paridhwani-NLP` with the already-installed Python/pandas/jsonschema:

```powershell
python -I -B verification/verify.py
./verification/Verify-Consumer.ps1
```

The recorded Python interpreter was
`C:\Users\amogh\AppData\Local\Python\pythoncore-3.14-64\python.exe` (3.14.3).
Pytest is unavailable, so the runner directly invokes original plain functions
and uses stdlib unittest for the new methods. It writes only verification results;
no downloads, sockets, UI or game compilation are performed. The C# script reads
cached Unity references and compiles only the isolated consumer sample.

Raw row results, logs, hashes and comparisons are under `results/`; the immutable
audit baseline is under `baseline/`. These are **agreement measurements**, not
independent language accuracy: the test set contains 79 normalized inputs, four
original failing variant families and five normalized training-overlap rows. There
are no Kannada-script held-out rows; authored script cases provide finite policy
coverage, not general Kannada semantic certification.

## Remaining integration and content decisions

- No HTTP server was started, socket denial retried/bypassed, endpoint attached,
  credentials created or network/security setting changed. Real transport and
  in-engine attach/submit/cancel/fallback acceptance remain untested.
- A future game adapter must map current story turns to curriculum IDs, provide
  player name/current request generation, pin content revision, retain authored
  fallback and validate local gates. Do not bind assessment responses to the
  existing `IDialogueTextService` text API.
- General Kannada grammar/register/negation and script rendering still need
  fluent/native acceptance. Unknown name/template scope and novel spelling support
  should grow through reviewed data/rules, not unsafe fuzzy acceptance.
- Hint timing, absent success-line fallback, per-response word credit, comprehension
  versus production, corrections/help/replay mastery credit and limited two-quest
  reuse remain content/product decisions. No broad mastery redesign was attempted.
- The 13 spelling CSV metadata omissions and differences in `mixed` detector label
  definitions are retained for review; these do not affect the new wire guarantees.
