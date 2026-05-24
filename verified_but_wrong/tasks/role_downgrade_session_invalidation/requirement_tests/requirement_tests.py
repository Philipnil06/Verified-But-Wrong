def user(role='admin'): return {'user_id':'u1','role':role}
def sessions(): return [{'session_id':'s1','user_id':'u1','privileged':True,'active':True},{'session_id':'s2','user_id':'u2','privileged':True,'active':True}]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def valid(fn):
    out=fn(user(),sessions(),'member'); return res('Valid role update succeeds', out['status']=='ok' and out['user']['role']=='member','ok',str(out))
def invalidate(fn):
    out=fn(user(),sessions(),'member'); return res('Admin role downgrade must invalidate privileged sessions', not out['sessions'][0]['active'],'inactive',str(out))
def invalid(fn):
    out=fn(user(),sessions(),'owner'); return res('Invalid roles must fail', out['status']=='error','error',str(out))
def missing(fn):
    out=fn(None,sessions(),'member'); return res('Missing users must fail', out['status']=='error','error',str(out))
def state(fn):
    out=fn(user(),sessions(),'member'); return res('Session state must be updated after downgrade', not out['sessions'][0]['active'],'updated',str(out))
REQUIREMENT_TESTS={'Valid role update succeeds':valid,'Admin role downgrade must invalidate privileged sessions':invalidate,'Invalid roles must fail':invalid,'Missing users must fail':missing,'Session state must be updated after downgrade':state}
