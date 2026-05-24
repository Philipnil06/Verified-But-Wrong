include "intended_contract.dfy"

method UpdateRoleRepaired(u: User, s: Session, newRole: Role)
  modifies u, s
  ensures u.role == newRole
  ensures old(u.role) == Admin && newRole == NoRole && old(s.active) && old(s.privileged) ==> !s.active
{
  var wasAdmin := u.role == Admin;
  var hadPrivilegedSession := s.active && s.privileged;
  u.role := newRole;
  if wasAdmin && newRole == NoRole && hadPrivilegedSession {
    s.active := false;
  }
}

method DemoIntended()
{
  var u := new User;
  var s := new Session;
  u.role := Admin;
  s.active := true;
  s.privileged := true;
  UpdateRoleRepaired(u, s, NoRole);
  assert u.role == NoRole;
  assert !s.active;
}
