datatype Role = Admin | NoRole

class Session {
  var active: bool
  var privileged: bool
}

class User {
  var role: Role
}

method UpdateRoleIntended(u: User, s: Session, newRole: Role)
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
