import copy
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'src'))
from matcher import AnswerMatcher
from assessment import AssessmentBoundary, ContractError, parse_request
from verification.policy_cases import authored_cases, FIELDS


class AssessmentRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matcher = AnswerMatcher(ROOT/'data')
        cls.boundary = AssessmentBoundary(cls.matcher)

    def request(self, text='Nanage haalu beku', quest='q1_2', step='q1_2_a'):
        return dict(version=1,request_id='0123456789abcdef0123456789abcdef',quest_id=quest,step_id=step,learner_text=text,player={'name':'Meera'})

    def test_all_heldout_fields(self):
        with (ROOT/'data/responses_test.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),178)
        for row in rows:
            with self.subTest(row=row['row_id']):
                result=self.matcher.evaluate(row['quest_id'],row['step_id'],row['input_text'],row['player'])
                self.assertEqual({k:result[k] for k in FIELDS},dict(zip(FIELDS,[row['expected_outcome']]+[row[k] for k in FIELDS[1:]])))

    def test_authored_policy(self):
        cases=authored_cases(self.matcher.content_dir)
        self.assertEqual(len(cases),210)
        for case in cases:
            with self.subTest(step=case['step_id'],text=case['text']):
                # Bare unknown name has an explicitly documented context requirement.
                player={'name':'Meera'} if case['text']=='Meera' else None
                result=self.matcher.evaluate(case['quest_id'],case['step_id'],case['text'],player)
                self.assertEqual({k:result[k] for k in case['expected']},case['expected'])

    def test_fail_closed_negative_cases(self):
        cases=[('q1_2','q1_2_a','Nimage haalu beku'),('q1_2','q1_2_a','Nanage haalu beda'),
               ('q1_2','q1_2_a','Nanage stone beku'),('q1_2','q1_2_a','Nanage haalu beku beda'),
               ('q1_3','q1_3_a','Nanna hesaru'),('q1_3','q1_3_a','Nanna hesaru idk'),
               ('q1_3','q1_3_a','Meera'),('q1_3','q1_3_a','xyzqwerty'),
               ('q1_3','q1_3_a','Nimage hesaru Meera'),('q1_3','q1_3_a','Nanna hesaru tea beku'),
               ('q2_2','q2_2_a','Ananya hatra keeli illa'),('q2_2','q2_2_a','Somanna hatra keeli ide Ananya alla'),
               ('q3_1','q3_1_a','Haudu oota kodi beda'),('q3_1','q3_1_a','stone kodi'),
               ('q1_2','q1_2_a','Nanage chaba bekx')]
        for q,s,text in cases:
            with self.subTest(text=text):self.assertEqual(self.matcher.evaluate(q,s,text)['outcome'],'not_accepted')

    def test_player_context_and_long_names(self):
        for name in ['Meera','Priya Rao','Anjali','Ananya','Ravi']:
            self.assertEqual(self.matcher.evaluate('q1_3','q1_3_a',name,{'name':name})['outcome'],'accepted')
            self.assertEqual(self.matcher.evaluate('q1_3','q1_3_a','Nanna hesaru '+name)['outcome'],'accepted')
        self.assertEqual(self.matcher.evaluate('q1_3','q1_3_a','Meera',{'name':'Priya'})['outcome'],'not_accepted')
        self.assertEqual(self.matcher.evaluate('q1_3','q1_3_a','Anna',{'name':'Anna'})['outcome'],'accepted')

    def test_global_diagnostics_and_mixed_answer(self):
        for (q,s),step in self.matcher.policy.steps.items():
            if step['type']!='respond':continue
            for text,category in [('Hello','english_only'),('Thank you','english_only'),('Chai chahiye','hindi_word')]:
                result=self.matcher.evaluate(q,s,text)
                self.assertEqual(result['outcome'],'not_accepted')
                self.assertEqual(result['error_category'],category)
                if step['speaker']=='somanna' and category=='english_only':self.assertEqual(result['reaction_id'],'r_somanna_ignores')
        self.assertEqual(self.matcher.evaluate('q1_1','q1_1_a','Thank you dhanyavada')['outcome'],'accepted')

    def test_socket_free_round_trip_and_context(self):
        request=self.request(); response=json.loads(self.boundary.handle_json(json.dumps(request).encode()))
        self.assertEqual(response['status'],'ok')
        for k in ('version','request_id','quest_id','step_id'):self.assertEqual(response[k],request[k])
        self.assertEqual(response['assessment']['outcome'],'accepted')
        self.assertEqual(len(response['content_revision']),64)
        self.assertNotIn('effect',json.dumps(response));self.assertNotIn('save',json.dumps(response))

    def test_invalid_requests(self):
        mutations=[('version',True),('version',2),('request_id','wrong'),('quest_id','unknown'),('step_id','q1_2_c'),
                   ('learner_text',None),('learner_text',''),('learner_text','x'*513),('learner_text','\U0001f600'*257),
                   ('learner_text','\ud800'),('player',{'name':'Meera','effect':'win'})]
        for k,v in mutations:
            with self.subTest(field=k,value=repr(v)[:30]):
                request=self.request();request[k]=v
                response=json.loads(self.boundary.handle_json(json.dumps(request).encode()))
                self.assertEqual(response['status'],'error')
        request=self.request();request['effect']='win'
        with self.assertRaises(ContractError):self.boundary.assess(request)

    def test_invalid_json(self):
        for body in [b'{}{}',b'{"version":1,"version":1}',b'\xff',b'NaN',b'x'*65537,b'['*20+b'0'+b']'*20]:
            self.assertEqual(json.loads(self.boundary.handle_json(body))['status'],'error')

    def test_recorded_fixtures(self):
        for path in (ROOT/'docs/fixtures').glob('*-request.json'):
            expected=json.loads(path.with_name(path.name.replace('-request','-response')).read_text(encoding='utf8'))
            self.assertEqual(json.loads(self.boundary.handle_json(path.read_bytes())),expected)

    def test_response_validation_and_sanitized_failures(self):
        step=self.matcher.policy.steps[('q1_2','q1_2_a')]
        good=self.matcher.evaluate('q1_2','q1_2_a','Chaha beku')
        for k,v in [('confidence',float('nan')),('confidence',True),('effect','win'),('answer_id','foreign'),('outcome','advance')]:
            bad=dict(good);bad[k]=v
            with self.assertRaises(ContractError):self.boundary.validate_result(bad,step)
        class Broken:
            def evaluate(self,*args,**kwargs):raise RuntimeError('secret learner text')
        boundary=copy.copy(self.boundary);boundary.matcher=Broken()
        # Accessing policy/evaluation fails internally, never exposing exception text.
        result=boundary.handle_json(json.dumps(self.request()).encode())
        self.assertNotIn(b'secret',result);self.assertEqual(json.loads(result)['error']['code'],'internal_error')


if __name__=='__main__':unittest.main()
