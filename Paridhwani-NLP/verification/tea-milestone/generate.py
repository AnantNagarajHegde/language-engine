"""Generate real, socket-free Python assessment exchanges for the C# milestone."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'src'))
from matcher import AnswerMatcher
from assessment import AssessmentBoundary
boundary=AssessmentBoundary(AnswerMatcher(ROOT/'data'))
out=ROOT/'verification/tea-milestone/results';out.mkdir(exist_ok=True)
cases=[]
for i,(name,text) in enumerate([('tea','Nanage chaha beku'),('water','Nanage neeru beku'),('correction','Cha'),('coffee','Nanage kaapi beku'),('milk','Nanage haalu beku'),('chapati','Nanage chapati beku'),('rejected','Nanage chaha beda'),('greeting','Namaskara'),('english-mix','tea beku'),('malformed-input','xyzqwerty')]):
    request=dict(version=1,request_id=format(i+1,'032x'),quest_id='q1_2',step_id='q1_2_a',learner_text=text,player={'name':'Meera'})
    body=json.dumps(request,ensure_ascii=False).encode('utf8')
    response=boundary.handle_json(body)
    (out/(name+'-request.json')).write_bytes(body)
    (out/(name+'-response.json')).write_bytes(response)
    cases.append(dict(name=name,request=request,response=json.loads(response)))
request=dict(cases[0]['request'],step_id='missing')
(out/'error-response.json').write_bytes(boundary.handle_json(json.dumps(request).encode()))
(out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
game=ROOT.parents[1]/'game/My project (1)/Assets/_Paridhwani/Scripts/Runtime'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [game/'TeaConversation.cs',game/'TeaProgress.cs',game/'TeaStallSession.cs',game/'TeaStallUI.cs',ROOT/'integration/AssessmentConsumer.cs']}
(out/'inputs-sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
print('REAL_ASSESSMENTS_GENERATED: 10 learner exchanges plus a real unknown-step error; no sockets.')
