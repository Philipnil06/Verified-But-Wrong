# Product ticket: payment webhook processing

## Background
The payments provider sends webhook events for payment outcomes. The service updates merchant balances for successful payments.

## Happy path
- Successful payment events increase merchant balance by the event amount.
- Failed payment events do not increase balance.
- The event has merchant, amount, currency, and status fields.

## Acceptance criteria
- Successful payment credits the merchant balance.
- Failed payment does not credit balance.
