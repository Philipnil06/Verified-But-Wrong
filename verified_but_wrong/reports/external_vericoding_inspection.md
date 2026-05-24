# External Vericoding Inspection

This report checks whether the public Dafny JSONL is viable for target-validity auditing. It does not validate gaps or estimate prevalence.

## Dataset

```json
{
  "status": "available",
  "repo_name": "vericoding-benchmark",
  "repo_url": "https://github.com/Beneficial-AI-Foundation/vericoding-benchmark",
  "local_path": "C:\\Users\\Philip Nilsson\\OneDrive - Mälardalens Tekniska Gymnasium\\Skrivbordet\\Hackathon apartresearch The Secure Program Synthesis\\verified_but_wrong\\external_data\\vericoding-benchmark",
  "jsonl_path": "C:\\Users\\Philip Nilsson\\OneDrive - Mälardalens Tekniska Gymnasium\\Skrivbordet\\Hackathon apartresearch The Secure Program Synthesis\\verified_but_wrong\\external_data\\vericoding-benchmark\\jsonl\\dafny_tasks.jsonl",
  "commit_hash": "349ee510deeb6e15e1eb0d98174914e7093252fd",
  "fetch_method": "local"
}
```

## Counts

- Total records: **2334**
- Total with non-empty description: **1777**
- Total with useful description: **1448**
- APPS records: **677**
- APPS useful descriptions: **676**
- HumanEval records: **162**
- HumanEval useful descriptions: **157**

### By source

| Source | Records | Non-empty descriptions | Useful descriptions |
| --- | --- | --- | --- |
| apps | 677 | 677 | 676 |
| bignum | 62 | 62 | 6 |
| dafnybench | 443 | 196 | 86 |
| humaneval | 162 | 162 | 157 |
| other | 990 | 680 | 523 |


## Fields observed

| Field | Frequency |
| --- | --- |
| id | 2334 |
| language | 2334 |
| qa-definitions-with-sorry | 2334 |
| qa-execs-with-bodies | 2334 |
| qa-execs-with-ghost-types | 2334 |
| qa-functions-with-default-values | 2334 |
| qa-issue | 2334 |
| qa-issue-type | 2334 |
| qa-methods-with-bodies | 2334 |
| qa-near-duplicate-group | 2334 |
| qa-score | 2334 |
| qa-specs-with-default-values | 2334 |
| source | 2334 |
| source-id | 2334 |
| source-notes | 2334 |
| vc-code | 2334 |
| vc-description | 2334 |
| vc-helpers | 2334 |
| vc-postamble | 2334 |
| vc-preamble | 2334 |
| vc-spec | 2334 |


## Missing canonical fields

| Canonical field | Missing count |
| --- | --- |
| description | 557 |
| spec | 9 |


## Recommended subset for audit

Use APPS tasks with useful descriptions and qa-score >= 0.8 when qa-score is available. Count: **640**.

## Sample apps records

### DA0000 (apps)

Source id: `apps_test_1`

NL excerpt:
```text
Given a positive integer x, find the positive integer not exceeding x that has the maximum sum of digits. If multiple such integers exist, return the largest one.
```
Spec excerpt:
```dafny
function intToDigits(x: int): seq<int> requires x >= 0 { if x == 0 then [0] else intToDigitsHelper(x) } function intToDigitsHelper(x: int): seq<int> requires x > 0 decreases x { if x < 10 then [x] else intToDigitsHelper(x / 10) + [x % 10] } function digitSum(digits: seq<int>): int { if |digits| == 0 then 0 else digits[0] + digitSum(digits[1..]) } predicate ValidInput(x: int) { x >= 1 } predicate ValidResult(x: int, result: int) requires ValidInput(x) { result > 0 && result <= x && (forall y :: 1 <= y <= x ==> digitSum(intToDigits(y)) <= digitSum(intToDigits(result))) && (forall y :: 1 <= y <= x && digitSum(intToDigits(y)) == digitSum(intToDigits(result)) ==> y <= result) } method solve(x:...
```

### DA0001 (apps)

Source id: `apps_test_5`

