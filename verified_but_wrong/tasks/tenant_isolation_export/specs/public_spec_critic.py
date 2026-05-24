def records():
    return [
        {'id':'r1','tenant_id':'t1','status':'active'},
        {'id':'r2','tenant_id':'t2','status':'active'},
        {'id':'r3','tenant_id':'t1','status':'archived'},
    ]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}

def run_tests(fn):
    tests=[]
    r=fn({'user_id':'u1','tenant_id':'t1'}, [{'id':'r1','tenant_id':'t1','status':'active'}], {'status':'active'})
    tests.append(res('valid_export_ok', r['status']=='ok' and len(r['records'])==1, 'ok', str(r)))
    r=fn(None, records(), {'status':'active'})
    tests.append(res('missing_actor_fails', r['status']=='error', 'error', str(r)))
    fails=[t for t in tests if not t['passed']]
    return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
