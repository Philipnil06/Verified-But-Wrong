# Product ticket: expiry handling

## Background
Inventory items should be marked for handling based on expiry dates.

## Happy path
- Items expiring today should be handled.
- Items expiring tomorrow should not be handled by default.

## Policy note
Some categories have lead-time rules.

## Acceptance criteria
- Expiring today returns handle_today true.
- Invalid dates return an error.