NL excerpt:
```text
Given n browser tabs indexed 1 to n with cursor at position pos, find minimum time to close all tabs except those in range [l, r]. Operations: move cursor (1 sec), close all tabs to left of cursor (1 sec), close all tabs to right of cursor (1 sec).
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, pos: int, l: int, r: int) { 1 <= n <= 100 && 1 <= pos <= n && 1 <= l <= r <= n } predicate NoTabsToClose(l: int, r: int, n: int) { l == 1 && r == n } predicate OnlyCloseRight(l: int, r: int, n: int) { l == 1 && r < n } predicate OnlyCloseLeft(l: int, r: int, n: int) { l > 1 && r == n } predicate CloseBothSides(l: int, r: int, n: int) { l > 1 && r < n } method solve(n: int, pos: int, l: int, r: int) returns (result: int) requires ValidInput(n, pos, l, r) ensures result >= 0 ensures NoTabsToClose(l, r, n) ==> result == 0 ensures OnlyCloseRight(l, r, n) ==> result == abs(pos - r) + 1 ensures OnlyCloseLeft(l, r, n) ==> result == abs(pos - l) + 1 ensures CloseBothS...
```

### DA0002 (apps)

Source id: `apps_test_10`

NL excerpt:
```text
Given a Martian year with n days and Earth-like weeks (5 work days + 2 days off), determine the minimum and maximum possible number of days off in that year.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int) { n >= 1 } function MinDaysOff(n: int): int requires ValidInput(n) { var completeWeeks := n / 7; var remainingDays := n % 7; var minAdditional := if remainingDays > 5 then remainingDays - 5 else 0; 2 * completeWeeks + minAdditional } function MaxDaysOff(n: int): int requires ValidInput(n) { var completeWeeks := n / 7; var remainingDays := n % 7; var maxAdditional := if remainingDays < 2 then remainingDays else 2; 2 * completeWeeks + maxAdditional } predicate ValidOutput(result: seq<int>, n: int) requires ValidInput(n) { |result| == 2 && result[0] >= 0 && result[1] >= 0 && result[0] <= result[1] && result[0] <= n && result[1] <= n && result[0] == MinDaysOff(n)...
```

### DA0003 (apps)

Source id: `apps_test_11`

NL excerpt:
```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```

### DA0004 (apps)

Source id: `apps_test_22`

NL excerpt:
```text
Check if a string is an "s-palindrome" - meaning it is symmetric when mirrored horizontally about its center. Some letters are symmetric: A, H, I, M, O, o, T, U, V, v, W, w, X, x, Y Some letters are mirror pairs: (p,q) and (b,d) All other letters cannot form valid s-palindromes
```
Spec excerpt:
```dafny
predicate is_s_palindrome(s: string) { var pal := "AHIMOoTUVvWwXxY"; forall i :: 0 <= i < |s| ==> var j := |s| - 1 - i; if i >= j then true else if s[i] == s[j] then s[i] in pal else (s[i] == 'p' && s[j] == 'q') || (s[i] == 'q' && s[j] == 'p') || (s[i] == 'b' && s[j] == 'd') || (s[i] == 'd' && s[j] == 'b') } method solve(s: string) returns (result: string) requires |s| >= 1 ensures result == "TAK" || result == "NIE" ensures result == "TAK" <==> is_s_palindrome(s)
```

### DA0005 (apps)

Source id: `apps_test_27`

NL excerpt:
```text
Given a string s of n lowercase Latin letters, find the minimum number of operations to construct it starting from an empty string. Operations are: (1) add one character to the end (unlimited use), (2) copy current string and append it to itself (at most once).
```
Spec excerpt:
```dafny
predicate ValidInput(n: nat, s: string) { |s| == n } function MaxCopySavings(s: string, n: nat): nat requires |s| == n ensures MaxCopySavings(s, n) <= n / 2 { MaxCopySavingsUpTo(s, n, n / 2) } function MaxCopySavingsUpTo(s: string, n: nat, limit: nat): nat requires |s| == n requires limit <= n / 2 ensures MaxCopySavingsUpTo(s, n, limit) <= limit decreases limit { if limit == 0 then 0 else var i := limit - 1; var current := if CanCopyAt(s, n, i) then i else 0; var prev := MaxCopySavingsUpTo(s, n, i); if current > prev then current else prev } predicate CanCopyAt(s: string, n: nat, i: nat) requires |s| == n requires i < n / 2 { var prefix_len := i + 1; var end_pos := i + 1 + prefix_len; end...
```

