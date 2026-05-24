# Ticket: tenant-scoped export

Export records matching requested filters, but only records whose tenant_id matches the authenticated actor tenant_id may be returned. User-provided filters must not override tenant scope.

Acceptance criteria:
- Tenant t1 receives only t1 records.
- Cross-tenant records are never included.
