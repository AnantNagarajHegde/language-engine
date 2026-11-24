"""Run with python -I -B verification/verify.py; no sockets or pytest required."""
import csv
import hashlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from matcher import AnswerMatcher
from assessment import AssessmentBoundary
from verification.policy_cases import authored_cases, FIELDS


def run():
    out=ROOT/'verification/results';out.mkdir(exist_ok=True)
    matcher=AnswerMatcher(ROOT/'data');boundary=AssessmentBoundary(matcher)
    plain=[];suite=unittest.TestSuite()
    for file in sorted((ROOT/'tests').glob('test_*.py')):
        spec=importlib.util.spec_from_file_location(file.stem,file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        for name,fn in vars(module).items():
            if name.startswith('test_') and callable(fn):
                try:fn();plain.append({'test':file.name+':'+name,'passed':True})
                except Exception as error:plain.append({'test':file.name+':'+name,'passed':False,'error':repr(error)})
    stream=io.StringIO();unit=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (out/'tests.txt').write_text(stream.getvalue(),encoding='utf8')
    def write(name,value):(out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
    summary={'existing_plain_functions':{'total':len(plain),'passed':sum(r['passed'] for r in plain)},'unittest_methods':{'total':unit.testsRun,'passed':unit.wasSuccessful()},'datasets':{}}
    write('existing-tests.json',plain)
    for split in ['train','test']:
        with (ROOT/'data'/('responses_'+split+'.csv')).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        results=[]
        for row in rows:
            result=matcher.evaluate(row['quest_id'],row['step_id'],row['input_text'],row['player'])
            expected=dict(zip(FIELDS,[row['expected_outcome']]+[row[k] for k in FIELDS[1:]]))
            diff={k:{'expected':v,'actual':result[k]} for k,v in expected.items() if result[k]!=v}
            results.append(dict(row_id=row['row_id'],quest_id=row['quest_id'],step_id=row['step_id'],text=row['input_text'],expected=expected,actual=result,differences=diff))
        summary['datasets'][split]={'rows':len(rows),'outcome_matches':sum(r['expected']['outcome']==r['actual']['outcome'] for r in results),'all_fields_match':sum(not r['differences'] for r in results)}
        write(split+'-evaluation.json',results)
    cases=authored_cases(matcher.content_dir);policy=[]
    for case in cases:
        result=matcher.evaluate(case['quest_id'],case['step_id'],case['text'])
        diff={k:{'expected':v,'actual':result[k]} for k,v in case['expected'].items() if result[k]!=v}
        contextual=matcher.evaluate(case['quest_id'],case['step_id'],case['text'],{'name':'Meera'}) if case['text']=='Meera' else result
        policy.append(dict(case,actual=result,differences=diff,contextual_actual=contextual))
    write('authored-evaluation.json',policy)
    summary['authored_policy']={'cases':len(cases),'mismatches_without_player_context':sum(bool(r['differences']) for r in policy),'mismatches_with_player_context':sum(any(r['contextual_actual'][k]!=v for k,v in r['expected'].items()) for r in policy)}
    # Execute assessment validation/serialization for every held-out respond example.
    serialized=[]
    for i,row in enumerate(json.loads((out/'test-evaluation.json').read_text(encoding='utf8'))):
        if row['step_id']=='ALL':continue
        request=dict(version=1,request_id=format(i,'032x'),quest_id=row['quest_id'],step_id=row['step_id'],learner_text=row['text'],player={'name':''})
        response=json.loads(boundary.handle_json(json.dumps(request,ensure_ascii=False).encode('utf8')))
        serialized.append({'row_id':row['row_id'],'status':response['status'],'response':response})
    write('boundary-heldout.json',serialized)
    summary['boundary_heldout']={'cases':len(serialized),'ok':sum(r['status']=='ok' for r in serialized)}
    baseline=json.loads((ROOT/'verification/baseline/summary.json').read_text(encoding='utf8'))
    summary['before']={k:baseline[k] for k in ['existing_tests','datasets','authored']}
    summary['source_hashes']={str(path.relative_to(ROOT.parent)):hashlib.sha256(path.read_bytes()).hexdigest() for path in list((ROOT/'src').glob('*.py'))+list((ROOT/'data').glob('*.csv'))+list(matcher.content_dir.rglob('*.json'))}
    before=baseline['source_hashes']
    summary['changed_original_files']=[p for p,h in before.items() if hashlib.sha256((ROOT.parents[1]/p).read_bytes()).hexdigest()!=h]
    schema_path=ROOT/'docs/assessment-v1.schema.json'
    if schema_path.exists():
        import jsonschema
        schema=json.loads(schema_path.read_text(encoding='utf8'));jsonschema.Draft202012Validator.check_schema(schema)
        count=0
        for row in serialized:
            jsonschema.validate(row['response'],schema);count+=1
        # Contract separation: assessment fixtures must fail current game's text-only schema.
        game=ROOT.parents[1]/'game/docs/contracts/nlp-v1.schema.json'
        old=json.loads(game.read_text(encoding='utf8'))
        response=serialized[0]['response']
        assert not jsonschema.Draft202012Validator(old).is_valid(response)
        for path in (ROOT/'docs/fixtures').glob('*.json'):
            jsonschema.validate(json.loads(path.read_text(encoding='utf8')),schema);count+=1
        summary['schema_checked_objects']=count
        summary['current_game_text_contract_rejects_assessment']=True
    write('summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['source_hashes','before']},indent=2))
    if not unit.wasSuccessful() or not all(r['passed'] for r in plain) or summary['datasets']['test']['all_fields_match']!=178 or summary['authored_policy']['mismatches_with_player_context'] or summary['boundary_heldout']['ok']!=len(serialized):return 1
    return 0


if __name__=='__main__':raise SystemExit(run())
