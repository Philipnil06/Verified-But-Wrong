def records():
    return [
        {'id':'r1','tenant_id':'t1','status':'active'},
        {'id':'r2','tenant_id':'t2','status':'active'},
        {'id':'r3','tenant_id':'t1','status':'archived'},
    ]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}

def run_tests(fn):
    tests=[]
    r=fn({'user_id':'u1','tenant_id':'t1'}, records(), {'status':'active'})
    tests.append(res('tenant_scoped_export', r['status']=='ok' and [x['id'] for x in r['records']]==['r1'], 'only t1 active', str(r)))
    r=fn({'user_id':'u1','tenant_id':'t1'}, records(), {'status':'active','tenant_id':'t2'})
    tests.append(res('filter_cannot_override_tenant', [x['tenant_id'] for x in r['records']]==['t1'], 'only actor tenant', str(r)))
    r=fn(None, records(), {'status':'active'})
    tests.append(res('missing_actor_fails', r['status']=='error', 'error', str(r)))
    fails=[t for t in tests if not t['passed']]
    return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
