# Product ticket: delete user

## Background
Support administrators need to delete active users that should no longer exist in the system.

## Happy path
- Admin deletes an active target user.
- Target status becomes deleted.

## Edge cases
- Missing targets should fail.
- Deleted targets should not be deleted again.

## Acceptance criteria
- Admin delete succeeds.
- Target state is updated.
