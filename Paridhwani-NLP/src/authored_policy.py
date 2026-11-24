"""Finite authored rules; no generated text or similarity-based acceptance."""
import json
import unicodedata
from pathlib import Path


class AuthoredPolicy:
    def __init__(self, content_dir, spelling):
        self.spelling = spelling
        root = Path(content_dir)
        self.feedback = json.loads((root / 'feedback.json').read_text(encoding='utf-8-sig'))
        vocabulary = json.loads((root / 'vocabulary.json').read_text(encoding='utf-8-sig'))['words']
        self.words = {w['word_id']: w for w in vocabulary}
        self.items = {self.norm(w[lang]) for wid in self.feedback['answer_rules']['item_words']
                      for w in [self.words[wid]] for lang in ('kanglish', 'kannada')}
        self.steps = {}
        for path in sorted((root / 'quests').glob('*.json')):
            quest = json.loads(path.read_text(encoding='utf-8-sig'))
            for step in quest['steps']:
                self.steps[(quest['quest_id'], step['step_id'])] = step
        self.reserved_names = {self.norm(w[lang]) for w in vocabulary if w['role'] != 'name' for lang in ('kanglish', 'english')}
        self.reserved_names.update({'hello', 'thanks', 'thank you', 'idk', 'unknown', 'xyzqwerty', 'not', 'no', 'yes'})
        self.kannada_markers = {self.norm(w['kanglish']) for w in vocabulary
                                if w['role'] != 'name' and self.norm(w['kanglish']) != self.norm(w['english'])}

    def norm(self, text):
        return self.spelling.normalize(text)

    def result(self, outcome, answer='', category='', correction='', reaction=''):
        return dict(outcome=outcome, answer_id=answer, error_category=category,
                    correction_type=correction, reaction_id=reaction, confidence=0.95)

    def valid_name(self, value, allow_vocabulary=False):
        tokens = value.split()
        return (1 <= len(tokens) <= 4 and len(value) <= 80
                and all(any(unicodedata.category(c).startswith('L') for c in token)
                        and all(unicodedata.category(c)[0] in 'LM' for c in token)
                        and (allow_vocabulary or token not in self.reserved_names) for token in tokens))

    def matches(self, pattern, text, player):
        # Preserve markers through punctuation normalization.
        pattern = pattern.replace('{player_name}', 'zzplayerzz').replace('{item}', 'zzitemzz')
        pattern = self.norm(pattern)
        if 'zzitemzz' in pattern:
            return any(text == pattern.replace('zzitemzz', item) for item in self.items)
        if 'zzplayerzz' in pattern:
            prefix, suffix = pattern.split('zzplayerzz')
            if not text.startswith(prefix) or (suffix and not text.endswith(suffix)):
                return False
            name = text[len(prefix):len(text)-len(suffix) if suffix else None].strip()
            supplied = player.get('name', '') if isinstance(player, dict) else player
            contextual = bool(supplied and supplied != 'any' and name == self.norm(supplied))
            if not self.valid_name(name, allow_vocabulary=contextual):
                return False
            # Bare unknown words cannot safely be distinguished from names.
            # Require supplied player context for that ambiguous form.
            if not prefix and not suffix:
                return contextual if supplied and supplied != 'any' else text in {'arun', 'aditi', 'ravi'}
            return True
        return text == pattern

    def match(self, quest, step_id, text, player=None):
        step = self.steps.get((quest, step_id))
        if not step:
            return None
        text = self.norm(text)
        # Explicit authored errors precede broad name/item templates.
        for error in step.get('anticipated_errors', []):
            for pattern in [error.get('kanglish', ''), error.get('kannada', '')] + error.get('also_matches', []):
                if pattern and self.matches(pattern, text, player):
                    return self.result('not_accepted', category=error['error_category'], reaction=error.get('reaction_id', 'r_puzzled'))
        for answer in step.get('accepted', []):
            for correction in answer.get('accepted_with_correction', []):
                if self.matches(correction['kanglish'], text, player):
                    return self.result('accepted_with_correction', answer['answer_id'], correction=correction['correction_type'], reaction=correction.get('reaction_id', ''))
            patterns = [answer.get('kanglish', ''), answer.get('kannada', '')] + answer.get('also_accepted', [])
            for pattern in patterns:
                if pattern and self.matches(pattern, text, player):
                    correction = answer.get('correction_type', '')
                    return self.result('accepted_with_correction' if correction else 'accepted', answer['answer_id'], correction=correction, reaction=answer.get('reaction_id', ''))
        return None

    def global_diagnostic(self, quest, step, text, detected):
        if (quest, step) not in self.steps:
            return None
        normalized = self.norm(text)
        words = set(normalized.split())
        category = ''
        if words & {'chahiye', 'shukriya', 'shukria', 'mujhe', 'nahi', 'kitna'}:
            category = 'hindi_word'
        elif (detected == 'english' and not words & self.kannada_markers) or normalized in {'hello', 'thank you', 'thanks'}:
            category = 'english_only'
        if not category:
            return None
        speaker = self.steps.get((quest, step), {}).get('speaker')
        reaction = 'r_somanna_ignores' if speaker == 'somanna' and category == 'english_only' else 'r_puzzled'
        return self.result('not_accepted', category=category, reaction=reaction)
