def update_role(user, sessions, new_role):
    if not user or new_role not in {'admin','member','guest'}: return {'status':'error','message':'invalid','user':user,'sessions':sessions}
    u=user.copy(); u['role']=new_role; return {'status':'ok','message':'updated','user':u,'sessions':[s.copy() for s in sessions]}
