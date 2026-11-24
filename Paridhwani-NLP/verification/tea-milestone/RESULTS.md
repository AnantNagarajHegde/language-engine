# First tea-stall assessment milestone: isolated integration verification

Status: **socket-free mapping/consumer/story-source tests pass; production/live
milestone remains incomplete.** No gameplay or evaluator production files were
changed in this pass. All changes remain working files; no Git writes, staging,
commits, pushes, branch changes or submodule updates were performed.

## What ran

Run from the Paridhwani workspace:

```powershell
./language-engine/Paridhwani-NLP/verification/tea-milestone/Verify-TeaMilestone.ps1
```

The runner calls the real `AnswerMatcher` and `AssessmentBoundary` in installed
Python, generates ten actual request/response exchanges plus a real unknown-step
error, then compiles the current `integration/AssessmentConsumer.cs`, the isolated
`integration/tea-milestone/TeaAssessmentSeam.cs`, and the current game files
`TeaConversation.cs` and `TeaProgress.cs`. It executes the actual
`LocalTeaConversation`, `TeaProgress` and `TeaSaveStore` code in standalone .NET.
Input SHA-256 hashes are saved and checked again after execution.

It does not start Unity or a server. `Support.cs` provides test-only compile
dependencies for world investigation/presentation/enum types; those systems are
not under test. Vector3 comes from installed Unity managed assemblies. Save tests
inject `TestProgressCodec` using System.Text.Json, not native JsonUtility. Saves
use fresh GUID paths under this test's ignored output directory, never the user's
actual visit. Compiler products, copied installed DLLs and temporary saves are
ignored. Python uses `-I -B`; nothing is installed or downloaded.

## Final results

| Stage | Result |
|---|---|
| Real evaluator/boundary exchanges | 10 learner exchanges + one unknown-step error generated |
| Isolated C# mapping/provider/progress/save checks | **186 assertions passed** |
| Source guards for controls/cancellation/attachment/provenance | **11/11 passed** |
| Existing evaluator test functions, rerun | **26/26 passed** |
| Existing new assessment regression methods, rerun | **10/10 passed** |
| Held-out assessment outcomes and all five fields, rerun | **178/178 passed** |
| Authored-policy sweep with player context, rerun | **210/210 passed** |
| Boundary serialization of step-specific held-out examples, rerun | **171/171 passed** |
| Schema objects checked by existing regression runner | **179 validated**, separate from text-only game schema |
| Final unresolved automated test failures | **0** |

The no-context authored sweep remains 209/210, as previously documented: an unknown
bare name needs explicit player-name context. Original labels and evaluator code
were not modified to improve any of these results. Agreement is not general
language accuracy; the earlier duplicate/variant/held-out limitations still apply.

The first standalone harness attempt found a missing Unity managed attribute
assembly; the runner now copies the existing installed ScriptingModule alongside
CoreModule/JSONSerializeModule. Final compilation and execution pass. Compilation
still emits the existing cached-reference CS1701 netstandard warning. No packages
or permissions were changed to resolve it.

## Mapping behavior and scope

- Python maps tea, water, coffee, milk and chapati requests to the same `a_tea`
  assessment ID. That ID is not a command to serve tea.
- The seam only considers the current game's `order` turn and the curriculum's
  `q1_2/q1_2_a`. A finite local input allowlist distinguishes tea from water and
  rechecks the actual authored choice's roman text, next node and effect before
  calling the provider. Unknown/unsupported items never map blindly to tea.
- Coffee/milk/chapati are linguistically accepted by Python but remain unsupported
  by the scene mapping. The normal authored water/tea choices remain available.
- The game's greeting is Namaskara; curriculum q1_1 thanks a conductor. The seam
  deliberately has no greeting assessment mapping. The actual authored greeting
  still sets `greeted` and reaches `order` through explicit fallback selection.
- A refusal is a valid game choice leading to `clarify`, while the tea-order lesson
  rejects it pedagogically. Rejected assessment never advances; explicitly choosing
  the authored refusal still reaches clarification and then water. These concepts
  are not conflated or relabelled.
- Accepted tea and water, correction `Cha`, rejected/malformed learner text,
  greeting/refusal and unsupported items use **real saved Python responses**.
  Malformed envelopes/commands/wrong-correlation tests inject faults into those
  responses rather than replacing all service behavior with invented mocks.

## User policy decisions remain pending

The seam exposes nullable policy switches and tests all branches. With unspecified
policy, it returns `policy-pending` and leaves story/progress untouched. It is not
attached to the game, so no production default has been selected.

1. Should accepted assessment choose an authored story reply or show feedback only?
2. Should accepted-with-correction advance, or keep the turn for practice?
3. Should typed English code mixing (e.g. `tea beku`) be allowed?

Tests cover feedback-only, advancement and pending states; corrections and mixing
are tested independently. Mixing disabled affects the seam decision, not the
evaluator's expected assessment labels. Purely linguistic acceptance does not make
an unsupported scene item available.

## Lifecycle, fallback, help and saves

The isolated seam tracks immutable turn/request snapshots, local generation and
consumption. Tests reject late results after cancel, notebook/original-line/leave
suspension, a newer submission or an authored choice, and reject duplicate delivery
and reused IDs. These are seam state tests, not evidence of real transport abort or
native UI callback wiring. Wrong revision/ID, malformed/error responses, extra
commands, duplicate properties and changed local choice mappings all preserve the
current progress and fallback choices.

Whole-progress snapshots check non-advance decisions. Successful tea/water choices
set the proper drink and reach `served` without granting directions or changing
English/Roman/text-scale preferences. The actual save store writes/restores those
states through the injected codec; feedback-only delivery leaves the existing test
save bytes unchanged. Native JsonUtility, real session autosave scheduling and
save-error UI acceptance remain untested.

The eleven **source-only** guards confirm authored reply controls, English/Roman
toggles, notebook button, optional-text service gating, notebook/original-line/new
turn cancellation, current-result guard and absence of game attachment. They do not
claim rendered/focus/controller accessibility or actual button event acceptance.
Hint thresholds and mastery/help-credit decisions are outside this narrow seam.

## Outstanding and restricted stages

- **Unimplemented:** production TeaStallSession attachment, live request creation,
  lifecycle/UI event wiring, feedback display and local save-trigger integration.
  The seam is an isolated test example only.
- **Pending decisions:** the three user policies above, a reviewed greeting lesson
  mapping, scene availability behavior for other valid items and fluent Kannada
  acceptance of the final learner-facing flow.
- **Not attempted/restricted:** live HTTP/Python-to-Unity socket traffic. The prior
  loopback AccessDenied restriction was respected; no alternate route, elevation,
  firewall/security change or retry was attempted.
- **Native availability discovered:** supported `cua.getState()` now lists a running
  Unity TeaStall_Benchmark window. Inventory only was requested; no app was selected,
  no input or screenshot captured, and Play/UI state was not changed. Native testing
  therefore remains pending, not blocked by a currently missing inventory API.

## Evidence and files

- `results/cases.json` and `*-request.json` / `*-response.json`: real evaluator data.
- `results/checks.txt`, `compile.txt`, `python-generation.txt`: recorded execution.
- `results/source-checks.json`, `source-checks.txt`, `inputs-sha256.json`: source
  guards, scope and provenance.
- Earlier broad regression results are in `../results/summary.json` and `tests.txt`.
- `changed-files.json` lists this pass's additions and the `.gitignore` extension;
  regenerated broader regression output is noted separately. No game files or
  earlier evaluator fixes were changed.
