"""
Test runner tự dong cho Social Network BFS.
Chay: python scripts/run_tests.py
"""
import subprocess, os

BINARY  = r".\SocialMedia.exe"
TESTDIR = r".\scripts\testcases"
TIMEOUT = 10  # giay

# (ten_thu_muc, [cac_lenh_nhap_stdin])
TEST_CASES = [
    # Nhom 1: CRUD
    ("tc01_connection_nonexistent",
     ["1", "users.csv", "edges.txt", "12", "0"]),

    ("tc03_remove_nonexistent_user",
     ["1", "users.csv", "edges.txt", "4", "9999", "0"]),

    # Nhom 2: I/O
    ("tc08_file_not_found",
     ["1", "khong_ton_tai.csv", "khong_ton_tai.txt", "6", "", "0"]),

    # Nhom 3: BFS
    ("tc13_chain_graph",
     ["1", "users.csv", "edges.txt", "10", "1", "", "0"]),

    # Nhom 4: Goi y
    ("tc18_isolated_user",
     ["1", "users.csv", "edges.txt", "11", "3", "5", "0"]),

    # Nhom 5: Bien
    ("tc25_single_user",
     ["1", "users.csv", "edges.txt", "11", "1", "5", "0"]),

    # Nhom 6: Export/Search
    ("tc30_search_by_name",
     ["1", "users.csv", "edges.txt", "8", "an", "", "0"]),

    # Nhom 7: Hieu nang
    ("tc34_measure_performance",
     ["1", "users.csv", "edges.txt", "14", "1", "0"]),
]

def run_tc(name, inputs):
    tc_dir = os.path.join(TESTDIR, name)
    stdin_str = "\n".join(inputs) + "\n"
    try:
        proc = subprocess.run(
            [BINARY],
            input=stdin_str.encode("utf-8"),
            capture_output=True,
            timeout=TIMEOUT,
            cwd=tc_dir
        )
        output = proc.stdout.decode("utf-8", errors="replace")
        crashed = proc.returncode != 0
        return not crashed, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

pass_count = fail_count = 0
for name, inputs in TEST_CASES:
    ok, out = run_tc(name, inputs)
    status = "PASS" if ok else "FAIL"
    if ok: pass_count += 1
    else:  fail_count += 1
    print(f"[{status}] {name}")
    if not ok:
        print(f"       >> {out[:150]}")

print(f"\nKet qua: {pass_count} PASS / {fail_count} FAIL / {len(TEST_CASES)} tong")
