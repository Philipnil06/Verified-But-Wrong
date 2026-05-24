def delete_user(actor, user, audit_log):
    if not user: return {'status':'error','message':'invalid','user':user,'audit_log':audit_log}
    u=user.copy(); u['status']='deleted'; log=[x.copy() for x in audit_log]; log.append({'event':'user_deleted'}); return {'status':'ok','message':'deleted','user':u,'audit_log':log}
