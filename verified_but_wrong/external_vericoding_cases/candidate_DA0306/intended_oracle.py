"""Task-specific intended oracle for DA0306."""


def _encrypt_right_left(s: str) -> str:
    out = [s[0]]
    for i in range(1, len(s)):
        if i % 2 == 0:
            out.append(s[i])
        else:
            out.insert(0, s[i])
    return "".join(out)


def run_tests(candidate):
    plains = ["abcde", "hello", "crl"]
    tests = [(_encrypt_right_left(p), p) for p in plains]
    rows = []
    for enc, plain in tests:
        got = candidate(enc)
        rows.append(
            {
                "input": repr((enc,)),
                "expected": plain,
                "actual": got,
                "intended_oracle_pass": got == plain,
                "oracle_note": "NL requires decryption of Right-Left cipher, not just matching output length.",
            }
        )
    return rows
