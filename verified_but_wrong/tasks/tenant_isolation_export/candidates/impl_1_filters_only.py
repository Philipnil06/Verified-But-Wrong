def export_records(actor, records, filters):
    if actor is None or records is None:
        return {'status':'error','message':'invalid input','records':[]}
    status=filters.get('status') if filters else None
    out=[r.copy() for r in records if status is None or r.get('status')==status]
    return {'status':'ok','message':'exported','records':out}
