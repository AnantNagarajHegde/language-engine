"""Source guards, not native UI acceptance or live cancellation tests."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
runtime=ROOT.parents[1]/'game/My project (1)/Assets/_Paridhwani/Scripts/Runtime'
ui=(runtime/'TeaStallUI.cs').read_text(encoding='utf8')
session=(runtime/'TeaStallSession.cs').read_text(encoding='utf8')
requests=(runtime/'DialogueTextRequests.cs').read_text(encoding='utf8')
checks={
 'authored_fallback_choice_buttons': 'session.Choose(index)' in ui,
 'english_help_toggle': 'dialogue-english' in ui,
 'roman_help_toggle': 'dialogue-roman' in ui,
 'notebook_help_button': 'dialogue-notebook' in ui,
 'optional_text_controls_require_service': 'if(session.OptionalDialogueText!=null)' in ui,
 'notebook_cancels_optional_text': 'SuspendDialogueText();' in session.split('public void OpenNotebook()',1)[1].split('public void Close()',1)[0],
 'original_line_cancels_optional_text': 'textRequests.Cancel();' in requests.split('public void UseAuthoredDialogue()',1)[1].split('void NewDialogueTurn()',1)[0],
 'new_turn_invalidates_optional_text': 'textRequests.Cancel();' in requests.split('void NewDialogueTurn()',1)[1].split('void SuspendDialogueText()',1)[0],
 'optional_reply_generation_guard': '!textRequests.IsCurrent(reply)' in requests,
 'isolated_example_not_attached_to_game': not any('TeaAssessmentSeam' in p.read_text(encoding='utf8') for p in runtime.glob('*.cs')),
}
hashes=json.loads((ROOT/'verification/tea-milestone/results/inputs-sha256.json').read_text(encoding='utf8'))
checks['compiled_source_inputs_unchanged_during_run']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
output={'scope':'source checks only; no rendered controls, input/focus or native session/save lifecycle exercised','checks':checks}
(ROOT/'verification/tea-milestone/results/source-checks.json').write_text(json.dumps(output,indent=2),encoding='utf8')
print('TEA_SOURCE_GUARDS:',sum(checks.values()),'/',len(checks))
raise SystemExit(0 if all(checks.values()) else 1)
