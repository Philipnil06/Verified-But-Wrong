# External Vericoding Gap Candidates

All entries are candidate-only and require manual validation.

- Records total: **2334**
- Records audited by scanner: **797**
- Candidate gaps found: **128**

## Counts by confidence

| Confidence | Count |
| --- | --- |
| high | 41 |
| low | 72 |
| medium | 15 |


## Counts by category

| Category | Count |
| --- | --- |
| conservation_or_permutation_missing | 1 |
| exact_value_missing | 42 |
| optimization_missing | 17 |
| output_format_missing | 14 |
| tie_break_missing | 22 |
| trivial_postcondition | 32 |


## Top 50 candidates

| Case | Source | Source ID | Category | Confidence | Validation difficulty |
| --- | --- | --- | --- | --- | --- |
| DA0136 | apps | apps_test_682 | trivial_postcondition | high | easy |
| DA0152 | apps | apps_test_755 | trivial_postcondition | high | easy |
| DA0157 | apps | apps_test_785 | trivial_postcondition | high | easy |
| DA0306 | apps | apps_test_1576 | trivial_postcondition | high | easy |
| DA0515 | apps | apps_test_4267 | trivial_postcondition | high | easy |
| DA0673 | apps | apps_test_4718 | trivial_postcondition | high | easy |
| DA0003 | apps | apps_test_11 | trivial_postcondition | high | easy |
| DA0010 | apps | apps_test_56 | trivial_postcondition | high | easy |
| DA0045 | apps | apps_test_181 | trivial_postcondition | high | easy |
| DA0082 | apps | apps_test_448 | trivial_postcondition | high | easy |
| DA0199 | apps | apps_test_985 | trivial_postcondition | high | easy |
| DA0208 | apps | apps_test_1009 | trivial_postcondition | high | easy |
| DA0244 | apps | apps_test_1134 | trivial_postcondition | high | easy |
| DA0258 | apps | apps_test_1212 | trivial_postcondition | high | easy |
| DA0265 | apps | apps_test_1240 | trivial_postcondition | high | easy |
| DA0281 | apps | apps_test_1346 | trivial_postcondition | high | easy |
| DA0293 | apps | apps_test_1430 | trivial_postcondition | high | easy |
| DA0315 | apps | apps_test_1618 | trivial_postcondition | high | easy |
| DA0359 | apps | apps_test_1849 | trivial_postcondition | high | easy |
| DA0363 | apps | apps_test_1886 | trivial_postcondition | high | easy |
| DA0406 | apps | apps_test_2238 | trivial_postcondition | high | easy |
| DA0409 | apps | apps_test_2256 | trivial_postcondition | high | easy |
| DA0417 | apps | apps_test_2340 | trivial_postcondition | high | easy |
| DA0438 | apps | apps_test_2456 | trivial_postcondition | high | easy |
| DA0445 | apps | apps_test_2516 | trivial_postcondition | high | easy |
| DA0454 | apps | apps_test_2594 | trivial_postcondition | high | easy |
| DA0525 | apps | apps_test_4298 | trivial_postcondition | high | easy |
| DA0538 | apps | apps_test_4326 | trivial_postcondition | high | easy |
| DA0650 | apps | apps_test_4635 | trivial_postcondition | high | easy |
| DH0057 | humaneval | humaneval_054 | trivial_postcondition | high | easy |
| DH0136 | humaneval | humaneval_134 | trivial_postcondition | high | easy |
| DA0136 | apps | apps_test_682 | exact_value_missing | high | easy |
| DA0136 | apps | apps_test_682 | optimization_missing | high | easy |
| DA0152 | apps | apps_test_755 | exact_value_missing | high | easy |
| DA0157 | apps | apps_test_785 | exact_value_missing | high | easy |
| DA0157 | apps | apps_test_785 | optimization_missing | high | easy |
| DA0306 | apps | apps_test_1576 | output_format_missing | high | easy |
| DA0306 | apps | apps_test_1576 | tie_break_missing | high | easy |
| DA0515 | apps | apps_test_4267 | exact_value_missing | high | easy |
| DA0673 | apps | apps_test_4718 | output_format_missing | high | easy |
| DH0160 | humaneval | humaneval_159 | trivial_postcondition | high | easy |
| DA0003 | apps | apps_test_11 | exact_value_missing | medium | easy |
| DA0003 | apps | apps_test_11 | optimization_missing | medium | easy |
| DA0417 | apps | apps_test_2340 | optimization_missing | medium | easy |
| DA0438 | apps | apps_test_2456 | exact_value_missing | medium | easy |
| DA0525 | apps | apps_test_4298 | exact_value_missing | medium | easy |
| DA0525 | apps | apps_test_4298 | optimization_missing | medium | easy |
| DH0136 | humaneval | humaneval_134 | tie_break_missing | medium | easy |
| DA0014 | apps | apps_test_66 | exact_value_missing | medium | medium |
| DA0063 | apps | apps_test_244 | exact_value_missing | medium | medium |


### DA0136 - high confidence

Source: `apps` / `apps_test_682`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given starting position (r1, c1) and ending position (r2, c2) on an 8×8 chessboard, find the minimum number of moves required for a rook, bishop, and king to move from the starting position to the ending position. Return 0 if a piece cannot reach the destination.
```
Spec excerpt:
```dafny
predicate ValidPosition(r: int, c: int) { 1 <= r <= 8 && 1 <= c <= 8 } function RookMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else if r1 == r2 || c1 == c2 then 1 else 2 } function BishopMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff == col_diff then 1 else if (r1 + c1) % 2 == (r2 + c2) % 2 then 2 else 0 } function KingMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff >= col_diff then row_diff else col_diff } predicate ValidResult(result: seq<int>, r1: int, c1: int, r2: int, c2: int) requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { |result| == 3 && result[0] == RookMoves(r1, c1, r2, c2) && resul...
```


### DA0152 - high confidence

Source: `apps` / `apps_test_755`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Find the minimum number of steps to move from position 0 to position x on a number line, where each step can move forward by 1, 2, 3, 4, or 5 positions.
```
Spec excerpt:
```dafny
predicate ValidInput(x: int) { x >= 1 } predicate IsMinimalSteps(x: int, steps: int) requires x >= 1 { steps >= 1 && steps * 5 >= x && (steps - 1) * 5 < x }
```


### DA0157 - high confidence

Source: `apps` / `apps_test_785`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a rectangular room with dimensions a × b meters, accommodate exactly n students such that each student has at least 6 square meters of space. You can increase either or both dimensions by any positive integer amount. Find the minimum possible area and corresponding dimensions.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int) { n > 0 && a > 0 && b > 0 } predicate ValidOutput(result: seq<int>, n: int, a: int, b: int) { |result| == 3 && result[0] >= 6 * n && result[1] > 0 && result[2] > 0 && result[0] == result[1] * result[2] && ((result[1] >= a && result[2] >= b) || (result[1] >= b && result[2] >= a)) } method solve(n: int, a: int, b: int) returns (result: seq<int>) requires ValidInput(n, a, b) ensures ValidOutput(result, n, a, b)
```


### DA0306 - high confidence

Source: `apps` / `apps_test_1576`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Decrypt a string that was encrypted using the Right-Left cipher. The Right-Left cipher encrypts by starting with the first character, then alternating between appending to the right (even positions) and prepending to the left (odd positions) for subsequent characters.
```
Spec excerpt:
```dafny
predicate ValidInput(t: string) { |t| >= 1 } method solve(t: string) returns (result: string) requires ValidInput(t) ensures |result| == |t|
```


