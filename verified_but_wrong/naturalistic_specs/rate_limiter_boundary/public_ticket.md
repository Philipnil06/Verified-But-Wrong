# Product ticket: request rate limiter

## Background
The API should track recent requests and block excessive traffic.

## Happy path
- First normal requests are allowed.
- Request state is updated when a request is allowed.

## Policy note
The intended quota is five requests per rolling minute.

## Acceptance criteria
- First request is allowed.
- State stores allowed request timestamps.
