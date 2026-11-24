"""Expand authored policy without modifying labels or consulting held-out results."""
import json
from pathlib import Path

FIELDS = ('outcome', 'answer_id', 'error_category', 'correction_type', 'reaction_id')


def authored_cases(content):
    content = Path(content)
    vocab = {w['word_id']: w for w in json.loads((content/'vocabulary.json').read_text(encoding='utf-8-sig'))['words']}
    feedback = json.loads((content/'feedback.json').read_text(encoding='utf-8-sig'))
    players = json.loads((content/'address_terms.json').read_text(encoding='utf-8-sig'))['players']
    def expand(text, language):
        if '{player_name}' in text:
            names = ['Arun','Aditi','Meera'] if language == 'kanglish' else [v['kannada'] for v in players.values()]
            return [text.replace('{player_name}', name) for name in names]
        if '{item}' in text:
            return [text.replace('{item}', vocab[wid]['kanglish']) for wid in feedback['answer_rules']['item_words']]
        return [text]
    cases = []
    for path in sorted((content/'quests').glob('*.json')):
        q = json.loads(path.read_text(encoding='utf-8-sig'))
        for s in q['steps']:
            if s['type'] != 'respond': continue
            def add(pattern, expected, language='kanglish'):
                for text in expand(pattern,language):
                    cases.append(dict(quest_id=q['quest_id'],step_id=s['step_id'],text=text,expected=expected,language=language))
            for a in s['accepted']:
                expected = dict(outcome='accepted_with_correction' if a.get('correction_type') else 'accepted',answer_id=a['answer_id'])
                for key in ('correction_type','reaction_id'):
                    if a.get(key): expected[key]=a[key]
                for lang in ('kanglish','kannada'):
                    if a.get(lang): add(a[lang], expected, lang)
                for text in a.get('also_accepted',[]): add(text,expected)
                for c in a.get('accepted_with_correction',[]):
                    expected_c=dict(outcome='accepted_with_correction',answer_id=a['answer_id'],correction_type=c['correction_type'])
                    if c.get('reaction_id'):expected_c['reaction_id']=c['reaction_id']
                    add(c['kanglish'],expected_c)
            for a in s.get('anticipated_errors',[]):
                expected=dict(outcome='not_accepted',error_category=a['error_category'])
                if a.get('reaction_id'):expected['reaction_id']=a['reaction_id']
                for lang in ('kanglish','kannada'):
                    if a.get(lang):add(a[lang],expected,lang)
                for text in a.get('also_matches',[]):add(text,expected)
    return cases