### DA0006 (apps)

Source id: `apps_test_29`

NL excerpt:
```text
Given a 6-digit ticket (string of digits 0-9), find the minimum number of digit replacements needed to make it "lucky". A ticket is lucky when the sum of its first three digits equals the sum of its last three digits. Any digit can be replaced with any digit 0-9.
```
Spec excerpt:
```dafny
function charToInt(c: char): int requires '0' <= c <= '9' { c as int - '0' as int } function isLucky(digits: seq<int>): bool requires |digits| == 6 requires forall i :: 0 <= i < |digits| ==> 0 <= digits[i] <= 9 { var sum1 := digits[0] + digits[1] + digits[2]; var sum2 := digits[3] + digits[4] + digits[5]; sum1 == sum2 } predicate ValidTicket(ticket: string) { |ticket| == 6 && forall i :: 0 <= i < |ticket| ==> '0' <= ticket[i] <= '9' } predicate canMakeLuckyWith0Changes(digits: seq<int>) requires |digits| == 6 requires forall i :: 0 <= i < |digits| ==> 0 <= digits[i] <= 9 { isLucky(digits) } predicate canMakeLuckyWith1Change(digits: seq<int>) requires |digits| == 6 requires forall i :: 0 <...
```

### DA0007 (apps)

Source id: `apps_test_45`

NL excerpt:
```text
Given positive integers n and k, find a strictly increasing sequence of k positive integers that sum to n and have the maximum possible greatest common divisor (GCD). If no such sequence exists, return -1.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, k: int) { n > 0 && k > 0 } predicate IsStrictlyIncreasing(s: seq<int>) { forall i :: 0 <= i < |s| - 1 ==> s[i] < s[i+1] } predicate AllPositive(s: seq<int>) { forall i :: 0 <= i < |s| ==> s[i] > 0 } function sum(s: seq<int>): int decreases |s| { if |s| == 0 then 0 else s[0] + sum(s[1..]) } predicate ValidSequence(s: seq<int>, n: int, k: int) { |s| == k && AllPositive(s) && IsStrictlyIncreasing(s) && sum(s) == n } predicate IsPossible(n: int, k: int) { k * (k + 1) / 2 <= n } method solve(n: int, k: int) returns (result: seq<int>) requires ValidInput(n, k) ensures (|result| == 1 && result[0] == -1) || (ValidSequence(result, n, k)) ensures (|result| == 1 && resul...
```

### DA0008 (apps)

Source id: `apps_test_48`

NL excerpt:
```text
Given an n × m multiplication table where element at row i and column j equals i·j (1-indexed), find the k-th smallest number among all n·m elements in the table.
```
Spec excerpt:
```dafny
function countLessValue(n: int, m: int, target: int): int requires n >= 0 && m >= 1 && target >= 1 ensures countLessValue(n, m, target) >= 0 ensures countLessValue(n, m, target) <= n * m { if n == 0 then 0 else var maxJ := (target - 1) / n; var actualMaxJ := if maxJ > m then m else maxJ; var contribution := if actualMaxJ >= 1 then actualMaxJ else 0; contribution + countLessValue(n - 1, m, target) } function countLessOrEqualValue(n: int, m: int, target: int): int requires n >= 1 && m >= 1 && target >= 0 ensures countLessOrEqualValue(n, m, target) >= 0 ensures countLessOrEqualValue(n, m, target) <= n * m { if target <= 0 then 0 else if target >= n * m then n * m else countLessValue(n, m, ta...
```

### DA0009 (apps)

Source id: `apps_test_50`

