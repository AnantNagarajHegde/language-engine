"""Socket-free assessment v1 boundary. Unity owns all progression and saves."""
import hashlib
import json
import math
import re

MAX_BODY_BYTES = 65536
FIELDS = {'outcome', 'answer_id', 'error_category', 'correction_type', 'reaction_id', 'detected_form', 'confidence'}


class ContractError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def exact_object(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ContractError('invalid_request')


def bounded_text(value, limit, required=True):
    if type(value) is not str or (required and not value.strip()):
        raise ContractError('invalid_request')
    try:
        if len(value.encode('utf-16-le', 'strict')) // 2 > limit:
            raise ContractError('invalid_request')
    except UnicodeError:
        raise ContractError('invalid_request') from None
    return value


def parse_request(body):
    if type(body) is not bytes or len(body) > MAX_BODY_BYTES:
        raise ContractError('invalid_json')
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ContractError('invalid_json')
            obj[key] = value
        return obj
    def bad_constant(_):
        raise ContractError('invalid_json')
    try:
        text = body.decode('utf-8', 'strict')
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise ContractError('invalid_json') from None
    def depth(obj, level=0):
        if level > 8:
            raise ContractError('invalid_json')
        if isinstance(obj, dict):
            for child in obj.values(): depth(child, level+1)
        elif isinstance(obj, list):
            for child in obj: depth(child, level+1)
    depth(value)
    return value


class AssessmentBoundary:
    def __init__(self, matcher):
        self.matcher = matcher
        # Hash the loaded content and training/spelling bytes, not a mutable save.
        digest = hashlib.sha256()
        for path in sorted(matcher.content_dir.rglob('*.json')) + [matcher.data_dir/'responses_train.csv', matcher.data_dir/'spelling_variants.csv']:
            digest.update(path.name.encode('utf-8')); digest.update(b'\0'); digest.update(path.read_bytes()); digest.update(b'\0')
        self.content_revision = digest.hexdigest()

    def assess(self, request):
        exact_object(request, {'version', 'request_id', 'quest_id', 'step_id', 'learner_text', 'player'})
        if type(request['version']) is not int:
            raise ContractError('invalid_request')
        if request['version'] != 1:
            raise ContractError('unsupported_version')
        if type(request['request_id']) is not str or not re.fullmatch('[0-9a-f]{32}', request['request_id']):
            raise ContractError('invalid_request')
        for key in ('quest_id', 'step_id'):
            bounded_text(request[key], 128)
        bounded_text(request['learner_text'], 512)
        exact_object(request['player'], {'name'})
        bounded_text(request['player']['name'], 80, required=False)
        step = self.matcher.policy.steps.get((request['quest_id'], request['step_id']))
        if step is None:
            raise ContractError('unknown_step')
        if step['type'] != 'respond':
            raise ContractError('unsupported_step')
        result = self.matcher.evaluate(request['quest_id'], request['step_id'], request['learner_text'], player=request['player'])
        self.validate_result(result, step)
        return dict(version=1, request_id=request['request_id'], quest_id=request['quest_id'], step_id=request['step_id'],
                    status='ok', content_revision=self.content_revision, assessment=result)

    def validate_result(self, result, step):
        try:
            exact_object(result, FIELDS)
            for key in FIELDS-{'confidence'}: bounded_text(result[key], 128, required=False)
            if type(result['confidence']) not in (int, float) or not math.isfinite(result['confidence']) or not 0 <= result['confidence'] <= 1:
                raise ValueError()
            outcome = result['outcome']
            if outcome not in {'accepted', 'accepted_with_correction', 'not_accepted'}:
                raise ValueError()
            if result['detected_form'] not in {'kanglish', 'kannada', 'english', 'hindi_roman', 'mixed', 'digits', 'noise'}:
                raise ValueError()
            feedback = self.matcher.policy.feedback
            if result['error_category'] and result['error_category'] not in {r['error_category'] for r in feedback['error_categories']}:
                raise ValueError()
            if result['correction_type'] and result['correction_type'] not in {r['correction_type'] for r in feedback['correction_types']}:
                raise ValueError()
            if result['reaction_id'] and result['reaction_id'] not in {r['reaction_id'] for r in feedback['reactions']}:
                raise ValueError()
            allowed_ids = {a['answer_id'] for a in step.get('accepted', [])+step.get('anticipated_errors', [])}
            if result['answer_id'] and result['answer_id'] not in allowed_ids:
                raise ValueError()
            if outcome == 'not_accepted':
                if not result['error_category'] or result['correction_type']: raise ValueError()
            elif not result['answer_id'] or result['error_category']:
                raise ValueError()
            elif (outcome == 'accepted_with_correction') != bool(result['correction_type']):
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            raise ContractError('invalid_assessment') from None

    def handle_json(self, body):
        request = None
        try:
            request = parse_request(body)
            response = self.assess(request)
        except ContractError as error:
            response = self.error(request, error.code)
        except Exception:
            # Fixed public error; never include learner text, paths or exception data.
            response = self.error(request, 'internal_error')
        return json.dumps(response, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')

    def error(self, request, code):
        rid = request.get('request_id') if type(request) is dict else ''
        if type(rid) is not str or not re.fullmatch('[0-9a-f]{32}', rid): rid = ''
        return dict(version=1, request_id=rid, status='error', error={'code': code})
