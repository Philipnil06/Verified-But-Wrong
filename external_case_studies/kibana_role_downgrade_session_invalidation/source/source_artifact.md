# Source Artifact

- Source type: externally sourced public GitHub issue
- Repository: `elastic/kibana`
- Issue number: `192346`
- Title: `[Serverless RBAC]Custom Role Fails to Override Admin Role for Logged-In User Even After Refresh`
- URL: https://github.com/elastic/kibana/issues/192346
- Labels: `bug`, `triage_needed`, `impact:high`, `Team: SecuritySolution`, `Team:Defend Workflows`, `Project:Serverless`, `RBAC`

## Original Issue Body

**Describe the bug**

- Custom Role Fails to Override Admin Role for Logged-In User Even After Refresh

**Kibana/Elasticsearch Stack version**

```
VERSION: 8.16.0 Serverless
BUILD: 78101
COMMIT: f51481d4d697ae23260d2b46ceae7545d3571e95
```

**Preconditions**

- There must be Users added in the serverless project with the admin user.
- Custom role should be present with the None role in the serverless project
- Invite the new user with the Admin role.
- Open side by side two Browsers to test the Role changes, Second browser should be open in Incognito

**Steps:**

- Now Change the role of the User to the None from admin
- Now Navigate to the Users Tab and Refresh for the Role change
- Now observe User still have the Admin access.
- To test this Try to add the Blocklist,
- Observe Blocklist is added successfully

**Actual Result**

- Custom Role Fails to Override Admin Role for Logged-In User Even After Refresh

**Expected Result**

- Custom Role should Override Admin Role for Logged-In User After Refresh

## Use In This Project

This project uses the public issue as an externally sourced software-requirements artifact. We adapt the requirement pattern into a minimal deterministic vericoding-style case study about stale privileged access after a role downgrade.

The adapted case separates:

- an incomplete public implementation spec about updating and viewing user roles,
- a deployable policy card requiring session invalidation or server-side permission revalidation after privilege downgrade,
- a hidden executable oracle used only for evaluation.

## Limitation

We do not claim to reproduce the original Kibana bug. We adapt the issue into a minimal vericoding-style case study about stale privileged access after role downgrade.