NL excerpt:
```text
You start with r bourles and no shares. There are n buying opportunities and m selling opportunities for shares. Find the maximum bourles you can have after trading. You can buy any number of shares at any buying price and sell any number of shares (up to what you own) at any selling price.
```
Spec excerpt:
```dafny
predicate ValidInput(input: string) { |input| > 0 && '\n' in input && var lines := SplitLinesFunc(input); |lines| >= 3 && ValidIntLine(lines[0], 3) && ValidIntLine(lines[1]) && ValidIntLine(lines[2]) && var firstLine := SplitIntsFunc(lines[0]); var S := SplitIntsFunc(lines[1]); var B := SplitIntsFunc(lines[2]); |firstLine| == 3 && firstLine[0] >= 1 && firstLine[1] >= 1 && firstLine[2] >= 1 && |S| == firstLine[0] && |B| == firstLine[1] } function ParseInput(input: string): (int, int, int, seq<int>, seq<int>) requires ValidInput(input) ensures var result := ParseInput(input); result.0 >= 1 && result.1 >= 1 && result.2 >= 1 && |result.3| == result.0 && |result.4| == result.1 && (forall i ::...
```

## Sample humaneval records

### DH0000 (humaneval)

Source id: `humaneval_000`

NL excerpt:
```text
This verification task involves implementing a method to determine if any two numbers in a given list have an absolute difference less than a specified threshold. The implementation uses nested loops to compare all pairs of elements and returns true as soon as a close pair is found, or false if no such pair exists.
```
Spec excerpt:
```dafny
predicate ValidInput(numbers: seq<real>, threshold: real) { true } function AbsDiff(a: real, b: real): real { if a >= b then a - b else b - a } predicate HasCloseElements(numbers: seq<real>, threshold: real) { exists i, j :: 0 <= i < j < |numbers| && AbsDiff(numbers[i], numbers[j]) < threshold } method has_close_elements(numbers: seq<real>, threshold: real) returns (result: bool) requires ValidInput(numbers, threshold) ensures result == HasCloseElements(numbers, threshold)
```

### DH0001 (humaneval)

Source id: `humaneval_001_separate-paren-groups`

NL excerpt:
```text
function_signature: def separate_paren_groups(paren_string: str) -> List[str] Input to this function is a string containing multiple groups of nested parentheses. Your goal is to separate those group into separate strings and return the list of those. Separate groups are balanced (each open brace is properly closed) and not nested within each other Ignore any spaces in the input string.
```
Spec excerpt:
```dafny
function ParenthesesDepth(s: string, i: int, j: int): int decreases j - i requires 0 <= i <= j <= |s| { if i == j then 0 else if s[i] == '(' then ParenthesesDepth(s, i+1, j) + 1 else if s[i] == ')' then ParenthesesDepth(s, i+1, j) - 1 else ParenthesesDepth(s, i+1, j) } function InnerDepthsPositive(s: string) : bool { forall i :: 0 < i < |s| ==> ParenthesesDepth(s, 0, i) > 0 } function InnerDepthsNonnegative(s: string) : bool { forall i :: 0 < i < |s| ==> ParenthesesDepth(s, 0, i) >= 0 } method separate_paren_groups(paren_string: string) returns (res : seq<string>) requires ParenthesesDepth(paren_string, 0, |paren_string|) == 0 requires InnerDepthsNonnegative(paren_string) ensures forall k...
```

### DH0002 (humaneval)

Source id: `humaneval_002`

NL excerpt:
```text
This task implements a function to extract the decimal (fractional) part of a positive floating point number. Given a number like 3.5, it should return 0.5, and for 1.25, it should return 0.25. The implementation involves subtracting the floor (integer part) from the original number.
```
Spec excerpt:
```dafny
predicate ValidInput(number: real) { number >= 0.0 } predicate ValidOutput(result: real, input: real) { 0.0 <= result < 1.0 && result == input - Floor(input) } function Floor(x: real): real ensures Floor(x) <= x < Floor(x) + 1.0 { if x >= 0.0 then FloorNonnegative(x) else -CeilNonnegative(-x) } function FloorNonnegative(x: real): real requires x >= 0.0 ensures FloorNonnegative(x) <= x < FloorNonnegative(x) + 1.0 ensures FloorNonnegative(x) >= 0.0 { FloorHelper(x, 0) } function FloorHelper(x: real, n: int): real requires x >= 0.0 requires n >= 0 ensures FloorHelper(x, n) <= x + n as real < FloorHelper(x, n) + 1.0 ensures FloorHelper(x, n) >= n as real decreases x { if x < 1.0 then n as rea...
```

### DH0003 (humaneval)

