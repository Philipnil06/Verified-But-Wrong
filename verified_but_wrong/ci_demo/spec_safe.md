# Refund spec

Refund amounts must be positive and cannot exceed the remaining paid amount. Successful refunds update `refunded_total`.

If the original purchase awarded loyalty points or rewards, the refunded portion must reverse proportional loyalty points without making the customer reward balance negative.
