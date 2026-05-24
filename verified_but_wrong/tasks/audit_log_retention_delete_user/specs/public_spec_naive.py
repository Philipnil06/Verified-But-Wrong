def actor(role='admin'): return {'user_id':'admin1','role':role}
def user(): return {'user_id':'u1','status':'active'}
def log(): return [{'event':'created','user_id':'u1'}]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def run_tests(fn):
    tests=[]; out=fn(actor(),user(),log()); tests.append(res('delete_sets_status', out['status']=='ok' and out['user']['status']=='deleted','deleted',str(out)))
    fails=[t for t in tests if not t['passed']]; return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