Source id: `humaneval_003`

NL excerpt:
```text
Given a list of integers representing bank account operations (positive for deposits, negative for withdrawals), determine if the account balance ever drops below zero. The account starts with a balance of zero.
```
Spec excerpt:
```dafny
function sum_prefix(ops: seq<int>, len: nat): int requires len <= |ops| { if len == 0 then 0 else sum_prefix(ops, len-1) + ops[len-1] } method below_zero(operations: seq<int>) returns (result: bool) ensures result <==> (exists i :: 0 < i <= |operations| && sum_prefix(operations, i) < 0)
```

### DH0004 (humaneval)

Source id: `humaneval_004`

NL excerpt:
```text
This task implements the calculation of Mean Absolute Deviation (MAD) for a sequence of floating-point numbers. The MAD is defined as the average of the absolute deviations from the arithmetic mean of the data set. The implementation should calculate the arithmetic mean, compute absolute deviations from this mean for each element, and then return the average of these absolute deviations while ensuring the result is non-negative.
```
Spec excerpt:
```dafny
function sum(numbers: seq<real>): real { if |numbers| == 0 then 0.0 else numbers[0] + sum(numbers[1..]) } function abs(x: real): real { if x >= 0.0 then x else -x } predicate ValidInput(numbers: seq<real>) { |numbers| > 0 } function ArithmeticMean(numbers: seq<real>): real requires ValidInput(numbers) { sum(numbers) / (|numbers| as real) } function AbsoluteDeviations(numbers: seq<real>): seq<real> requires ValidInput(numbers) { seq(|numbers|, i requires 0 <= i < |numbers| => abs(numbers[i] - ArithmeticMean(numbers))) } function MAD(numbers: seq<real>): real requires ValidInput(numbers) { sum(AbsoluteDeviations(numbers)) / (|numbers| as real) } lemma sum_non_negative(numbers: seq<real>) re...
```

### DH0005 (humaneval)

Source id: `humaneval_005`

NL excerpt:
```text
This verification task involves implementing a method that inserts a delimiter between every two consecutive elements in a sequence of integers. The method should handle edge cases like empty sequences or single-element sequences, and for longer sequences, it should produce a result with alternating original elements and delimiters.
```
Spec excerpt:
```dafny
predicate ValidInput(numbers: seq<int>, delimiter: int) { true // Any sequence and delimiter are valid inputs } predicate ValidOutput(numbers: seq<int>, delimiter: int, result: seq<int>) { if |numbers| <= 1 then result == numbers else |result| == 2 * |numbers| - 1 && (forall i :: 0 <= i < |numbers| ==> result[2 * i] == numbers[i]) && (forall i :: 0 <= i < |numbers| - 1 ==> result[2 * i + 1] == delimiter) } method InsertDelimiter(numbers: seq<int>, delimiter: int) returns (result: seq<int>) requires ValidInput(numbers, delimiter) ensures ValidOutput(numbers, delimiter, result)
```

### DH0006 (humaneval)

Source id: `humaneval_006`

NL excerpt:
```text
This verification task implements a parser for nested parentheses strings. Given a string containing groups of nested parentheses separated by spaces, the goal is to find the maximum nesting depth for each group independently. The implementation must correctly split the input by spaces, calculate nesting depths, and return a sequence of maximum depths corresponding to each group.
```
Spec excerpt:
```dafny
function SplitBySpacesResult(s: string): seq<string> requires forall i :: 0 <= i < |s| ==> s[i] == '(' || s[i] == ')' || s[i] == ' ' ensures forall i :: 0 <= i < |SplitBySpacesResult(s)| ==> forall j :: 0 <= j < |SplitBySpacesResult(s)[i]| ==> SplitBySpacesResult(s)[i][j] == '(' || SplitBySpacesResult(s)[i][j] == ')' ensures |s| == 0 ==> |SplitBySpacesResult(s)| == 0 { if |s| == 0 then [] else var groups := []; var current_group := ""; var i := 0; SplitBySpacesHelper(s, i, current_group, groups) } function MaxNestingDepth(group: string): int requires forall i :: 0 <= i < |group| ==> group[i] == '(' || group[i] == ')' ensures MaxNestingDepth(group) >= 0 { MaxNestingDepthHelper(group, 0, 0,...
```

