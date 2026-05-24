def records():
    return [
        {'id':'r1','tenant_id':'t1','status':'active'},
        {'id':'r2','tenant_id':'t2','status':'active'},
        {'id':'r3','tenant_id':'t1','status':'archived'},
    ]
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}

def valid_export(fn):
    r=fn({'tenant_id':'t1'}, [{'id':'r1','tenant_id':'t1','status':'active'}], {'status':'active'}); return res('Valid tenant export succeeds', r['status']=='ok' and len(r['records'])==1, 'ok one', str(r))
def no_cross_tenant(fn):
    r=fn({'tenant_id':'t1'}, records(), {'status':'active'}); return res('Export must not include records from other tenants', all(x['tenant_id']=='t1' for x in r['records']) and len(r['records'])==1, 'only t1', str(r))
def tenant_required(fn):
    r=fn({}, records(), {'status':'active'}); return res('Requester tenant_id must be required', r['status']=='error', 'error', str(r))
def no_override(fn):
    r=fn({'tenant_id':'t1'}, records(), {'status':'active','tenant_id':'t2'}); return res('Filters must not override tenant isolation', all(x['tenant_id']=='t1' for x in r['records']), 'only t1', str(r))
def count_match(fn):
    r=fn({'tenant_id':'t1'}, records(), {'status':'active'}); return res('Exported record count must match tenant-scoped results', len(r['records'])==1, 'count 1', str(r))
REQUIREMENT_TESTS={'Valid tenant export succeeds':valid_export,'Export must not include records from other tenants':no_cross_tenant,'Requester tenant_id must be required':tenant_required,'Filters must not override tenant isolation':no_override,'Exported record count must match tenant-scoped results':count_match}
