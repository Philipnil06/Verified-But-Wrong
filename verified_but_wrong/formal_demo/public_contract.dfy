datatype Role = Admin | NoRole

class Session {
  var active: bool
  var privileged: bool
}

class User {
  var role: Role
}

method UpdateRolePublic(u: User, newRole: Role)
  modifies u
  ensures u.role == newRole
{
  u.role := newRole;
}
