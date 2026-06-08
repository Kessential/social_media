"""
Script chay TC33: Stress Memory
Pipe stdin truc tiep vao tien trinh SocialMedia.exe, kiem tra ket qua.
Chay tu thu muc goc du an: python scripts/run_tc33.py
"""
import subprocess, os, sys, re

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

# Buoc 2: Kiem tra thong ke sau khi load (phai co 50 users, 49 edges)
lines += ["12"]

# Buoc 3: removeUser(1..50) — menu 4, nhap ID
for i in range(1, 51):
    lines += ["4", str(i)]

# Buoc 4: Kiem tra thong ke sau khi xoa het (phai co 0 users, 0 edges)
lines += ["12"]

# Buoc 5: Load lai cung file
lines += ["1", USERS, EDGES]

# Buoc 6: Kiem tra thong ke sau khi load lai (phai co 50 users, 49 edges)
lines += ["12"]

# Buoc 7: Thoat chuong trinh
lines += ["0"]

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

# ---------- Kiem tra dieu kien thuc te trong output ----------
print("\n--- KIEM TRA TC33 ---")
print("TC33: Stress memory — load, xoa het, load lai")

failures = []

# Tim tat ca cac khoi thong ke tu output
# Output thong ke co dang:
#   Tong so nguoi dung:    XX
#   Tong so ket noi:       YY
stat_blocks = re.findall(
    r"Tong so nguoi dung:\s*(\d+).*?Tong so ket noi:\s*(\d+)",
    stdout,
    re.DOTALL,
)

print(f"\nTim thay {len(stat_blocks)} khoi thong ke trong output:")
for i, (users, edges) in enumerate(stat_blocks, 1):
    print(f"  Khoi {i}: users={users}, edges={edges}")

# Buoc 1: Sau khi load lan dau — phai co 50 users, 49 edges
print("\nBuoc 1: Load 50 users va 49 connections.")
if len(stat_blocks) >= 1:
    u1, e1 = stat_blocks[0]
    if int(u1) == 50 and int(e1) == 49:
        print(f"  [OK] getUserCount()={u1}, getEdgeCount()={e1}")
    else:
        msg = f"getUserCount()={u1} (can 50), getEdgeCount()={e1} (can 49)"
        print(f"  [FAIL] {msg}")
        failures.append(f"Buoc 1: {msg}")
else:
    print("  [FAIL] Khong tim thay thong ke sau khi load lan dau.")
    failures.append("Buoc 1: Khong co thong ke sau load lan dau")

# Buoc 2: Sau khi xoa het — phai co 0 users, 0 edges
print("\nBuoc 2: removeUser(1) den removeUser(50) — xoa tung user.")
print("Buoc 3: Kiem tra getUserCount() = 0, getEdgeCount() = 0.")
if len(stat_blocks) >= 2:
    u2, e2 = stat_blocks[1]
    if int(u2) == 0 and int(e2) == 0:
        print(f"  [OK] getUserCount()={u2}, getEdgeCount()={e2}")
    else:
        msg = f"getUserCount()={u2} (can 0), getEdgeCount()={e2} (can 0)"
        print(f"  [FAIL] {msg}")
        failures.append(f"Buoc 3: {msg}")
else:
    print("  [FAIL] Khong tim thay thong ke sau khi xoa het.")
    failures.append("Buoc 3: Khong co thong ke sau xoa het")

# Buoc 3: Sau khi load lai — phai co 50 users, 49 edges
print("\nBuoc 4: Load lai cung file data.")
print("Buoc 5: Kiem tra getUserCount() = 50, getEdgeCount() = 49.")
if len(stat_blocks) >= 3:
    u3, e3 = stat_blocks[2]
    if int(u3) == 50 and int(e3) == 49:
        print(f"  [OK] getUserCount()={u3}, getEdgeCount()={e3}")
    else:
        msg = f"getUserCount()={u3} (can 50), getEdgeCount()={e3} (can 49)"
        print(f"  [FAIL] {msg}")
        failures.append(f"Buoc 5: {msg}")
else:
    print("  [FAIL] Khong tim thay thong ke sau khi load lai.")
    failures.append("Buoc 5: Khong co thong ke sau load lai")

print("\nKiem tra: Khong memory leak, khong crash, data duoc tai lai dung.")

# ---------- Ket qua cuoi cung ----------
print("\n" + "=" * 60)
if not failures and not crashed:
    print("[PASS] TC33 — tat ca dieu kien deu thoa man, khong crash.")
else:
    if crashed:
        print("[FAIL] TC33 — chuong trinh bi crash (returncode != 0).")
    for f in failures:
        print(f"[FAIL] {f}")
print("=" * 60)