### DA0515 - high confidence

Source: `apps` / `apps_test_4267`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a room temperature in degrees Celsius, determine whether to turn on an air conditioner. The air conditioner should be turned on if and only if the temperature is 30°C or higher.
```
Spec excerpt:
```dafny
predicate ValidTemperature(temp: int) { -40 <= temp <= 40 } function ExpectedOutput(temp: int): string { if temp >= 30 then "Yes\n" else "No\n" } predicate CorrectOutput(temp: int, output: string) { output == ExpectedOutput(temp) } method solve(X: int) returns (result: string) requires ValidTemperature(X) ensures CorrectOutput(X, result)
```


### DA0673 - high confidence

Source: `apps` / `apps_test_4718`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a date string in format "2017/01/dd" where dd represents a day from 01 to 31, replace the year "2017" with "2018" and output the corrected date string.
```
Spec excerpt:
```dafny
predicate ValidInput(dateStr: string) { |dateStr| == 10 && dateStr[0..4] == "2017" } predicate ValidOutput(input: string, output: string) requires |input| >= 4 { output == "2018" + input[4..] && |output| == 10 && output[0..4] == "2018" && output[4..] == input[4..] } method solve(dateStr: string) returns (result: string) requires ValidInput(dateStr) ensures ValidOutput(dateStr, result)
```


### DA0003 - high confidence

Source: `apps` / `apps_test_11`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```


### DA0010 - high confidence

Source: `apps` / `apps_test_56`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Simulate pouring champagne into a pyramid of glasses for t seconds. The pyramid has n levels where level i has i glasses (1-indexed). Each second, 1 unit is poured into the top glass. Each glass has capacity 1. When a glass overflows, excess champagne splits equally to the two glasses below. Count the number of completely full glasses after t seconds.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, t: int) { 1 <= n <= 10 && 0 <= t <= 10000 } function TotalGlasses(n: int): int { n * (n + 1) / 2 } predicate ValidResult(result: int, n: int, t: int) { result >= 0 && result <= TotalGlasses(n) } predicate CorrectForEdgeCases(result: int, n: int, t: int) { (t == 0 ==> result == 0) && (n == 1 && t >= 1 ==> result == 1) && (n == 1 && t == 0 ==> result == 0) && (t >= 1 && n > 1 ==> result >= 1) } method solve(n: int, t: int) returns (result: int) requires ValidInput(n, t) ensures ValidResult(result, n, t) ensures CorrectForEdgeCases(result, n, t)
```


### DA0045 - high confidence

Source: `apps` / `apps_test_181`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given a camera rotation angle in degrees, determine the minimum number of 90-degree clockwise rotations needed to minimize the image's deviation from vertical orientation. When a camera rotates by x degrees, the image appears rotated by -x degrees.
```
Spec excerpt:
```dafny
function NormalizeAngle(angle: int): int { var n := angle % 360; if n < 0 then n + 360 else n } function DeviationFromVertical(angle: int): int requires 0 <= angle < 360 { if angle <= 180 then angle else 360 - angle } function ImageAngleAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { NormalizeAngle(-cameraAngle + 90 * rotations) } function ImageDeviationAfterRotations(cameraAngle: int, rotations: int): int requires 0 <= rotations <= 3 { DeviationFromVertical(ImageAngleAfterRotations(cameraAngle, rotations)) } predicate IsOptimalRotations(cameraAngle: int, result: int) requires 0 <= result <= 3 { forall k :: 0 <= k <= 3 ==> var result_deviation := ImageDeviationAfterRotations(cameraAngle, result); var k_deviation := ImageDeviationAfterRotations(cameraAngle, k); result_deviation < k_deviation || (result_deviation == k_deviation && result <= k) } method solve(x: int) returns (result: int) ensures 0 <= result <= 3 ensures IsOptimalRotations(x, result)
```


### DA0082 - high confidence

Source: `apps` / `apps_test_448`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given n children numbered 1 to n, where child i needs at least a_i candies. Children initially line up in order 1, 2, ..., n. Distribution algorithm: 1. Give m candies to the first child in line 2. If the child has received enough candies (≥ a_i), they go home 3. Otherwise, the child goes to the end of the line 4. Repeat until all children go home Find which child goes home last.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, m: int, a: seq<int>) { n > 0 && m > 0 && |a| == n && forall i :: 0 <= i < |a| ==> a[i] > 0 } predicate ValidResult(result: int, n: int) { 1 <= result <= n } function SumCandiesStillNeeded(queue: seq<seq<int>>): nat requires forall child :: child in queue ==> |child| == 3 && child[0] >= 0 && child[1] > 0 { if |queue| == 0 then 0 else var child := queue[0]; var stillNeeded := if child[1] <= child[0] then 0 else child[1] - child[0]; stillNeeded + SumCandiesStillNeeded(queue[1..]) } method solve(n: int, m: int, a: seq<int>) returns (result: int) requires ValidInput(n, m, a) ensures ValidResult(result, n)
```


### DA0199 - high confidence

Source: `apps` / `apps_test_985`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n bishops on a 1000×1000 grid, count the number of pairs that attack each other. Two bishops attack each other if and only if they are on the same diagonal (either main diagonal or anti-diagonal). Main diagonal: x - y is constant, Anti-diagonal: x + y is constant.
```
Spec excerpt:
```dafny
predicate ValidInput(positions: seq<(int, int)>) { |positions| >= 1 && |positions| <= 200000 && (forall i :: 0 <= i < |positions| ==> 1 <= positions[i].0 <= 1000 && 1 <= positions[i].1 <= 1000) && (forall i, j :: 0 <= i < j < |positions| ==> positions[i] != positions[j]) } function CountAttackingPairs(positions: seq<(int, int)>): int requires ValidInput(positions) { |set i, j | 0 <= i < j < |positions| && (positions[i].0 + positions[i].1 == positions[j].0 + positions[j].1 || positions[i].0 - positions[i].1 == positions[j].0 - positions[j].1) :: (i, j)| } predicate ValidOutput(positions: seq<(int, int)>, result: int) requires ValidInput(positions) { result == CountAttackingPairs(positions) && result >= 0 } method SolveBishops(positions: seq<(int, int)>) returns (result: int) requires ValidInput(positions) ensures ValidOutput(positions, result) ensures result >= 0
```


### DA0208 - high confidence

Source: `apps` / `apps_test_1009`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n cowbells with integer sizes s₁ ≤ s₂ ≤ ... ≤ sₙ and k boxes, find the minimum box size s such that all cowbells can be packed into the k boxes, where each box can hold at most 2 cowbells, the sum of cowbell sizes in each box cannot exceed the box size s, and all boxes have the same size s.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, k: int, L: seq<int>) { n >= 1 && k >= 1 && n <= 2*k && |L| == n && (forall i :: 0 <= i < |L|-1 ==> L[i] <= L[i+1]) && (forall i :: 0 <= i < |L| ==> L[i] >= 0) } predicate ValidBoxConfiguration(boxes: seq<int>, boxSize: int) { |boxes| >= 1 && (forall i :: 0 <= i < |boxes| ==> boxes[i] <= boxSize) && (forall i :: 0 <= i < |boxes| ==> boxes[i] >= 0) } function sum(s: seq<int>): int { if |s| == 0 then 0 else s[0] + sum(s[1..]) } function max(s: seq<int>): int requires |s| > 0 { if |s| == 1 then s[0] else if s[0] >= max(s[1..]) then s[0] else max(s[1..]) } method solve(n: int, k: int, L: seq<int>) returns (result: int) requires ValidInput(n, k, L) ensures result >= 0
```


