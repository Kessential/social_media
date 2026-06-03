"""
Script chay TC33: Stress Memory
Pipe stdin truc tiep vao tien trinh SocialMedia.exe, kiem tra ket qua.
Chay tu thu muc goc du an: python scripts/run_tc33.py
"""
import subprocess, os, sys

# Buoc nay can thiet tren Windows de in ky tu UTF-8 ra terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BINARY   = r"./SocialMedia"
TC_DIR   = r"./scripts/testcases/tc33_stress_memory"
TIMEOUT  = 30  # giay
USERS    = "./scripts/testcases/tc33_stress_memory/users.csv"
EDGES    = "./scripts/testcases/tc33_stress_memory/edges.txt"

# ---------- Xay dung chuoi stdin ----------
lines = []

# Buoc 1: Load du lieu
lines += ["1", USERS, EDGES]

# Buoc 2: removeUser(1..50) — menu 4, nhap ID
for i in range(1, 51):
    lines += ["4", str(i)]

# Buoc 3: Thoat menu xoa, ve menu chinh, roi thoat
lines += ["12"]   # quit sub-menu (neu co)

# Buoc 4: Load lai cung file
lines += ["1", USERS, EDGES]

# Buoc 5: Thoat chuong trinh
lines += ["12"]

stdin_str = "\n".join(lines) + "\n"

# ---------- In preview stdin ----------
print("=" * 60)
print("TC33 -- Stress Memory: load -> xoa het -> load lai")
print("=" * 60)
print(f"Binary : {BINARY}")
print(f"Timeout: {TIMEOUT}s")
print(f"Stdin ({len(lines)} dong):")
for idx, l in enumerate(lines, 1):
    print(f"  [{idx:>3}] {l!r}")
print("=" * 60)

# ---------- Chay chuong trinh (stream output truc tiep ra terminal) ----------
collected_stdout = []
retcode = 0

print("\n--- OUTPUT (live) ---")
sys.stdout.flush()

try:
    proc = subprocess.Popen(
        [BINARY],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd(),
    )
    # Gui toan bo stdin mot lan, doc stdout theo tung dòng
    proc.stdin.write(stdin_str.encode("utf-8"))
    proc.stdin.close()

    # Stream stdout ra terminal dong thoi giu lai de so sanh
    for raw_line in proc.stdout:
        sys.stdout.buffer.write(raw_line)
        sys.stdout.buffer.flush()
        collected_stdout.append(raw_line.decode("utf-8", errors="replace"))

    proc.wait(timeout=TIMEOUT)
    retcode = proc.returncode

    stderr_raw = proc.stderr.read()
    if stderr_raw:
        print("--- STDERR ---")
        sys.stdout.buffer.write(stderr_raw)
        sys.stdout.buffer.flush()

except subprocess.TimeoutExpired:
    proc.kill()
    print("[FAIL] TIMEOUT — chuong trinh khong ket thuc trong thoi gian cho phep.")
    sys.exit(1)
except FileNotFoundError:
    print(f"[FAIL] Khong tim thay binary: {BINARY}")
    print("       Hay build truoc: cmake --build build --config Release")
    sys.exit(1)

stdout = "".join(collected_stdout)

# ---------- Kiem tra exit code ----------
crashed = retcode != 0
print(f"\nReturn code: {retcode}  →  {'CRASH / ERROR' if crashed else 'OK'}")

# ---------- So sanh voi expected (neu co) ----------
expected_path = os.path.join(TC_DIR, "expected.txt")
if os.path.exists(expected_path):
    with open(expected_path, encoding="utf-8") as f:
        expected = f.read()
    print("\n--- EXPECTED ---")
    print(expected)
    # Kiem tra tung dong key trong expected co xuat hien trong output
    key_lines = [l.strip() for l in expected.splitlines() if l.strip()]
    missing = [l for l in key_lines if l not in stdout]
    if not missing and not crashed:
        print("\n[PASS] TC33 — tat ca dong kiem tra deu co trong output, khong crash.")
    else:
        if crashed:
            print("\n[FAIL] TC33 — chuong trinh bi crash (returncode != 0).")
        if missing:
            print(f"\n[FAIL] TC33 — cac dong sau KHONG xuat hien trong output:")
            for m in missing:
                print(f"         - {m!r}")
else:
    if not crashed:
        print("\n[PASS] TC33 — chuong trinh chay thanh cong (khong co expected.txt de so sanh).")
    else:
        print("\n[FAIL] TC33 — chuong trinh bi crash.")