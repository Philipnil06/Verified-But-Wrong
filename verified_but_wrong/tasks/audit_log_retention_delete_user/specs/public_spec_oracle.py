def actor(role='admin'): return {'user_id':'admin1','role':role}
def user(): return {'user_id':'u1','status':'active'}
def log(): return [{'event':'created','user_id':'u1'}]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def run_tests(fn):
    tests=[]; out=fn(actor(),user(),log()); tests.append(res('audit_preserved', len(out['audit_log'])>=2 and out['audit_log'][0]['event']=='created','preserve + append',str(out)))
    tests.append(res('metadata_recorded', any(x.get('event')=='user_deleted' and x.get('actor_id')=='admin1' for x in out['audit_log']),'metadata',str(out)))
    out=fn(actor('member'),user(),log()); tests.append(res('member_fails', out['status']=='error','error',str(out)))
    fails=[t for t in tests if not t['passed']]; return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