### DA0244 - high confidence

Source: `apps` / `apps_test_1134`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n consecutive days of river observations where on day i there are m_i marks strictly above the current water level, find the minimum possible sum of d_i over all n days, where d_i is the number of marks strictly below the water level on day i. Each day a mark is made at the current water level, marks never wash away, and the total number of marks can only stay the same or increase each day.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, m: seq<int>) { n > 0 && |m| == n && forall i :: 0 <= i < n ==> 0 <= m[i] < i + 1 } predicate ValidSolution(n: int, m: seq<int>, dm: seq<int>) { |dm| == n && |m| == n && (forall i :: 0 <= i < n ==> dm[i] >= m[i] + 1) && (forall i :: 0 <= i < n - 1 ==> dm[i] <= dm[i + 1]) } function SumBelow(m: seq<int>, dm: seq<int>): int requires |m| == |dm| { if |m| == 0 then 0 else (dm[0] - 1 - m[0]) + SumBelow(m[1..], dm[1..]) } method solve(n: int, m: seq<int>) returns (result: int) requires ValidInput(n, m) ensures result >= 0
```


### DA0258 - high confidence

Source: `apps` / `apps_test_1212`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a fence with n planks of heights, find k consecutive planks with the minimum sum of heights. Return the 1-indexed starting position of such a sequence. If multiple solutions exist, return any valid one.
```
Spec excerpt:
```dafny
function sum_window(heights: seq<int>, start: int, k: int): int requires 0 <= start requires start + k <= |heights| requires k > 0 decreases k { if k == 1 then heights[start] else heights[start] + sum_window(heights, start + 1, k - 1) } predicate ValidInput(n: int, k: int, heights: seq<int>) { 1 <= k <= n && |heights| == n && forall i :: 0 <= i < n ==> 1 <= heights[i] <= 100 } predicate ValidResult(result: int, n: int, k: int, heights: seq<int>) requires ValidInput(n, k, heights) { 1 <= result <= n-k+1 && forall start :: 0 <= start <= n-k ==> sum_window(heights, result-1, k) <= sum_window(heights, start, k) && forall start :: 0 <= start < result-1 ==> sum_window(heights, start, k) > sum_window(heights, result-1, k) } method solve(n: int, k: int, heights: seq<int>) returns (result: int) requires ValidInput(n, k, heights) ensures ValidResult(result, n, k, heights)
```


### DA0265 - high confidence

Source: `apps` / `apps_test_1240`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n columns of soldiers where column i has l_i soldiers starting with left leg and r_i soldiers starting with right leg, find which column to swap (change all left-leg soldiers to right-leg and vice versa) to maximize the beauty of the parade. Beauty is defined as |L - R| where L is total left-leg soldiers and R is total right-leg soldiers across all columns. You can swap at most one column. Output the 1-indexed column number to swap, or 0 if no swap improves the current beauty.
```
Spec excerpt:
```dafny
predicate ValidInput(columns: seq<(int, int)>) { forall i :: 0 <= i < |columns| ==> columns[i].0 > 0 && columns[i].1 > 0 } function abs(x: int): int { if x >= 0 then x else -x } function sum_left(columns: seq<(int, int)>): int { if |columns| == 0 then 0 else columns[0].0 + sum_left(columns[1..]) } function sum_right(columns: seq<(int, int)>): int { if |columns| == 0 then 0 else columns[0].1 + sum_right(columns[1..]) } method solve(columns: seq<(int, int)>) returns (result: int) requires ValidInput(columns) ensures 0 <= result <= |columns| ensures var L := sum_left(columns); var R := sum_right(columns); var original_beauty := abs(L - R); if result == 0 then forall i :: 0 <= i < |columns| ==> var new_L := L - columns[i].0 + columns[i].1; var new_R := R - columns[i].1 + columns[i].0; abs(new_L - new_R) <= original_beauty else 1 <= result <= |columns| && var best_idx := result - 1; var best_L := L - columns[best_idx].0 + columns[best_idx].1; var best_R := R - columns[best_idx].1 + columns[best_idx].0; var best_beauty := abs(best_L - best_R); best_beauty > original_beauty && forall i :...
```


### DA0281 - high confidence

Source: `apps` / `apps_test_1346`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given two polynomials f(x) and g(x) with positive integer coefficients, find any coefficient in their product h(x) = f(x) · g(x) that is not divisible by a given prime p. The gcd constraint ensures at least one coefficient in each polynomial is not divisible by p.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, m: int, p: int, f: seq<int>, g: seq<int>) { n >= 1 && m >= 1 && p >= 2 && |f| == n && |g| == m && (forall k :: 0 <= k < |f| ==> f[k] > 0) && (forall k :: 0 <= k < |g| ==> g[k] > 0) && (exists k :: 0 <= k < |f| && f[k] % p != 0) && (exists k :: 0 <= k < |g| && g[k] % p != 0) } predicate ValidResult(result: int, n: int, m: int, p: int, f: seq<int>, g: seq<int>) requires p != 0 { exists i, j :: 0 <= i < |f| && 0 <= j < |g| && (forall k :: 0 <= k < i ==> f[k] % p == 0) && f[i] % p != 0 && (forall k :: 0 <= k < j ==> g[k] % p == 0) && g[j] % p != 0 && result == i + j && 0 <= result < |f| + |g| } method solve(n: int, m: int, p: int, f: seq<int>, g: seq<int>) returns (result: int) requires ValidInput(n, m, p, f, g) requires p != 0 ensures ValidResult(result, n, m, p, f, g)
```


### DA0293 - high confidence

