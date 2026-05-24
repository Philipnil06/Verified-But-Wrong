def update_role(user, sessions, new_role):
    if not user or new_role not in {'admin','member','guest'}: return {'status':'error','message':'invalid','user':user,'sessions':sessions}
    old=user.get('role'); u=user.copy(); u['role']=new_role; out=[]
    for s in sessions:
        x=s.copy()
        if old=='admin' and new_role!='admin' and x.get('user_id')==u.get('user_id') and x.get('privileged'):
            x['active']=False
        out.append(x)
    return {'status':'ok','message':'updated','user':u,'sessions':out}
