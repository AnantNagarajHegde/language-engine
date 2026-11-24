import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from assessment_host import respond,ROUTE
from assessment import AssessmentBoundary
from matcher import AnswerMatcher

class HostChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.boundary=AssessmentBoundary(AnswerMatcher(ROOT/'data'))
 def test_real_exchange(self):
  request=(ROOT/'docs/fixtures/accepted-request.json').read_bytes()
  status,body=respond(self.boundary,ROUTE,'application/json; charset=utf-8',request)
  self.assertEqual(status,200);self.assertEqual(json.loads(body)['assessment']['outcome'],'accepted')
 def test_bad_routes_types_limits_and_json(self):
  for path,ctype,body,status in [(ROUTE+'?x=1','application/json',b'{}',404),(ROUTE,'text/plain',b'{}',415),(ROUTE,'application/json',b'x'*65537,413)]:
   self.assertEqual(respond(self.boundary,path,ctype,body)[0],status)
  self.assertEqual(json.loads(respond(self.boundary,ROUTE,'application/json',b'{')[1])['error']['code'],'invalid_json')