### DH0007 (humaneval)

Source id: `humaneval_007`

NL excerpt:
```text
This task implements a string filtering function that takes a list of strings and a substring, returning a new list containing only the strings that contain the given substring. The filtering should preserve the original order of matching strings and be case-sensitive.
```
Spec excerpt:
```dafny
function contains_substring(s: string, sub: string): bool { if |sub| == 0 then true else if |sub| > |s| then false else exists i {:trigger s[i..i+|sub|]} :: 0 <= i <= |s| - |sub| && s[i..i+|sub|] == sub } function filter_sequence(strings: seq<string>, substring: string): seq<string> { filter_sequence_helper(strings, substring, |strings|) } function filter_sequence_helper(strings: seq<string>, substring: string, n: int): seq<string> requires 0 <= n <= |strings| { if n == 0 then [] else if contains_substring(strings[n-1], substring) then filter_sequence_helper(strings, substring, n-1) + [strings[n-1]] else filter_sequence_helper(strings, substring, n-1) } method filter_by_substring(strings:...
```

### DH0008 (humaneval)

Source id: `humaneval_008`

NL excerpt:
```text
This verification task implements a method to compute both the sum and product of all integers in a given sequence. For an empty list, the method should return (0, 1) representing the empty sum and empty product respectively. The implementation uses iterative computation while maintaining loop invariants to ensure correctness.
```
Spec excerpt:
```dafny
function SumSeq(s: seq<int>): int { if |s| == 0 then 0 else s[0] + SumSeq(s[1..]) } function ProductSeq(s: seq<int>): int { if |s| == 0 then 1 else s[0] * ProductSeq(s[1..]) } lemma SumSeqAppend(s: seq<int>, x: int) ensures SumSeq(s + [x]) == SumSeq(s) + x { if |s| == 0 { assert s + [x] == [x]; assert SumSeq([x]) == x + SumSeq([]); assert SumSeq([]) == 0; } else { assert s == [s[0]] + s[1..]; assert s + [x] == [s[0]] + (s[1..] + [x]); SumSeqAppend(s[1..], x); } } lemma ProductSeqAppend(s: seq<int>, x: int) ensures ProductSeq(s + [x]) == ProductSeq(s) * x { if |s| == 0 { assert s + [x] == [x]; assert ProductSeq([x]) == x * ProductSeq([]); assert ProductSeq([]) == 1; } else { assert s == [s...
```

### DH0009 (humaneval)

Source id: `humaneval_009`

NL excerpt:
```text
This verification task implements a rolling maximum function that takes a list of integers and returns a list where each element represents the maximum value encountered from the beginning of the list up to and including the current position.
```
Spec excerpt:
```dafny
function max_up_to(numbers: seq<int>, index: int): int requires 0 <= index < |numbers| { if index == 0 then numbers[0] else var prev_max := max_up_to(numbers, index - 1); if numbers[index] > prev_max then numbers[index] else prev_max } method rolling_max(numbers: seq<int>) returns (result: seq<int>) ensures |result| == |numbers| ensures |numbers| == 0 ==> |result| == 0 ensures |numbers| > 0 ==> |result| > 0 ensures forall i :: 0 <= i < |result| ==> result[i] == max_up_to(numbers, i) ensures forall i :: 0 <= i < |result| ==> forall j :: 0 <= j <= i ==> numbers[j] <= result[i] ensures forall i :: 0 <= i < |result| ==> exists j :: 0 <= j <= i && numbers[j] == result[i]
```

## Sample weakest_spec_looking records

### DA0003 (apps)

Source id: `apps_test_11`

NL excerpt:
```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```

### DA0010 (apps)

Source id: `apps_test_56`

