def export_records(actor, records, filters):
    if not actor or not actor.get('tenant_id') or records is None:
        return {'status':'error','message':'missing actor or records','records':[]}
    status=filters.get('status') if filters else None
    tenant=actor['tenant_id']
    out=[r.copy() for r in records if r.get('tenant_id')==tenant and (status is None or r.get('status')==status)]
    return {'status':'ok','message':'exported','records':out}
