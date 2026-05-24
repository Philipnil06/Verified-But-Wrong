def delete_user(actor, user, audit_log):
    if not actor or actor.get('role')!='admin' or not user: return {'status':'error','message':'invalid','user':user,'audit_log':audit_log}
    u=user.copy(); u['status']='deleted'; log=[x.copy() for x in audit_log]; log.append({'event':'user_deleted','user_id':u.get('user_id'),'actor_id':actor.get('user_id')}); return {'status':'ok','message':'deleted','user':u,'audit_log':log}