NL excerpt:
```text
Simulate pouring champagne into a pyramid of glasses for t seconds. The pyramid has n levels where level i has i glasses (1-indexed). Each second, 1 unit is poured into the top glass. Each glass has capacity 1. When a glass overflows, excess champagne splits equally to the two glasses below. Count the number of completely full glasses after t seconds.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, t: int) { 1 <= n <= 10 && 0 <= t <= 10000 } function TotalGlasses(n: int): int { n * (n + 1) / 2 } predicate ValidResult(result: int, n: int, t: int) { result >= 0 && result <= TotalGlasses(n) } predicate CorrectForEdgeCases(result: int, n: int, t: int) { (t == 0 ==> result == 0) && (n == 1 && t >= 1 ==> result == 1) && (n == 1 && t == 0 ==> result == 0) && (t >= 1 && n > 1 ==> result >= 1) } method solve(n: int, t: int) returns (result: int) requires ValidInput(n, t) ensures ValidResult(result, n, t) ensures CorrectForEdgeCases(result, n, t)
```

### DA0045 (apps)

Source id: `apps_test_181`

NL excerpt:
```text
Given a camera rotation angle in degrees, determine the minimum number of 90-degree clockwise rotations needed to minimize the image's deviation from vertical orientation. When a camera rotates by x degrees, the image appears rotated by -x degrees.
```
Spec excerpt:
```dafny
function NormalizeAngle(angle: int): int { var n := angle % 360; if n < 0 then n + 360 else n } function DeviationFromVertical(angle: int): int requires 0 <= angle < 360 { if angle <= 180 then angle else 360 - angle } function ImageAngleAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { NormalizeAngle(-cameraAngle + 90 * rotations) } function ImageDeviationAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { DeviationFromVertical(ImageAngleAfterRotations(cameraAngle, rotations)) } predicate IsOptimalRotations(cameraAngle: int, result: int) requires 0 <= result <= 3 { forall k :: 0 <= k <= 3 ==> var result_deviation := Image...
```

### DA0082 (apps)

Source id: `apps_test_448`

NL excerpt:
```text
Given n children numbered 1 to n, where child i needs at least a_i candies. Children initially line up in order 1, 2, ..., n. Distribution algorithm: 1. Give m candies to the first child in line 2. If the child has received enough candies (≥ a_i), they go home 3. Otherwise, the child goes to the end of the line 4. Repeat until all children go home Find which child goes home last.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, m: int, a: seq<int>) { n > 0 && m > 0 && |a| == n && forall i :: 0 <= i < |a| ==> a[i] > 0 } predicate ValidResult(result: int, n: int) { 1 <= result <= n } function SumCandiesStillNeeded(queue: seq<seq<int>>): nat requires forall child :: child in queue ==> |child| == 3 && child[0] >= 0 && child[1] > 0 { if |queue| == 0 then 0 else var child := queue[0]; var stillNeeded := if child[1] <= child[0] then 0 else child[1] - child[0]; stillNeeded + SumCandiesStillNeeded(queue[1..]) } method solve(n: int, m: int, a: seq<int>) returns (result: int) requires ValidInput(n, m, a) ensures ValidResult(result, n)
```

### DA0136 (apps)

Source id: `apps_test_682`

NL excerpt:
```text
Given starting position (r1, c1) and ending position (r2, c2) on an 8×8 chessboard, find the minimum number of moves required for a rook, bishop, and king to move from the starting position to the ending position. Return 0 if a piece cannot reach the destination.
```
Spec excerpt:
```dafny
predicate ValidPosition(r: int, c: int) { 1 <= r <= 8 && 1 <= c <= 8 } function RookMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else if r1 == r2 || c1 == c2 then 1 else 2 } function BishopMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff == col_diff then 1 else if (r1 + c1) % 2 == (r2 + c2) % 2 then 2 else 0 } function KingMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPositi...
```

### DA0152 (apps)

Source id: `apps_test_755`

NL excerpt:
```text
Find the minimum number of steps to move from position 0 to position x on a number line, where each step can move forward by 1, 2, 3, 4, or 5 positions.
```
Spec excerpt:
```dafny
predicate ValidInput(x: int) { x >= 1 } predicate IsMinimalSteps(x: int, steps: int) requires x >= 1 { steps >= 1 && steps * 5 >= x && (steps - 1) * 5 < x }
```

### DA0157 (apps)

Source id: `apps_test_785`

