def user(role='admin'): return {'user_id':'u1','role':role}
def sessions(): return [{'session_id':'s1','user_id':'u1','privileged':True,'active':True},{'session_id':'s2','user_id':'u2','privileged':True,'active':True}]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def run_tests(fn):
    tests=[]; out=fn(user(), sessions(), 'member'); tests.append(res('role_updates', out['status']=='ok' and out['user']['role']=='member','ok',str(out)))
    out=fn(user(), sessions(), 'owner'); tests.append(res('invalid_role_fails', out['status']=='error','error',str(out)))
    fails=[t for t in tests if not t['passed']]; return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
