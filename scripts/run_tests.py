#!/usr/bin/env python3
"""
run_tests.py – Kiem thu tu dong toan bo chuc nang menu 0-14
Dataset chinh: scripts/users.csv + scripts/edges.txt
Chay tu thu muc goc: python scripts/run_tests.py
"""

import subprocess
import sys
import os

# ── Cau hinh ──────────────────────────────────────────────────────────────────
BINARY  = "./SocialMedia"
USERS   = "scripts/users.csv"
EDGES   = "scripts/edges.txt"
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ──────────────────────────────────────────────────────────────────────────────

PASS_COUNT = 0
FAIL_COUNT = 0
W = 72

# Lenh tai dataset chinh
LOAD = ["1", USERS, EDGES]


def divider(char="═"):
    print(char * W)


def section(title):
    print()
    divider("═")
    print(f"  >> {title}")
    divider("═")


def run_test(label, inputs, timeout=30):
    """
    Chay ./SocialMedia voi stdin cho truoc.
    In TOAN BO stdout/stderr ra terminal (khong capture).
    PASS neu exit code == 0, FAIL neu crash / timeout.
    """
    global PASS_COUNT, FAIL_COUNT

    divider("─")
    print(f"  TEST : {label}")
    print(f"  INPUT: {' | '.join(repr(x) for x in inputs)}")
    divider("─")

    stdin_data = ("\n".join(inputs) + "\n").encode("utf-8")

    try:
        proc = subprocess.run(
            [BINARY],
            input=stdin_data,
            timeout=timeout,
            cwd=ROOT,
            # stdout / stderr KHONG bi capture → hien thi thang ra terminal
        )
        ok = (proc.returncode == 0)
    except subprocess.TimeoutExpired:
        print(f"\n[TIMEOUT] Qua {timeout}s!")
        ok = False
    except FileNotFoundError:
        print(f"\n[LOI] Khong tim thay binary '{BINARY}'. Hay chay 'make' truoc.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[LOI] {e}")
        ok = False

    result = "PASS" if ok else "FAIL"
    print(f"\n  --> {result} : {label}")
    PASS_COUNT += (1 if ok else 0)
    FAIL_COUNT += (0 if ok else 1)
    return ok


# ══════════════════════════════════════════════════════════════════════════════
divider("═")
print("  KIEM THU TU DONG – SOCIAL NETWORK BFS SIMULATION")
print(f"  Binary  : {BINARY}")
print(f"  Dataset : {USERS}  +  {EDGES}")
print(f"  Thu muc : {ROOT}")
divider("═")

# ── NHOM 1: TAI DU LIEU (Menu 1) ─────────────────────────────────────────────
section("NHOM 1 – TAI DU LIEU (Menu 1)")

run_test(
    "1a. Tai thanh cong dataset chinh",
    [*LOAD, "0"],
)

run_test(
    "1b. File khong ton tai → bao loi, khong crash",
    ["1", "khong_co.csv", "khong_co.txt", "0"],
)

# ── NHOM 2: THEM / XOA NGUOI DUNG (Menu 2, 4) ────────────────────────────────
section("NHOM 2 – THEM / XOA NGUOI DUNG (Menu 2, 4)")

run_test(
    "2a. Them nguoi dung moi (ID=99990, ten=TestUser)",
    [*LOAD, "2", "99990", "TestUser Moi", "0"],
)

run_test(
    "2b. Them nguoi dung trung ID → canh bao, khong crash",
    [*LOAD, "2", "1", "Nguoi Trung ID", "0"],
)

run_test(
    "2c. Them roi xoa nguoi dung (ID=99990)",
    [*LOAD, "2", "99990", "TestUser Moi", "4", "99990", "0"],
)

run_test(
    "2d. Xoa nguoi dung khong ton tai (ID=99999)",
    [*LOAD, "4", "99999", "0"],
)

# ── NHOM 3: THEM / XOA KET NOI (Menu 3, 5) ───────────────────────────────────
section("NHOM 3 – THEM / XOA KET NOI (Menu 3, 5)")

run_test(
    "3a. Them ket noi 2 user ton tai (1 <-> 2)",
    [*LOAD, "3", "1", "2", "0"],
)

run_test(
    "3b. Them ket noi voi user khong ton tai (1 <-> 99999)",
    [*LOAD, "3", "1", "99999", "0"],
)

run_test(
    "3c. Them ket noi ca 2 khong ton tai (88888 <-> 99999)",
    [*LOAD, "3", "88888", "99999", "0"],
)

run_test(
    "3d. Xoa ket noi ton tai (1 <-> 2)",
    [*LOAD, "3", "1", "2", "5", "1", "2", "0"],
)

run_test(
    "3e. Xoa ket noi khong ton tai (1 <-> 99999)",
    [*LOAD, "5", "1", "2", "0"],
)

# ── NHOM 4: DANH SACH & THONG TIN (Menu 6, 7) ────────────────────────────────
section("NHOM 4 – DANH SACH & THONG TIN NGUOI DUNG (Menu 6, 7)")

run_test(
    "4a. Hien thi danh sach nguoi dung (trang 1 roi thoat)",
    [*LOAD, "6", "", "0"],
)