NL excerpt:
```text
Given a rectangular room with dimensions a × b meters, accommodate exactly n students such that each student has at least 6 square meters of space. You can increase either or both dimensions by any positive integer amount. Find the minimum possible area and corresponding dimensions.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int) { n > 0 && a > 0 && b > 0 } predicate ValidOutput(result: seq<int>, n: int, a: int, b: int) { |result| == 3 && result[0] >= 6 * n && result[1] > 0 && result[2] > 0 && result[0] == result[1] * result[2] && ((result[1] >= a && result[2] >= b) || (result[1] >= b && result[2] >= a)) } method solve(n: int, a: int, b: int) returns (result: seq<int>) requires ValidInput(n, a, b) ensures ValidOutput(result, n, a, b)
```

### DA0199 (apps)

Source id: `apps_test_985`

NL excerpt:
```text
Given n bishops on a 1000×1000 grid, count the number of pairs that attack each other. Two bishops attack each other if and only if they are on the same diagonal (either main diagonal or anti-diagonal). Main diagonal: x - y is constant, Anti-diagonal: x + y is constant.
```
Spec excerpt:
```dafny
predicate ValidInput(positions: seq<(int, int)>) { |positions| >= 1 && |positions| <= 200000 && (forall i :: 0 <= i < |positions| ==> 1 <= positions[i].0 <= 1000 && 1 <= positions[i].1 <= 1000) && (forall i, j :: 0 <= i < j < |positions| ==> positions[i] != positions[j]) } function CountAttackingPairs(positions: seq<(int, int)>): int requires ValidInput(positions) { |set i, j | 0 <= i < j < |positions| && (positions[i].0 + positions[i].1 == positions[j].0 + positions[j].1 || positions[i].0 - positions[i].1 == positions[j].0 - positions[j].1) :: (i, j)| } predicate ValidOutput(positions: seq<(int, int)>, result: int) requires ValidInput(positions) { result == CountAttackingPairs(positions)...
```

### DA0208 (apps)

Source id: `apps_test_1009`

NL excerpt:
```text
Given n cowbells with integer sizes s₁ ≤ s₂ ≤ ... ≤ sₙ and k boxes, find the minimum box size s such that all cowbells can be packed into the k boxes, where each box can hold at most 2 cowbells, the sum of cowbell sizes in each box cannot exceed the box size s, and all boxes have the same size s.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, k: int, L: seq<int>) { n >= 1 && k >= 1 && n <= 2*k && |L| == n && (forall i :: 0 <= i < |L|-1 ==> L[i] <= L[i+1]) && (forall i :: 0 <= i < |L| ==> L[i] >= 0) } predicate ValidBoxConfiguration(boxes: seq<int>, boxSize: int) { |boxes| >= 1 && (forall i :: 0 <= i < |boxes| ==> boxes[i] <= boxSize) && (forall i :: 0 <= i < |boxes| ==> boxes[i] >= 0) } function sum(s: seq<int>): int { if |s| == 0 then 0 else s[0] + sum(s[1..]) } function max(s: seq<int>): int requires |s| > 0 { if |s| == 1 then s[0] else if s[0] >= max(s[1..]) then s[0] else max(s[1..]) } method solve(n: int, k: int, L: seq<int>) returns (result: int) requires ValidInput(n, k, L) ensures result >= 0
```

### DA0244 (apps)

Source id: `apps_test_1134`

NL excerpt:
```text
Given n consecutive days of river observations where on day i there are m_i marks strictly above the current water level, find the minimum possible sum of d_i over all n days, where d_i is the number of marks strictly below the water level on day i. Each day a mark is made at the current water level, marks never wash away, and the total number of marks can only stay the same or increase each day.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, m: seq<int>) { n > 0 && |m| == n && forall i :: 0 <= i < n ==> 0 <= m[i] < i + 1 } predicate ValidSolution(n: int, m: seq<int>, dm: seq<int>) { |dm| == n && |m| == n && (forall i :: 0 <= i < n ==> dm[i] >= m[i] + 1) && (forall i :: 0 <= i < n - 1 ==> dm[i] <= dm[i + 1]) } function SumBelow(m: seq<int>, dm: seq<int>): int requires |m| == |dm| { if |m| == 0 then 0 else (dm[0] - 1 - m[0]) + SumBelow(m[1..], dm[1..]) } method solve(n: int, m: seq<int>) returns (result: int) requires ValidInput(n, m) ensures result >= 0
```
