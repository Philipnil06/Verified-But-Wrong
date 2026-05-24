def delete_user(actor, user, audit_log):
    if not actor or actor.get('role')!='admin' or not user: return {'status':'error','message':'invalid','user':user,'audit_log':audit_log}
    u=user.copy(); u['status']='deleted'; return {'status':'ok','message':'deleted','user':u,'audit_log':[x.copy() for x in audit_log]}