run_test(
    "4b. Xem thong tin user ton tai (ID=1)",
    [*LOAD, "7", "1", "", "0"],
)

run_test(
    "4c. Xem thong tin user khong ton tai (ID=99999)",
    [*LOAD, "7", "99999", "0"],
)

# ── NHOM 5: TIM KIEM THEO TEN (Menu 8) ───────────────────────────────────────
section("NHOM 5 – TIM KIEM NGUOI DUNG THEO TEN (Menu 8)")

run_test(
    "5a. Tim kiem co ket qua ('Nguyen') → xem trang 1 roi thoat",
    [*LOAD, "8", "Nguyen", "", "0"],
)

run_test(
    "5b. Tim kiem khong co ket qua ('ZZZNOTEXIST')",
    [*LOAD, "8", "ZZZNOTEXIST", "0"],
)

run_test(
    "5c. Tim kiem chuoi rong → thong bao nhap tu khoa",
    [*LOAD, "8", "", "0"],
)

# ── NHOM 6: BAN BE TRUC TIEP (Menu 9) ────────────────────────────────────────
section("NHOM 6 – XEM BAN BE TRUC TIEP (Menu 9)")

run_test(
    "6a. Ban be truc tiep user co nhieu ban (ID=1) → trang 1 roi thoat",
    [*LOAD, "9", "1", "", "0"],
)

run_test(
    "6b. Ban be cua user khong ton tai (ID=99999)",
    [*LOAD, "9", "99999", "0"],
)

# ── NHOM 7: BFS – BAN CUA BAN (Menu 10) ──────────────────────────────────────
section("NHOM 7 – TIM BAN CUA BAN BFS (Menu 10)")

run_test(
    "7a. BFS user co nhieu ban (ID=1) → trang 1 roi thoat",
    [*LOAD, "10", "1", "", "0"],
)

run_test(
    "7b. BFS user khong ton tai (ID=99999)",
    [*LOAD, "10", "99999", "0"],
)

# ── NHOM 8: GOI Y KET BAN (Menu 11) ──────────────────────────────────────────
section("NHOM 8 – GOI Y KET BAN (Menu 11)")

run_test(
    "8a. Goi y ket ban binh thuong (ID=1, top 10)",
    [*LOAD, "11", "1", "10", "0"],
)

run_test(
    "8b. Goi y ket ban user khong ton tai (ID=99999)",
    [*LOAD, "11", "99999", "5", "0"],
)

# ── NHOM 9: THONG KE DO THI (Menu 12) ────────────────────────────────────────
section("NHOM 9 – THONG KE DO THI (Menu 12)")

run_test(
    "9a. In thong ke do thi (O(V+E))",
    [*LOAD, "12", "0"],
)

# ── NHOM 10: EXPORT KET QUA (Menu 13) ────────────────────────────────────────
section("NHOM 10 – EXPORT KET QUA RA FILE (Menu 13)")

run_test(
    "10a. Export goi y ket ban ra file (ID=1, top 10)",
    [*LOAD, "13", "1", "1", "10", "suggestions.txt", "0"],
)

run_test(
    "10b. Export thong ke do thi ra file",
    [*LOAD, "13", "2", "stats.txt", "0"],
)

run_test(
    "10c. Export thong tin & ban be user (ID=1)",
    [*LOAD, "13", "3", "1", "user_info.txt", "0"],
)

run_test(
    "10d. Export goi y ket ban voi user khong ton tai (ID=99999)",
    [*LOAD, "13", "1", "99999", "10", "suggestions_err.txt", "0"],
)

run_test(
    "10e. Export thong tin & ban be user khong ton tai (ID=99999)",
    [*LOAD, "13", "3", "99999", "user_err.txt", "0"],
)

run_test(
    "10f. Export menu → chon 0 quay lai",
    [*LOAD, "13", "0", "0"],
)

# ── NHOM 11: DO HIEU SUAT (Menu 14) ──────────────────────────────────────────
section("NHOM 11 – DO HIEU SUAT BENCHMARK (Menu 14)")

run_test(
    "11a. Chay toan bo benchmark tu dong (warm-up + do 10 lan/mau)",
    [*LOAD, "14", "0"],
    timeout=120,
)

# ── NHOM 12: XU LY LOI INPUT (Edge cases) ────────────────────────────────────
section("NHOM 12 – XU LY LOI INPUT")

run_test(
    "12a. Chon menu khong hop le (99) → thong bao, khong crash",
    [*LOAD, "99", "0"],
)

run_test(
    "12b. Chuoi ki tu dac biet o ten nguoi dung",
    [*LOAD, "2", "99991", "Nguyen @Test #2024!", "0"],
)

# ══════════════════════════════════════════════════════════════════════════════
# TONG KET
# ══════════════════════════════════════════════════════════════════════════════
total = PASS_COUNT + FAIL_COUNT
print()
divider("═")
print("  KET QUA TONG HOP")
divider("─")
print(f"  PASS : {PASS_COUNT}/{total}")
print(f"  FAIL : {FAIL_COUNT}/{total}")
if FAIL_COUNT == 0:
    print("  --> Toan bo test deu PASS! Chuong trinh hoat dong on dinh.")
else:
    print(f"  --> Co {FAIL_COUNT} test FAIL. Xem log phia tren.")
divider("═")