Source: `apps` / `apps_test_1430`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given a binary string S of length N and an integer K, find the maximum length of consecutive '1's achievable using at most K flip operations. Each flip operation chooses a contiguous range and flips all bits in that range (0→1, 1→0).
```
Spec excerpt:
```dafny
predicate ValidInput(N: int, K: int, S: string) { N > 0 && K >= 0 && |S| == N && forall i :: 0 <= i < |S| ==> S[i] == '0' || S[i] == '1' } function StringToBits(S: string): seq<int> requires forall i :: 0 <= i < |S| ==> S[i] == '0' || S[i] == '1' { seq(|S|, i requires 0 <= i < |S| => if S[i] == '0' then 0 else 1) } predicate ValidResult(result: int, N: int) { 0 <= result <= N } method solve(N: int, K: int, S: string) returns (result: int) requires ValidInput(N, K, S) ensures ValidResult(result, N)
```


### DA0315 - high confidence

Source: `apps` / `apps_test_1618`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a staircase with n stairs at non-decreasing heights, process m boxes thrown sequentially. Each box has width w and height h, covering stairs 1 through w. A box falls until its bottom touches either a stair top or a previously placed box top within its coverage area. Determine the landing height of each box's bottom.
```
Spec excerpt:
```dafny
function max(a: int, b: int): int { if a >= b then a else b } predicate ValidStairs(stair_heights: seq<int>) { |stair_heights| >= 1 && (forall i :: 0 <= i < |stair_heights| - 1 ==> stair_heights[i] <= stair_heights[i + 1]) && (forall i :: 0 <= i < |stair_heights| ==> stair_heights[i] >= 0) } predicate ValidBoxes(boxes: seq<(int, int)>, stairs_amount: int) { forall i :: 0 <= i < |boxes| ==> boxes[i].0 >= 1 && boxes[i].0 <= stairs_amount && boxes[i].1 >= 1 } predicate ValidResult(result: seq<int>, boxes: seq<(int, int)>, stair_heights: seq<int>) requires |stair_heights| >= 1 requires forall i :: 0 <= i < |boxes| ==> boxes[i].0 >= 1 && boxes[i].0 <= |stair_heights| { |result| == |boxes| && (forall i :: 0 <= i < |boxes| ==> result[i] >= 0) && (forall i :: 0 <= i < |boxes| ==> result[i] >= stair_heights[0] && result[i] >= stair_heights[boxes[i].0 - 1]) && (forall i :: 0 <= i < |boxes| ==> result[i] == max(if i == 0 then stair_heights[0] else result[i-1] + boxes[i-1].1, stair_heights[boxes[i].0 - 1])) } method solve(stairs_amount: int, stair_heights: seq<int>, boxes_amount: int, boxes:...
```


### DA0359 - high confidence

Source: `apps` / `apps_test_1849`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given an integer n, consider all integers from 0 to 10^n - 1, each padded with leading zeros to exactly n digits. A "block" is a maximal consecutive sequence of identical digits. For each length i from 1 to n, count the total number of blocks of length i across all these padded numbers. Output n integers modulo 998244353, where the i-th integer is the number of blocks of length i.
```
Spec excerpt:
```dafny
const MOD := 998244353 predicate ValidInput(n: int) { n >= 1 } function BlockCountFormula(n: int, i: int): int requires n >= 1 && 1 <= i <= n { if i == n then 10 else ((2 * 9 * pow(10, n - i - 1, MOD) * 10) + (if i < n - 1 then ((n - 1 - i) * 9 * 9 * pow(10, n - i - 2, MOD) * 10) else 0)) % MOD } predicate ValidResult(result: seq<int>, n: int) requires n >= 1 { |result| == n && (forall k :: 0 <= k < n ==> 0 <= result[k] < MOD) && (n >= 1 ==> result[n-1] == 10) && (forall i :: 0 <= i < n-1 ==> result[i] == BlockCountFormula(n, i+1)) } method solve(n: int) returns (result: seq<int>) requires ValidInput(n) ensures ValidResult(result, n)
```


### DA0363 - high confidence

Source: `apps` / `apps_test_1886`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a non-empty word consisting of lowercase and uppercase English letters, capitalize the first letter while keeping all other letters unchanged.
```
Spec excerpt:
```dafny
predicate ValidInput(word: string) { |word| > 0 && forall i :: 0 <= i < |word| ==> ('a' <= word[i] <= 'z') || ('A' <= word[i] <= 'Z') } predicate CorrectCapitalization(input: string, output: string) requires ValidInput(input) { |output| == |input| && ('A' <= output[0] <= 'Z') && (('a' <= input[0] <= 'z') ==> ('A' <= output[0] <= 'Z')) && (('A' <= input[0] <= 'Z') ==> (output[0] == input[0])) && forall i :: 1 <= i < |input| ==> output[i] == input[i] }
```


### DA0406 - high confidence

Source: `apps` / `apps_test_2238`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given an odd integer n (3 ≤ n ≤ 101), create an n×n matrix representing a crystal with a diamond pattern. Use 'D' for diamond cells and '*' for all other cells. The diamond pattern forms a symmetric diamond shape where the top half starts with 1 'D' and increases by 2 'D's per row until the middle row has n 'D's, then the bottom half decreases symmetrically. All 'D's in each row are centered with '*' characters filling remaining positions. // First half (including middle): rows 0 to magic // Second half: rows magic+1 to n-1
```
Spec excerpt:
```dafny
predicate ValidInput(n: int) { n >= 3 && n <= 101 && n % 2 == 1 } predicate ValidResult(result: seq<string>, n: int) { |result| == n && forall i :: 0 <= i < |result| ==> |result[i]| == n } predicate CorrectDiamondPattern(result: seq<string>, n: int) { |result| == n ==> ( var magic := (n - 1) / 2; (forall i :: 0 <= i <= magic && i < |result| ==> var stars := magic - i; var diamonds := n - 2 * stars; result[i] == RepeatChar('*', stars) + RepeatChar('D', diamonds) + RepeatChar('*', stars)) && (forall i :: magic + 1 <= i < n && i < |result| ==> var u := i - magic; var stars := u; var diamonds := n - 2 * stars; result[i] == RepeatChar('*', stars) + RepeatChar('D', diamonds) + RepeatChar('*', stars)) ) } method solve(n: int) returns (result: seq<string>) requires ValidInput(n) ensures ValidResult(result, n) ensures CorrectDiamondPattern(result, n)
```


### DA0409 - high confidence

Source: `apps` / `apps_test_2256`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n students in positions 1 to n, with two rival students initially at positions a and b, find the maximum distance between the rivals after performing at most x adjacent swaps. Distance between positions p and s is |p - s|.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, x: int, a: int, b: int) { 2 <= n <= 100 && 0 <= x <= 100 && 1 <= a <= n && 1 <= b <= n && a != b } function MaxDistance(n: int, x: int, a: int, b: int): int requires ValidInput(n, x, a, b) { var initialDistance := if a >= b then a - b else b - a; var maxPossibleDistance := initialDistance + x; var maxLineDistance := n - 1; if maxPossibleDistance <= maxLineDistance then maxPossibleDistance else maxLineDistance } predicate ValidResult(n: int, x: int, a: int, b: int, result: int) requires ValidInput(n, x, a, b) { result == MaxDistance(n, x, a, b) && 0 <= result <= n - 1 } method SolveRivalDistance(n: int, x: int, a: int, b: int) returns (result: int) requires ValidInput(n, x, a, b) ensures ValidResult(n, x, a, b, result) ensures result >= 0
```


