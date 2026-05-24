predicate ValidInput(t: string) { |t| >= 1 } method solve(t: string) returns (result: string) requires ValidInput(t) ensures |result| == |t|
