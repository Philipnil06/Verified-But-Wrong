include "public_contract.dfy"

method UpdateRoleIncomplete(u: User, s: Session, newRole: Role)
  modifies u
  ensures u.role == newRole
  ensures s.active == old(s.active)
{
  u.role := newRole;
}

method DemoPublic()
{
  var u := new User;
  var s := new Session;
  u.role := Admin;
  s.active := true;
  s.privileged := true;
  UpdateRoleIncomplete(u, s, NoRole);
  assert u.role == NoRole;
  assert s.active;
}