### DA0417 - high confidence

Source: `apps` / `apps_test_2340`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Navigate down a cliff from height h to ground using platforms and magic crystals. Character starts at platform height h, can pull levers to hide current platform and toggle platform at height x-1, can fall safely at most 2 heights, and magic crystals can toggle any platform state (except height h). Find minimum number of crystals needed to reach ground safely.
```
Spec excerpt:
```dafny
predicate ValidInput(h: int, n: int, platforms: seq<int>) { h >= 1 && n >= 1 && |platforms| >= n && n > 0 && platforms[0] == h } predicate ValidCrystalCount(crystals: int, n: int) { crystals >= 0 && crystals <= n - 1 } function CountCrystalsNeeded(h: int, platforms: seq<int>): int requires |platforms| >= 1 requires platforms[0] == h requires h >= 1 { if |platforms| == 1 then 0 else CountCrystalsNeededUpTo(h, platforms + [0], |platforms| - 1) } function CountCrystalsNeededUpTo(h: int, arr: seq<int>, upTo: int): int requires |arr| >= 1 requires 0 <= upTo < |arr| requires arr[0] == h requires h >= 1 decreases upTo { if upTo == 0 then 0 else var curPos := SimulatePositionUpTo(h, arr, upTo - 1); var prevCrystals := CountCrystalsNeededUpTo(h, arr, upTo - 1); if curPos == arr[upTo] then prevCrystals else if upTo + 1 < |arr| && arr[upTo + 1] == arr[upTo] - 1 then prevCrystals else prevCrystals + 1 } function SimulatePositionUpTo(h: int, arr: seq<int>, upTo: int): int requires |arr| >= 1 requires 0 <= upTo < |arr| requires arr[0] == h requires h >= 1 decreases upTo { if upTo == 0 then h el...
```


### DA0438 - high confidence

Source: `apps` / `apps_test_2456`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given integers n and r, determine the number of distinct shapes that can be formed by painting n consecutive days on calendars where a week can have k days (1 ≤ k ≤ r). Days are arranged left-to-right in rows, wrapping to the next row when reaching the end of a week. All painted cells must be connected by sides. Two shapes are considered the same if one can be moved to exactly overlap the other using only parallel translations.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, r: int) { n >= 1 && r >= 1 } function ExpectedResult(n: int, r: int): int requires ValidInput(n, r) { var k := if r < n - 1 then r else n - 1; k * (k + 1) / 2 + (if r >= n then 1 else 0) }
```


### DA0445 - high confidence

Source: `apps` / `apps_test_2516`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given a string S of length N containing only digits 0-9 and a prime number P, count how many contiguous substrings of S are divisible by P when interpreted as base-10 integers.
```
Spec excerpt:
```dafny
predicate isPrime(p: int) requires p >= 2 { forall k :: 2 <= k < p ==> p % k != 0 } predicate ValidInput(n: int, p: int, s: string) { n >= 1 && p >= 2 && isPrime(p) && |s| == n && forall i :: 0 <= i < |s| ==> '0' <= s[i] <= '9' } function substringToInt(s: string): int requires forall i :: 0 <= i < |s| ==> '0' <= s[i] <= '9' requires |s| > 0 { if |s| == 1 then s[0] as int - '0' as int else substringToInt(s[..|s|-1]) * 10 + (s[|s|-1] as int - '0' as int) } predicate ValidResult(result: int, n: int) { result >= 0 && result <= n * (n + 1) / 2 } method solve(n: int, p: int, s: string) returns (result: int) requires ValidInput(n, p, s) ensures ValidResult(result, n)
```


### DA0454 - high confidence

Source: `apps` / `apps_test_2594`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a rectangular park represented as an n×m grid of squares, find the minimum number of lanterns needed to light up all squares. Lanterns are placed on edges between squares, and each lantern illuminates adjacent squares (up to 2 squares, or 1 if on boundary).
```
Spec excerpt:
```dafny
predicate ValidInput(input: string) { var lines := SplitLines(input); |lines| > 0 && var t := ParseInt(lines[0]); t > 0 && |lines| >= t + 1 && forall i {:trigger SplitSpaces(lines[i+1])} :: 0 <= i < t ==> var parts := SplitSpaces(lines[i+1]); |parts| >= 2 && var n := ParseInt(parts[0]); var m := ParseInt(parts[1]); n >= 1 && m >= 1 } function MinLanterns(n: int, m: int): int requires n >= 1 && m >= 1 { (n * m + 1) / 2 } predicate ValidOutput(input: string, output: seq<int>) requires ValidInput(input) { var lines := SplitLines(input); var t := ParseInt(lines[0]); |output| == t && forall i {:trigger output[i]} :: 0 <= i < t ==> var parts := SplitSpaces(lines[i+1]); |parts| >= 2 && var n := ParseInt(parts[0]); var m := ParseInt(parts[1]); n >= 1 && m >= 1 && output[i] == MinLanterns(n, m) }
```


### DA0525 - high confidence

Source: `apps` / `apps_test_4298`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given N apple trees numbered 1 to N in a row, find the minimum number of inspectors needed to inspect all trees. Each inspector at position i covers trees from (i-D) to (i+D).
```
Spec excerpt:
```dafny
predicate ValidInput(N: int, D: int) { N >= 1 && N <= 20 && D >= 1 && D <= 20 } function CoverageRange(position: int, D: int): (int, int) { (position - D, position + D) } predicate TreesCovered(N: int, D: int, inspectors: int) { inspectors >= 1 && inspectors <= N && inspectors == ((N - 1) / (2 * D + 1)) + 1 }
```


### DA0538 - high confidence

Source: `apps` / `apps_test_4326`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given N students, divide them into groups such that the number of groups containing 3 or more students is maximized. Groups with 2 or fewer students are not counted toward the result.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int) { 1 <= n <= 1000 } function MaxGroupsWithAtLeastThree(n: int): int requires ValidInput(n) { n / 3 } predicate ValidSolution(n: int, result: int) requires ValidInput(n) { result == MaxGroupsWithAtLeastThree(n) && result >= 0 && result <= n }
```


### DA0650 - high confidence

Source: `apps` / `apps_test_4635`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given two integers n and k, construct a string of length n using only the first k letters of the alphabet ('a', 'b', ..., k-th letter). Each of the k letters must appear at least once. Maximize the minimum frequency among all letters used. The optimal strategy is to distribute characters as evenly as possible by cycling through the k letters repeatedly.
```
Spec excerpt:
```dafny
predicate ValidInput(input: string) { |input| > 0 && (exists lines :: lines == SplitByNewline(input) && |lines| >= 1 && IsValidInteger(lines[0]) && StringToIntVal(lines[0]) >= 0 && |lines| >= StringToIntVal(lines[0]) + 1 && (forall i :: 1 <= i <= StringToIntVal(lines[0]) && i < |lines| ==> ValidTestCaseLine(lines[i]))) } predicate ValidTestCaseLine(line: string) { exists parts :: (parts == SplitBySpace(line) && |parts| >= 2 && IsValidInteger(parts[0]) && IsValidInteger(parts[1]) && StringToIntVal(parts[0]) > 0 && StringToIntVal(parts[1]) > 0 && StringToIntVal(parts[1]) <= 26) } predicate IsValidInteger(s: string) { |s| > 0 && (|s| == 1 || s[0] != '0' || s == "0") && forall i :: 0 <= i < |s| ==> '0' <= s[i] <= '9' } function StringToIntVal(s: string): int requires IsValidInteger(s) ensures StringToIntVal(s) >= 0 { if |s| == 0 then 0 else if |s| == 1 then (s[0] as int) - 48 else StringToIntVal(s[0..|s|-1]) * 10 + ((s[|s|-1] as int) - 48) } predicate CyclicPatternCorrect(n: int, k: int, output: string) requires n > 0 && k > 0 && k <= 26 { |output| == n && (forall j :: 0 <= j < n ==>...
```


### DH0057 - high confidence

Source: `humaneval` / `humaneval_054`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
This task involves determining if two strings contain exactly the same set of unique characters, regardless of character frequency or order. The implementation should compare the set of characters in each string and return true if they are identical sets.
```
Spec excerpt:
```dafny
function CharSet(s: string): set<char> { set c | c in s } method same_chars(s0: string, s1: string) returns (result: bool) ensures result == (CharSet(s0) == CharSet(s1))
```


### DH0136 - high confidence

Source: `humaneval` / `humaneval_134`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
This verification task involves implementing a method to determine if the last character of a string is an alphabetical character that stands alone (not part of a word). A "word" is defined as a group of characters separated by spaces. The method should return true if the last character is a letter AND is not part of a word, false otherwise. A standalone letter is either the entire string (single character) or a letter preceded by a space.
```
Spec excerpt:
```dafny
predicate IsAlpha(c: char) { ('a' <= c <= 'z') || ('A' <= c <= 'Z') } predicate ValidLastCharIsStandaloneLetter(txt: string) { |txt| > 0 && IsAlpha(txt[|txt| - 1]) && (|txt| == 1 || txt[|txt| - 2] == ' ') } method check_if_last_char_is_a_letter(txt: string) returns (result: bool) ensures result == ValidLastCharIsStandaloneLetter(txt)
```


### DA0136 - high confidence

Source: `apps` / `apps_test_682`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given starting position (r1, c1) and ending position (r2, c2) on an 8×8 chessboard, find the minimum number of moves required for a rook, bishop, and king to move from the starting position to the ending position. Return 0 if a piece cannot reach the destination.
```
Spec excerpt:
```dafny
predicate ValidPosition(r: int, c: int) { 1 <= r <= 8 && 1 <= c <= 8 } function RookMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else if r1 == r2 || c1 == c2 then 1 else 2 } function BishopMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff == col_diff then 1 else if (r1 + c1) % 2 == (r2 + c2) % 2 then 2 else 0 } function KingMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff >= col_diff then row_diff else col_diff } predicate ValidResult(result: seq<int>, r1: int, c1: int, r2: int, c2: int) requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { |result| == 3 && result[0] == RookMoves(r1, c1, r2, c2) && resul...
```


### DA0136 - high confidence

Source: `apps` / `apps_test_682`

Suspected missing requirement: **formal optimality/argmax/minimality comparison**

Why spec may be weak: NL contains optimization missing cues; spec lacks expected patterns for formal optimality/argmax/minimality comparison; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a feasible but non-optimal value`

NL excerpt:
```text
Given starting position (r1, c1) and ending position (r2, c2) on an 8×8 chessboard, find the minimum number of moves required for a rook, bishop, and king to move from the starting position to the ending position. Return 0 if a piece cannot reach the destination.
```
Spec excerpt:
```dafny
predicate ValidPosition(r: int, c: int) { 1 <= r <= 8 && 1 <= c <= 8 } function RookMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else if r1 == r2 || c1 == c2 then 1 else 2 } function BishopMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { if r1 == r2 && c1 == c2 then 0 else var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff == col_diff then 1 else if (r1 + c1) % 2 == (r2 + c2) % 2 then 2 else 0 } function KingMoves(r1: int, c1: int, r2: int, c2: int): int requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { var row_diff := if r1 >= r2 then r1 - r2 else r2 - r1; var col_diff := if c1 >= c2 then c1 - c2 else c2 - c1; if row_diff >= col_diff then row_diff else col_diff } predicate ValidResult(result: seq<int>, r1: int, c1: int, r2: int, c2: int) requires ValidPosition(r1, c1) && ValidPosition(r2, c2) { |result| == 3 && result[0] == RookMoves(r1, c1, r2, c2) && resul...
```


### DA0152 - high confidence

Source: `apps` / `apps_test_755`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Find the minimum number of steps to move from position 0 to position x on a number line, where each step can move forward by 1, 2, 3, 4, or 5 positions.
```
Spec excerpt:
```dafny
predicate ValidInput(x: int) { x >= 1 } predicate IsMinimalSteps(x: int, steps: int) requires x >= 1 { steps >= 1 && steps * 5 >= x && (steps - 1) * 5 < x }
```


### DA0157 - high confidence

Source: `apps` / `apps_test_785`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a rectangular room with dimensions a × b meters, accommodate exactly n students such that each student has at least 6 square meters of space. You can increase either or both dimensions by any positive integer amount. Find the minimum possible area and corresponding dimensions.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int) { n > 0 && a > 0 && b > 0 } predicate ValidOutput(result: seq<int>, n: int, a: int, b: int) { |result| == 3 && result[0] >= 6 * n && result[1] > 0 && result[2] > 0 && result[0] == result[1] * result[2] && ((result[1] >= a && result[2] >= b) || (result[1] >= b && result[2] >= a)) } method solve(n: int, a: int, b: int) returns (result: seq<int>) requires ValidInput(n, a, b) ensures ValidOutput(result, n, a, b)
```


### DA0157 - high confidence

Source: `apps` / `apps_test_785`

Suspected missing requirement: **formal optimality/argmax/minimality comparison**

Why spec may be weak: NL contains optimization missing cues; spec lacks expected patterns for formal optimality/argmax/minimality comparison; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a feasible but non-optimal value`

NL excerpt:
```text
Given a rectangular room with dimensions a × b meters, accommodate exactly n students such that each student has at least 6 square meters of space. You can increase either or both dimensions by any positive integer amount. Find the minimum possible area and corresponding dimensions.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int) { n > 0 && a > 0 && b > 0 } predicate ValidOutput(result: seq<int>, n: int, a: int, b: int) { |result| == 3 && result[0] >= 6 * n && result[1] > 0 && result[2] > 0 && result[0] == result[1] * result[2] && ((result[1] >= a && result[2] >= b) || (result[1] >= b && result[2] >= a)) } method solve(n: int, a: int, b: int) returns (result: seq<int>) requires ValidInput(n, a, b) ensures ValidOutput(result, n, a, b)
```


### DA0306 - high confidence

Source: `apps` / `apps_test_1576`

Suspected missing requirement: **exact output formatting/order/string constraints**

Why spec may be weak: NL contains output format missing cues; spec lacks expected patterns for exact output formatting/order/string constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Decrypt a string that was encrypted using the Right-Left cipher. The Right-Left cipher encrypts by starting with the first character, then alternating between appending to the right (even positions) and prepending to the left (odd positions) for subsequent characters.
```
Spec excerpt:
```dafny
predicate ValidInput(t: string) { |t| >= 1 } method solve(t: string) returns (result: string) requires ValidInput(t) ensures |result| == |t|
```


### DA0306 - high confidence

Source: `apps` / `apps_test_1576`

Suspected missing requirement: **specified tie-breaking rule**

Why spec may be weak: NL contains tie break missing cues; spec lacks expected patterns for specified tie-breaking rule; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Decrypt a string that was encrypted using the Right-Left cipher. The Right-Left cipher encrypts by starting with the first character, then alternating between appending to the right (even positions) and prepending to the left (odd positions) for subsequent characters.
```
Spec excerpt:
```dafny
predicate ValidInput(t: string) { |t| >= 1 } method solve(t: string) returns (result: string) requires ValidInput(t) ensures |result| == |t|
```


### DA0515 - high confidence

Source: `apps` / `apps_test_4267`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a room temperature in degrees Celsius, determine whether to turn on an air conditioner. The air conditioner should be turned on if and only if the temperature is 30°C or higher.
```
Spec excerpt:
```dafny
predicate ValidTemperature(temp: int) { -40 <= temp <= 40 } function ExpectedOutput(temp: int): string { if temp >= 30 then "Yes\n" else "No\n" } predicate CorrectOutput(temp: int, output: string) { output == ExpectedOutput(temp) } method solve(X: int) returns (result: string) requires ValidTemperature(X) ensures CorrectOutput(X, result)
```


### DA0673 - high confidence

Source: `apps` / `apps_test_4718`

Suspected missing requirement: **exact output formatting/order/string constraints**

Why spec may be weak: NL contains output format missing cues; spec lacks expected patterns for exact output formatting/order/string constraints; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given a date string in format "2017/01/dd" where dd represents a day from 01 to 31, replace the year "2017" with "2018" and output the corrected date string.
```
Spec excerpt:
```dafny
predicate ValidInput(dateStr: string) { |dateStr| == 10 && dateStr[0..4] == "2017" } predicate ValidOutput(input: string, output: string) requires |input| >= 4 { output == "2018" + input[4..] && |output| == 10 && output[0..4] == "2018" && output[4..] == input[4..] } method solve(dateStr: string) returns (result: string) requires ValidInput(dateStr) ensures ValidOutput(dateStr, result)
```


### DH0160 - high confidence

Source: `humaneval` / `humaneval_159`

Suspected missing requirement: **semantic correctness condition**

Why spec may be weak: formal postcondition appears to contain only weak result/range/shape constraints; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
This verification task involves implementing a method that calculates carrot consumption for a rabbit. Given the number of carrots already eaten, the number of additional carrots needed, and the number of carrots remaining in stock, the method should return the total carrots that will be eaten and how many carrots will be left. The rabbit will eat as many carrots as possible from the remaining stock, up to the number needed.
```
Spec excerpt:
```dafny
predicate ValidInput(number: int, need: int, remaining: int) { 0 <= number <= 1000 && 0 <= need <= 1000 && 0 <= remaining <= 1000 } function CanEat(need: int, remaining: int): int { if need <= remaining then need else remaining } function TotalEaten(number: int, need: int, remaining: int): int { number + CanEat(need, remaining) } function CarrotsLeft(need: int, remaining: int): int { remaining - CanEat(need, remaining) } predicate ValidResult(result: seq<int>, number: int, need: int, remaining: int) { |result| == 2 && result[0] == TotalEaten(number, need, remaining) && result[1] == CarrotsLeft(need, remaining) && result[0] >= number && result[1] >= 0 && result[1] <= remaining } method eat(number: int, need: int, remaining: int) returns (result: seq<int>) requires ValidInput(number, need, remaining) ensures ValidResult(result, number, need, remaining)
```


### DA0003 - medium confidence

Source: `apps` / `apps_test_11`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```


### DA0003 - medium confidence

Source: `apps` / `apps_test_11`

Suspected missing requirement: **formal optimality/argmax/minimality comparison**

Why spec may be weak: NL contains optimization missing cues; spec lacks expected patterns for formal optimality/argmax/minimality comparison; spec appears trivial or shape/range-only

Suggested bad candidate: `return 0 or 1 regardless of the input`

NL excerpt:
```text
Given n tiles numbered 1 to n, paint tiles according to rules: - Tile can be painted Red if divisible by a (gives p chocolates) - Tile can be painted Blue if divisible by b (gives q chocolates) - If divisible by both a and b, choose the color giving more chocolates Find the maximum total chocolates possible.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, a: int, b: int, p: int, q: int) { n > 0 && a > 0 && b > 0 && p > 0 && q > 0 } function gcd(a: int, b: int): int requires a > 0 && b >= 0 ensures gcd(a, b) > 0 decreases b { if b == 0 then a else gcd(b, a % b) } method solve(n: int, a: int, b: int, p: int, q: int) returns (result: int) requires ValidInput(n, a, b, p, q) ensures result >= 0
```


### DA0417 - medium confidence

Source: `apps` / `apps_test_2340`

Suspected missing requirement: **formal optimality/argmax/minimality comparison**

Why spec may be weak: NL contains optimization missing cues; spec lacks expected patterns for formal optimality/argmax/minimality comparison; spec appears trivial or shape/range-only

Suggested bad candidate: `return a feasible but non-optimal value`

NL excerpt:
```text
Navigate down a cliff from height h to ground using platforms and magic crystals. Character starts at platform height h, can pull levers to hide current platform and toggle platform at height x-1, can fall safely at most 2 heights, and magic crystals can toggle any platform state (except height h). Find minimum number of crystals needed to reach ground safely.
```
Spec excerpt:
```dafny
predicate ValidInput(h: int, n: int, platforms: seq<int>) { h >= 1 && n >= 1 && |platforms| >= n && n > 0 && platforms[0] == h } predicate ValidCrystalCount(crystals: int, n: int) { crystals >= 0 && crystals <= n - 1 } function CountCrystalsNeeded(h: int, platforms: seq<int>): int requires |platforms| >= 1 requires platforms[0] == h requires h >= 1 { if |platforms| == 1 then 0 else CountCrystalsNeededUpTo(h, platforms + [0], |platforms| - 1) } function CountCrystalsNeededUpTo(h: int, arr: seq<int>, upTo: int): int requires |arr| >= 1 requires 0 <= upTo < |arr| requires arr[0] == h requires h >= 1 decreases upTo { if upTo == 0 then 0 else var curPos := SimulatePositionUpTo(h, arr, upTo - 1); var prevCrystals := CountCrystalsNeededUpTo(h, arr, upTo - 1); if curPos == arr[upTo] then prevCrystals else if upTo + 1 < |arr| && arr[upTo + 1] == arr[upTo] - 1 then prevCrystals else prevCrystals + 1 } function SimulatePositionUpTo(h: int, arr: seq<int>, upTo: int): int requires |arr| >= 1 requires 0 <= upTo < |arr| requires arr[0] == h requires h >= 1 decreases upTo { if upTo == 0 then h el...
```


### DA0438 - medium confidence

Source: `apps` / `apps_test_2456`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given integers n and r, determine the number of distinct shapes that can be formed by painting n consecutive days on calendars where a week can have k days (1 ≤ k ≤ r). Days are arranged left-to-right in rows, wrapping to the next row when reaching the end of a week. All painted cells must be connected by sides. Two shapes are considered the same if one can be moved to exactly overlap the other using only parallel translations.
```
Spec excerpt:
```dafny
predicate ValidInput(n: int, r: int) { n >= 1 && r >= 1 } function ExpectedResult(n: int, r: int): int requires ValidInput(n, r) { var k := if r < n - 1 then r else n - 1; k * (k + 1) / 2 + (if r >= n then 1 else 0) }
```


### DA0525 - medium confidence

Source: `apps` / `apps_test_4298`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec appears trivial or shape/range-only

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given N apple trees numbered 1 to N in a row, find the minimum number of inspectors needed to inspect all trees. Each inspector at position i covers trees from (i-D) to (i+D).
```
Spec excerpt:
```dafny
predicate ValidInput(N: int, D: int) { N >= 1 && N <= 20 && D >= 1 && D <= 20 } function CoverageRange(position: int, D: int): (int, int) { (position - D, position + D) } predicate TreesCovered(N: int, D: int, inspectors: int) { inspectors >= 1 && inspectors <= N && inspectors == ((N - 1) / (2 * D + 1)) + 1 }
```


### DA0525 - medium confidence

Source: `apps` / `apps_test_4298`

Suspected missing requirement: **formal optimality/argmax/minimality comparison**

Why spec may be weak: NL contains optimization missing cues; spec lacks expected patterns for formal optimality/argmax/minimality comparison; spec appears trivial or shape/range-only

Suggested bad candidate: `return a feasible but non-optimal value`

NL excerpt:
```text
Given N apple trees numbered 1 to N in a row, find the minimum number of inspectors needed to inspect all trees. Each inspector at position i covers trees from (i-D) to (i+D).
```
Spec excerpt:
```dafny
predicate ValidInput(N: int, D: int) { N >= 1 && N <= 20 && D >= 1 && D <= 20 } function CoverageRange(position: int, D: int): (int, int) { (position - D, position + D) } predicate TreesCovered(N: int, D: int, inspectors: int) { inspectors >= 1 && inspectors <= N && inspectors == ((N - 1) / (2 * D + 1)) + 1 }
```


### DH0136 - medium confidence

Source: `humaneval` / `humaneval_134`

Suspected missing requirement: **specified tie-breaking rule**

Why spec may be weak: NL contains tie break missing cues; spec lacks expected patterns for specified tie-breaking rule; spec appears trivial or shape/range-only; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
This verification task involves implementing a method to determine if the last character of a string is an alphabetical character that stands alone (not part of a word). A "word" is defined as a group of characters separated by spaces. The method should return true if the last character is a letter AND is not part of a word, false otherwise. A standalone letter is either the entire string (single character) or a letter preceded by a space.
```
Spec excerpt:
```dafny
predicate IsAlpha(c: char) { ('a' <= c <= 'z') || ('A' <= c <= 'Z') } predicate ValidLastCharIsStandaloneLetter(txt: string) { |txt| > 0 && IsAlpha(txt[|txt| - 1]) && (|txt| == 1 || txt[|txt| - 2] == ' ') } method check_if_last_char_is_a_letter(txt: string) returns (result: bool) ensures result == ValidLastCharIsStandaloneLetter(txt)
```


### DA0014 - medium confidence

Source: `apps` / `apps_test_66`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Two athletes Willman and Bolt compete in a race with step lengths w and b meters respectively. The race distance L is chosen uniformly at random from integers 1 to t (inclusive). Each athlete can take at most floor(L/step_length) steps, traveling floor(L/step_length) * step_length distance. They tie when they travel the same total distance: floor(L/w) * w = floor(L/b) * b. Find the probability that they tie, expressed as an irreducible fraction.
```
Spec excerpt:
```dafny
predicate ValidInput(t: int, w: int, b: int) { t > 0 && w > 0 && b > 0 } predicate ValidFraction(numerator: int, denominator: int) { numerator >= 0 && denominator > 0 && numerator <= denominator } predicate IsIrreducibleFraction(numerator: int, denominator: int) requires ValidFraction(numerator, denominator) { gcd(numerator, denominator) == 1 } method solve(t: int, w: int, b: int) returns (numerator: int, denominator: int) requires ValidInput(t, w, b) ensures ValidFraction(numerator, denominator) ensures IsIrreducibleFraction(numerator, denominator)
```


### DA0063 - medium confidence

Source: `apps` / `apps_test_244`

Suspected missing requirement: **semantic definition of the exact returned value**

Why spec may be weak: NL contains exact value missing cues; spec lacks expected patterns for semantic definition of the exact returned value; spec has few semantic-strength tokens

Suggested bad candidate: `return a range/shape-valid but semantically wrong value`

NL excerpt:
```text
Given 3 shells numbered 0, 1, 2, a ball starts under one shell. An operator makes n moves: odd moves swap shells 0 and 1, even moves swap shells 1 and 2. Given the final position x after n moves, determine the initial position of the ball. // odd move: swap 0 and 1 // even move: swap 1 and 2 // reverse odd move: swap 0 and 1 // reverse even move: swap 1 and 2
```
Spec excerpt:
```dafny
predicate ValidPosition(pos: int) { 0 <= pos <= 2 } function SwapMove(pos: int, moveNum: int): int requires ValidPosition(pos) requires moveNum >= 1 ensures ValidPosition(SwapMove(pos, moveNum)) { if moveNum % 2 == 1 then if pos == 0 then 1 else if pos == 1 then 0 else 2 else if pos == 1 then 2 else if pos == 2 then 1 else 0 } function ReverseMove(pos: int, moveNum: int): int requires ValidPosition(pos) requires moveNum >= 1 ensures ValidPosition(ReverseMove(pos, moveNum)) { if moveNum % 2 == 1 then if pos == 0 then 1 else if pos == 1 then 0 else 2 else if pos == 1 then 2 else if pos == 2 then 1 else 0 } method ShellGame(n: int, x: int) returns (result: int) requires n >= 1 && n <= 2000000000 requires ValidPosition(x) ensures ValidPosition(result)
```
