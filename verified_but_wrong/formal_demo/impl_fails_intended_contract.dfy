include "intended_contract.dfy"

method UpdateRoleIncomplete(u: User, s: Session, newRole: Role)
  modifies u, s
  ensures u.role == newRole
  ensures old(u.role) == Admin && newRole == NoRole && old(s.active) && old(s.privileged) ==> !s.active
{
  u.role := newRole;
}
