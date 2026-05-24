def actor(role='admin'): return {'user_id':'admin1','role':role}
def user(): return {'user_id':'u1','status':'active'}
def log(): return [{'event':'created','user_id':'u1'}]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def valid(fn):
    out=fn(actor(),user(),log()); return res('Valid delete succeeds', out['status']=='ok','ok',str(out))
def preserve(fn):
    out=fn(actor(),user(),log()); return res('Required audit records must be preserved', len(out['audit_log'])>=2 and out['audit_log'][0]['event']=='created','preserved',str(out))
def metadata(fn):
    out=fn(actor(),user(),log()); return res('Deletion metadata must be recorded', any(x.get('event')=='user_deleted' for x in out['audit_log']),'metadata',str(out))
def admin(fn):
    out=fn(actor('member'),user(),log()); return res('Only admins may delete users', out['status']=='error','error',str(out))
def state(fn):
    out=fn(actor(),user(),log()); return res('Deleted state must be updated', out['user']['status']=='deleted','deleted',str(out))
REQUIREMENT_TESTS={'Valid delete succeeds':valid,'Required audit records must be preserved':preserve,'Deletion metadata must be recorded':metadata,'Only admins may delete users':admin,'Deleted state must be updated':state}
