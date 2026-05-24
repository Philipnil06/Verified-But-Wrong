def export_records(actor, records, filters):
    if not actor or records is None:
        return {'status':'error','message':'invalid','records':[]}
    tenant=(filters or {}).get('tenant_id', actor.get('tenant_id'))
    status=(filters or {}).get('status')
    return {'status':'ok','message':'exported','records':[r.copy() for r in records if r.get('tenant_id')==tenant and (status is None or r.get('status')==status)]}
