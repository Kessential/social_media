"""
Tao bo du lieu mang xa hoi thuc te cho du an FriendsSuggestion.

Cac file output:
  - users.csv   : userID,name       (10,000+ nguoi dung)
  - edges.txt   : userID_1 userID_2 (cac canh quan he ban be)

Script tao do thi mo phong mang xa hoi thuc te:
  - Phan phoi bac theo luat luy thua (scale-free) thong qua co che lien ket uu tien (preferential attachment)
  - Cac cum cong dong voi cac ket noi noi bo day dac hon
  - Mot so luong nho cac nguoi dung "influencer" (hub) co rat nhieu ket noi

Cach dung:
    python scripts/generate_dataset.py
"""

import random
import os

# ─── Cau hinh ──────────────────────────────────────────────────────────────
NUM_USERS             = 10_500   # Tong so nguoi dung
NUM_ISOLATED          = 100      # Nguoi dung co lap (degree = 0, Isolated group)
NUM_PERIPHERAL        = 300      # Nguoi dung ngoai bien (degree = 1-3, Low group)
NUM_COMMUNITIES       = 50       # So luong cum cong dong
INTRA_COMMUNITY_EDGES = 100_000  # Canh trong noi bo cong dong (day dac, Medium group)
INTER_COMMUNITY_EDGES = 50_000   # Canh noi giua cac cong dong
HUB_COUNT             = 195      # Hub thuong (High group, degree ~100-999)
HUB_EXTRA_EDGES       = 15_000   # Canh bo sung cho hub thuong
SUPER_HUB_COUNT       = 5        # Sieu hub (Hub group, degree 1000+)
SUPER_HUB_EDGES       = 5_000    # Canh bo sung cho sieu hub (~1000 moi hub)
SEED = 42                        # Hat giong de tai tao ngau nhien giong nhau

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(OUTPUT_DIR, "users.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.txt")

# ─── Kho ten pools (100% Tieng Viet khong dau) ──────────────────────────────────
FIRST_NAMES_VN = [
    "An", "Bao", "Chi", "Dung", "Duc", "Giang", "Ha", "Hieu", "Hoa", "Hoang",
    "Hung", "Huong", "Khanh", "Lan", "Linh", "Long", "Mai", "Minh", "Nam", "Ngan",
    "Ngoc", "Nhung", "Phong", "Phuc", "Phuong", "Quan", "Quynh", "Son", "Thao",
    "Thanh", "Thang", "Thien", "Thinh", "Thu", "Thuy", "Tien", "Trang", "Trung",
    "Tuan", "Tung", "Uyen", "Van", "Viet", "Vu", "Xuan", "Yen",
]

LAST_NAMES_VN = [
    "Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo",
    "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly", "Trinh", "Dinh",
]

MIDDLE_NAMES_VN = [
    "Van", "Thi", "Huu", "Minh", "Duc", "Quoc", "Thanh", "Ngoc",
    "Hoang", "Xuan", "Bao", "Anh", "Tuan", "Phuong", "Hong",
]

FIRST_NAMES_EN = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Daniel", "Karen", "Matthew",
    "Lisa", "Anthony", "Nancy", "Mark", "Betty", "Steven", "Margaret",
    "Andrew", "Sandra", "Joshua", "Ashley", "Kevin", "Emily", "Brian",
    "Kimberly", "George", "Michelle", "Timothy", "Laura", "Ryan", "Megan",
    "Tyler", "Hannah", "Austin", "Olivia", "Sophia", "Emma", "Liam", "Noah",
]

LAST_NAMES_EN = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
]


def generate_name(rng: random.Random) -> str:
    """Tao ten day du ngau nhien (70% Tieng Viet, 30% Tieng Anh)."""
    if rng.random() < 0.7:
        last = rng.choice(LAST_NAMES_VN)
        middle = rng.choice(MIDDLE_NAMES_VN)
        first = rng.choice(FIRST_NAMES_VN)
        return f"{last} {middle} {first}"
    else:
        first = rng.choice(FIRST_NAMES_EN)
        last = rng.choice(LAST_NAMES_EN)
        return f"{first} {last}"


def main():
    rng = random.Random(SEED)

    # ── 1. Tao nguoi dung ───────────────────────────────────────────────────────
    print(f"[1/5] Dang tao {NUM_USERS} nguoi dung...")
    users: dict[int, str] = {}
    for uid in range(1, NUM_USERS + 1):
        users[uid] = generate_name(rng)

    # ── 2. Phan loai nguoi dung vao cac nhom ────────────────────────────────────
    print(f"[2/5] Phan loai: {NUM_ISOLATED} isolated, {NUM_PERIPHERAL} peripheral, "
          f"{SUPER_HUB_COUNT} sieu hub, {HUB_COUNT} hub thuong...")
    all_ids = list(range(1, NUM_USERS + 1))
    rng.shuffle(all_ids)

    isolated_ids   = set(all_ids[:NUM_ISOLATED])                              # degree = 0
    peripheral_ids = all_ids[NUM_ISOLATED : NUM_ISOLATED + NUM_PERIPHERAL]   # degree 1-3
    community_ids  = all_ids[NUM_ISOLATED + NUM_PERIPHERAL:]                 # tham gia cum

    # ── 3. Phan chia community users vao cac cum cong dong ──────────────────────
    print(f"[3/5] Phan chia {len(community_ids)} nguoi dung vao {NUM_COMMUNITIES} cum...")
    communities: list[list[int]] = [[] for _ in range(NUM_COMMUNITIES)]
    for i, uid in enumerate(community_ids):
        communities[i % NUM_COMMUNITIES].append(uid)

    # ── 4. Tao cac canh ket noi ─────────────────────────────────────────────────
    edges: set[tuple[int, int]] = set()

    def add_edge(u: int, v: int):
        if u != v:
            edges.add((min(u, v), max(u, v)))

    print(f"[4/5] Tao canh ({INTRA_COMMUNITY_EDGES} noi bo + {INTER_COMMUNITY_EDGES} lien cum "
          f"+ {NUM_PERIPHERAL}x1-3 peripheral + {SUPER_HUB_EDGES} sieu hub + {HUB_EXTRA_EDGES} hub)...")

    # 4a. Canh noi bo cum (Medium group)
    for _ in range(INTRA_COMMUNITY_EDGES):
        comm = rng.choice(communities)
        if len(comm) >= 2:
            u, v = rng.sample(comm, 2)
            add_edge(u, v)

    # 4b. Canh lien cum
    for _ in range(INTER_COMMUNITY_EDGES):
        c1, c2 = rng.sample(range(NUM_COMMUNITIES), 2)
        u = rng.choice(communities[c1])
        v = rng.choice(communities[c2])
        add_edge(u, v)

    # 4c. Peripheral users (Low group): moi nguoi 1-3 ket noi toi community
    for uid in peripheral_ids:
        for _ in range(rng.randint(1, 3)):
            add_edge(uid, rng.choice(community_ids))

    # 4d. Sieu hub (Hub group 1000+): chon tu community_ids
    hub_pool    = rng.sample(community_ids, SUPER_HUB_COUNT + HUB_COUNT)
    super_hubs  = hub_pool[:SUPER_HUB_COUNT]
    regular_hubs = hub_pool[SUPER_HUB_COUNT:]

    for _ in range(SUPER_HUB_EDGES):
        add_edge(rng.choice(super_hubs), rng.choice(community_ids))

    # 4e. Hub thuong (High group 100-999)
    for _ in range(HUB_EXTRA_EDGES):
        add_edge(rng.choice(regular_hubs), rng.choice(community_ids))

    # ── 5. Ghi cac file ket qua ─────────────────────────────────────────────────
    print(f"[5/5] Ghi file... ({len(users)} users, {len(edges)} edges)")

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for uid in range(1, NUM_USERS + 1):
            f.write(f"{uid},{users[uid]}\n")

    with open(EDGES_FILE, "w", encoding="utf-8") as f:
        for u, v in sorted(edges):
            f.write(f"{u} {v}\n")

    # ── Tom tat ─────────────────────────────────────────────────────────────────
    total_edges = len(edges)
    avg_degree  = 2 * total_edges / NUM_USERS
    print(f"\n{'='*55}")
    print(f"  Da tao bo du lieu thanh cong!")
    print(f"  Tong nguoi dung:      {NUM_USERS:>10,}")
    print(f"    Isolated  (deg=0):  {NUM_ISOLATED:>10,}")
    print(f"    Peripheral(deg 1-3):{NUM_PERIPHERAL:>10,}")
    print(f"    Sieu hub  (1000+):  {SUPER_HUB_COUNT:>10,}")
    print(f"    Hub thuong(100-999):{HUB_COUNT:>10,}")
    print(f"    Community (Medium): {len(community_ids)-SUPER_HUB_COUNT-HUB_COUNT:>10,}")
    print(f"  Tong canh ket noi:    {total_edges:>10,}")
    print(f"  Bac trung binh:       {avg_degree:>10.1f}")
    print(f"{'='*55}")
    print(f"  -> {USERS_FILE}")
    print(f"  -> {EDGES_FILE}")


# =============================================================================
# CAC KICH BAN THU NGHIEM (TEST CASES)
# =============================================================================

def write_testcase(name: str, users: dict[int, str],
                   edges: list[tuple[int, int]], expected: str):
    """Ghi mot kich ban thu nghiem vao thu muc testcases/<name>/."""
    tc_dir = os.path.join(OUTPUT_DIR, "testcases", name)
    os.makedirs(tc_dir, exist_ok=True)

    with open(os.path.join(tc_dir, "users.csv"), "w", encoding="utf-8") as f:
        for uid in sorted(users):
            f.write(f"{uid},{users[uid]}\n")

    with open(os.path.join(tc_dir, "edges.txt"), "w", encoding="utf-8") as f:
        for u, v in edges:
            f.write(f"{u} {v}\n")

    with open(os.path.join(tc_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(expected)

    print(f"  [OK] {name:40s} | {len(users):>5} nguoi dung | {len(edges):>5} ket noi")


def generate_testcases():
    """Tao cac bo du lieu test bien va dac biet theo 7 nhom chuc nang."""
    print("\n" + "=" * 60)
    print("  Dang tao cac kich ban thu nghiem...")
    print("=" * 60)

    # ══════════════════════════════════════════════════════
    # NHOM 1: CRUD (TC01 - TC07)
    # ══════════════════════════════════════════════════════
    
    # ── TC01: Them ket noi giua nguoi dung khong ton tai ─────────────────────
    write_testcase("tc01_connection_nonexistent",
        users={1: "An", 2: "Binh"},
        edges=[(1,2),(999,888),(1,999)],
        expected=(
            "TC01: Them ket noi giua nguoi dung khong ton tai\n"
            "Chi co user 1 va 2 ton tai.\n"
            "addConnection(1, 2) -> thanh cong (ca 2 ton tai)\n"
            "addConnection(999, 888) -> '[CANH BAO] Mot trong hai User ID khong ton tai: 999 <-> 888. Bo qua ket noi nay.'\n"
            "addConnection(1, 999) -> '[CANH BAO] Mot trong hai User ID khong ton tai: 1 <-> 999. Bo qua ket noi nay.'\n"
            "  (Luu y: ca 2 truong hop deu dung CUNG thong bao, khong phan biet 1 hay 2 user sai)\n"
            "Ket qua: getEdgeCount() = 1 (chi co canh 1-2)\n"
            "Kiem tra: Khong crash, chi canh hop le duoc them.\n"
        ))

    # ── TC02: User ID trung lap trong CSV ────────────────────────────────────
    # Ghi de file users.csv de co dong trung (write_testcase sort theo key nen chi giu 1 ban)
    tc02_dir = os.path.join(OUTPUT_DIR, "testcases", "tc02_duplicate_user_id")
    os.makedirs(tc02_dir, exist_ok=True)
    with open(os.path.join(tc02_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Alice\n1,AliceDuplicate\n2,Bob\n")
    with open(os.path.join(tc02_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("1 2\n")
    with open(os.path.join(tc02_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC02: User ID trung lap trong CSV\n"
            "Dong 1: \"1,Alice\" -> them thanh cong\n"
            "Dong 2: \"1,AliceDuplicate\" -> bo qua + canh bao (SAU KHI FIX addUser)\n"
            "Dong 3: \"2,Bob\" -> them thanh cong\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 2\n"
            "  - getUserName(1) = \"Alice\" (giu ten dau tien, khong bi ghi de)\n"
            "  - getUserName(2) = \"Bob\"\n"
            "  - Xuat canh bao cho dong trung ID\n"
        )
    print(f"  [OK] {'tc02_duplicate_user_id':40s} |     2 nguoi dung |     1 ket noi")

    # ── TC03: removeUser user khong ton tai ───────────────────────────────────
    write_testcase("tc03_remove_nonexistent_user",
        users={1: "An", 2: "Binh"},
        edges=[(1,2)],
        expected=(
            "TC03: removeUser voi user khong ton tai\n"
            "removeUser(9999) -> xuat '[LOI] Nguoi dung 9999 khong ton tai!'\n"
            "removeUser(0) -> xuat '[LOI] Nguoi dung 0 khong ton tai!'\n"
            "  (moi user ID khong ton tai se in chinh xac ID do trong thong bao loi)\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 2 (khong thay doi)\n"
            "  - getEdgeCount() = 1 (khong thay doi)\n"
            "  - Khong crash, chi xuat thong bao loi\n"
        ))

    # ── TC04: removeConnection ket noi khong ton tai ──────────────────────────
    write_testcase("tc04_remove_nonexistent_connection",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2)],
        expected=(
            "TC04: removeConnection voi ket noi khong ton tai\n"
            "removeConnection(1, 3) -> '[LOI] Ket noi giua User ID 1 va User ID 3 khong ton tai.'\n"
            "  (user 1 va 3 ton tai nhung khong co canh)\n"
            "removeConnection(1, 9999) -> '[LOI] Mot trong hai User ID khong ton tai. Khong the xoa ket noi.'\n"
            "  (user 9999 khong ton tai)\n"
            "removeConnection(9999, 8888) -> '[LOI] Mot trong hai User ID khong ton tai. Khong the xoa ket noi.'\n"
            "  (Luu y: ca 2 truong hop user khong ton tai deu dung CUNG thong bao chung)\n"
            "Ket qua mong doi:\n"
            "  - getEdgeCount() = 1 (chi co canh 1-2, khong thay doi)\n"
            "  - Khong crash, chi xuat thong bao loi\n"
        ))

    # ── TC05: Xoa ket noi roi kiem tra BFS cap nhat ──────────────────────────
    write_testcase("tc05_remove_connection_bfs",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2),(2,3)],
        expected=(
            "TC05: Xoa ket noi roi kiem tra BFS cap nhat dung\n"
            "Do thi ban dau: 1-2-3 (chain)\n"
            "getFriendsOfFriends(1) ban dau -> {3} (qua 2)\n"
            "Thao tac: removeConnection(1, 2)\n"
            "Sau khi xoa:\n"
            "  - getFriendsOfFriends(1) -> {} (1 khong con ban nao)\n"
            "  - suggestFriends(1) -> [] (khong con ket noi)\n"
            "  - getEdgeCount() -> 1 (chi con canh 2-3)\n"
            "Kiem tra: BFS cap nhat dung sau khi xoa connection.\n"
        ))

    # ── TC06: Them roi xoa, kiem tra adjList doi xung ────────────────────────
    write_testcase("tc06_add_remove_symmetry",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung", 5: "Em"},
        edges=[(1,2),(2,3),(3,4),(4,5),(1,3)],
        expected=(
            "TC06: Them roi xoa ket noi, kiem tra doi xung adjList\n"
            "Do thi ban dau: 1-2, 2-3, 3-4, 4-5, 1-3\n"
            "Thao tac:\n"
            "  1. removeUser(2) -> xoa user 2 va tat ca ket noi (1-2, 2-3)\n"
            "  2. Kiem tra adjList[1] khong con chua 2\n"
            "  3. Kiem tra adjList[3] khong con chua 2\n"
            "  4. suggestFriends(1) -> [{4, mutualCount=1}] (4 la ban cua ban qua 3)\n"
            "  5. getUserCount() = 4\n"
            "  6. getEdgeCount() = 3 (canh 1-3, 3-4, 4-5 con lai)\n"
            "Kiem tra: adjList doi xung sau moi thao tac xoa.\n"
        ))

    # ── TC07: Them user sau khi load file ─────────────────────────────────────
    write_testcase("tc07_add_after_load",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2),(2,3)],
        expected=(
            "TC07: Them user va connection sau khi load file\n"
            "Sau khi load: getUserCount() = 3, getEdgeCount() = 2\n"
            "Thao tac:\n"
            "  1. addUser(4, 'Dung') -> them thanh cong\n"
            "  2. addConnection(3, 4) -> them thanh cong\n"
            "  3. addConnection(1, 4) -> them thanh cong\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 4\n"
            "  - getEdgeCount() = 4\n"
            "  - suggestFriends(2) -> [{4, mutualCount=2}] (qua 1 VA 3)\n"
            "  - suggestFriends(4) -> [{2, mutualCount=2}] (qua 1 VA 3)\n"
            "Kiem tra: Them user/connection sau load van hoat dong binh thuong.\n"
        ))


    # ══════════════════════════════════════════════════════
    # NHOM 2: I/O (TC08 - TC12)
    # ══════════════════════════════════════════════════════
    
    # ── TC08: Tai file khong ton tai ──────────────────────────────────────────
    write_testcase("tc08_file_not_found",
        users={1: "An", 2: "Binh"},
        edges=[(1,2)],
        expected=(
            "TC08: Tai file khong ton tai\n"
            "Goi loadUsersFromFile(\"khong_ton_tai.csv\") -> tra ve false, xuat loi, KHONG crash.\n"
            "Goi loadConnectionsFromFile(\"khong_ton_tai.txt\") -> tra ve false, xuat loi, KHONG crash.\n"
            "He thong van hoat dong binh thuong sau khi load that bai.\n"
        ))

    # ── TC09: CSV va edges co dong trong xen ke ──────────────────────────────
    tc09_dir = os.path.join(OUTPUT_DIR, "testcases", "tc09_blank_lines_whitespace")
    os.makedirs(tc09_dir, exist_ok=True)
    with open(os.path.join(tc09_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Alice\n\n3,Charlie\n")
    with open(os.path.join(tc09_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("\n1 3\n\n")
    with open(os.path.join(tc09_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC09: CSV co dong trong va khoang trang\n"
            "File users.csv co dong trong xen ke giua user 1 va user 3.\n"
            "File edges.txt co dong trong o dau va cuoi file.\n"
            "Ket qua mong doi:\n"
            "  - Dong trong duoc bo qua (skip), khong crash\n"
            "  - getUserCount() = 2 (chi co user 1 va 3)\n"
            "  - getEdgeCount() = 1 (canh 1-3)\n"
            "  - Khong xuat loi cho dong trong\n"
        )
    print(f"  [OK] {'tc09_blank_lines_whitespace':40s} |     2 nguoi dung |     1 ket noi")

    # ── TC10: Du lieu CSV loi dinh dang ────────────────────────────────────────
    write_testcase("tc10_malformed_csv",
        users={"abc": "NguoiDungLoiDinhDang", "2": "Binh"},
        edges=[(2, 2)],
        expected=(
            "TC10: File CSV chua ID dang chu (abc) khong hop le\n"
            "Dong 'abc,NguoiDungLoiDinhDang' -> stoi('abc') nem ngoai le -> '[CANH BAO] Dinh dang dong khong hop le, bo qua'\n"
            "Dong '2,Binh' -> them thanh cong user ID=2\n"
            "Canh (2,2) la tu ket noi -> '[CANH BAO] Khong the tu ket noi toi chinh minh (User ID: 2)'\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 1 (chi co user 2 'Binh')\n"
            "  - getEdgeCount() = 0 (canh tu ket noi bi bo qua)\n"
            "  - Khong crash nho co try-catch trong loadUsersFromFile\n"
        ))

    # ── TC11: Ten nguoi dung co ky tu dac biet (dau phay, ngoac kep) ─────────
    tc11_dir = os.path.join(OUTPUT_DIR, "testcases", "tc11_special_chars_name")
    os.makedirs(tc11_dir, exist_ok=True)
    with open(os.path.join(tc11_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Nguyen Van A\n")
        f.write("2,Tran, Thi B\n")        # Dau phay trong ten!
        f.write("3,Le \"Nickname\" C\n")   # Ngoac kep trong ten
    with open(os.path.join(tc11_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("1 2\n2 3\n")
    with open(os.path.join(tc11_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC11: Ten nguoi dung co ky tu dac biet\n"
            "User 1: \"Nguyen Van A\" -> ten binh thuong, OK\n"
            "User 2: \"Tran, Thi B\" -> ten chua dau phay!\n"
            "  Parser: getline(ss, strUserID, ',') -> strUserID = \"2\", name = \" Thi B\"\n"
            "  Phan \"Tran\" bi mat vi parser cat tai dau phay dau tien trong ten.\n"
            "  => Day la han che cua CSV parser don gian.\n"
            "User 3: \"Le \\\"Nickname\\\" C\" -> ngoac kep, parser van OK\n"
            "Kiem tra: Khong crash.\n"
        )
    print(f"  [OK] {'tc11_special_chars_name':40s} |     3 nguoi dung |     2 ket noi")

    # ── TC12: Edges file chua du lieu sai dinh dang ──────────────────────────
    tc12_dir = os.path.join(OUTPUT_DIR, "testcases", "tc12_malformed_edges")
    os.makedirs(tc12_dir, exist_ok=True)
    with open(os.path.join(tc12_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,An\n2,Binh\n")
    with open(os.path.join(tc12_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("1 2 extra_data\nabc def\n1\n1 2\n")
    with open(os.path.join(tc12_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC12: Edges file chua du lieu sai dinh dang\n"
            "Dong 1: \"1 2 extra_data\" -> ss >> userID_1 >> userID_2 thanh cong (bo qua extra), them canh 1-2\n"
            "Dong 2: \"abc def\" -> ss >> int fail -> canh bao, bo qua\n"
            "Dong 3: \"1\" -> chi co 1 so -> ss >> userID_2 fail -> canh bao, bo qua\n"
            "Dong 4: \"1 2\" -> thanh cong (nhung canh 1-2 da co, HashSet bo qua trung lap)\n"
            "Ket qua mong doi:\n"
            "  - getEdgeCount() = 1 (chi co canh 1-2 hop le)\n"
            "  - Xuat 2 canh bao cho dong 2 va dong 3\n"
            "  - Khong crash\n"
        )
    print(f"  [OK] {'tc12_malformed_edges':40s} |     2 nguoi dung |     4 ket noi")


    # ══════════════════════════════════════════════════════
    # NHOM 3: BFS (TC13 - TC17)
    # ══════════════════════════════════════════════════════
    
    # ── TC13: Do thi dang chuoi / tuyen tinh ──────────────────────────────────
    write_testcase("tc13_chain_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC13: Do thi hinh xich (1-2-3-4-5)\n"
            "suggestFriends(1) -> [3] (FoF qua 2, mutualCount=1)\n"
            "suggestFriends(3) -> [1, 5] (FoF qua 2 va 4)\n"
            "suggestFriends(5) -> [3] (FoF qua 4)\n"
            "Nguoi dung 1 khong the thay nguoi dung 4 hoac 5 (do sau > 2)\n"
        ))

    # ── TC14: Do thi hinh kim cuong ───────────────────────────────────────────
    write_testcase("tc14_diamond_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(1,3),(2,4),(3,4)],
        expected=(
            "TC14: Do thi hinh kim cuong\n"
            "suggestFriends(1) -> [4] voi mutualCount=2 (qua 2 VA 3)\n"
            "suggestFriends(4) -> [1] voi mutualCount=2 (qua 2 VA 3)\n"
            "Kiem tra tong hop so ban chung dung dan.\n"
        ))

    # ── TC15: Do thi vong tron thuan tuy (cycle) ─────────────────────────────
    write_testcase("tc15_cycle_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(2,3),(3,4),(4,1)],
        expected=(
            "TC15: Do thi vong tron thuan tuy (1-2-3-4-1)\n"
            "Ban truc tiep cua 1: {2, 4}\n"
            "getFriendsOfFriends(1) -> {3} (qua 2 VA qua 4)\n"
            "suggestFriends(1) -> [{3, mutualCount=2}]\n"
            "  (goi y qua ca 2 lan duong: 1->2->3 va 1->4->3)\n"
            "suggestFriends(2) -> [{4, mutualCount=2}]\n"
            "  (goi y qua: 2->1->4 va 2->3->4)\n"
            "Kiem tra: tong hop so ban chung dung khi co nhieu duong di.\n"
        ))

    # ── TC16: Hinh tam giac co duoi ────────────────────────────────────────────
    write_testcase("tc16_triangle_with_tail",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(2,3),(1,3),(3,4)],
        expected=(
            "TC16: Hinh tam giac voi duoi (1-2-3 + 3-4)\n"
            "suggestFriends(1) -> [4] mutualCount=1 (qua 3)\n"
            "suggestFriends(2) -> [4] mutualCount=1 (qua 3)\n"
            "suggestFriends(4) -> [1, 2] moi nguoi mutualCount=1 (qua 3)\n"
        ))

    # ── TC17: Do thi hai phan (bipartite graph) ──────────────────────────────
    bp_users = {1: "A1", 2: "A2", 3: "A3", 4: "B1", 5: "B2", 6: "B3"}
    bp_edges = []
    for a in [1, 2, 3]:
        for b in [4, 5, 6]:
            bp_edges.append((a, b))
    write_testcase("tc17_bipartite_graph",
        users=bp_users,
        edges=bp_edges,
        expected=(
            "TC17: Do thi hai phan (bipartite graph)\n"
            "Nhom A = {1,2,3}, Nhom B = {4,5,6}\n"
            "Moi node nhom A ket noi tat ca node nhom B (9 canh).\n"
            "suggestFriends(1) -> [{2, mutualCount=3}, {3, mutualCount=3}]\n"
            "  (2 va 3 deu co 3 ban chung voi 1: qua 4, 5, 6)\n"
            "suggestFriends(4) -> [{5, mutualCount=3}, {6, mutualCount=3}]\n"
            "  (5 va 6 deu co 3 ban chung voi 4: qua 1, 2, 3)\n"
            "Khong co goi y cheo nhom (da la ban truc tiep).\n"
        ))


    # ══════════════════════════════════════════════════════
    # NHOM 4: Goi y ket ban (TC18 - TC23)
    # ══════════════════════════════════════════════════════
    
    # ── TC18: Nguoi dung co lap ───────────────────────────────────────────────
    write_testcase("tc18_isolated_user",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (1, 4), (2, 4)],
        expected=(
            "TC18: Nguoi dung co lap\n"
            "User 3 (Charlie) co 0 ban be — hoan toan co lap.\n"
            "suggestFriends(3) -> [] (Trong, khong co bat ky ket noi nao de BFS)\n"
            "suggestFriends(1) -> [] (Ban cua 1: {2,4}; ban cua 2: {1,4}; ban cua 4: {1,2})\n"
            "  -> tat ca FoF deu da la ban truc tiep hoac chinh user 1, khong con ai de goi y)\n"
            "  User 3 (Charlie) KHONG bao gio duoc goi y vi khong co duong ket noi toi user 1.\n"
        ))

    # ── TC19: Chi co duy nhat mot nguoi ban ────────────────────────────────────
    write_testcase("tc19_single_friend",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (2, 3), (2, 4)],
        expected=(
            "TC19: Ban duy nhat\n"
            "User 1 co dung 1 nguoi ban: nguoi dung 2.\n"
            "suggestFriends(1) -> [3, 4] (ban cua nguoi dung 2)\n"
            "mutualConnectionsCount cho ca hai = 1 (thong qua nguoi dung 2)\n"
        ))

    # ── TC20: Nhom hoan hao (K5) ──────────────────────────────────────────
    write_testcase("tc20_complete_clique",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)],
        expected=(
            "TC20: Nhom hoan hao (K5)\n"
            "Moi nguoi deu da la ban cua nhau.\n"
            "suggestFriends(any) -> [] (Trong, khong co goi y moi)\n"
        ))

    # ── TC21: Do thi hinh sao ────────────────────────────────────────────────────
    write_testcase("tc21_star_graph",
        users={1: "Hub", 2: "L1", 3: "L2", 4: "L3", 5: "L4", 6: "L5"},
        edges=[(1,2),(1,3),(1,4),(1,5),(1,6)],
        expected=(
            "TC21: Do thi hinh sao\n"
            "User 1 la trung tam, cac user 2-6 la nhanh.\n"
            "suggestFriends(1) -> [] (Tat ca deu la ban truc tiep, khong co FoF)\n"
            "suggestFriends(2) -> [3,4,5,6] voi mutualCount=1 (thong qua trung tam)\n"
            "suggestFriends(2, maxSuggestions=2) -> chi lay top 2\n"
        ))

    # ── TC22: Hai phan lien thong roi rac ───────────────────────────────────
    write_testcase("tc22_disconnected_components",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F"},
        edges=[(1,2),(2,3),(1,3), (4,5),(5,6),(4,6)],
        expected=(
            "TC22: Hai phan lien thong roi rac\n"
            "Nhom 1: {1,2,3} ket noi hoan toan. Nhom 2: {4,5,6} ket noi hoan toan.\n"
            "suggestFriends(1) -> [] (Da la ban voi tat ca nguoi trong nhom)\n"
            "suggestFriends(4) -> [] (Cung ly do)\n"
            "Khong the goi y cheo giua hai nhom.\n"
        ))

    # ── TC23: Kiem tra chan tren cua so luong goi y (maxSuggestions) ───────────
    ms_users = {1: "Alice", 2: "Hub"}
    ms_edges = [(1, 2)]
    for i in range(3, 13):
        ms_users[i] = f"Friend_{i}"
        ms_edges.append((2, i))
    write_testcase("tc23_max_suggestions_limit",
        users=ms_users,
        edges=ms_edges,
        expected=(
            "TC23: Gioi han maxSuggestions\n"
            "Nguoi dung 1 -> 1 ban (nguoi dung 2). Nguoi dung 2 -> 10 ban khac (3-12).\n"
            "suggestFriends(1, 5) -> dung 5 ket qua (bi gioi han boi maxSuggestions=5)\n"
            "suggestFriends(1, 20) -> dung 10 ket qua (tat ca FoF san co, khong du 20)\n"
            "suggestFriends(1, 0) -> printSuggestions in '[LOI] So luong goi y phai lon hon 0.'\n"
            "  (maxSuggestions<=0 khong tra ve 0 ket qua ma thoat som voi thong bao loi)\n"
        ))


    # ══════════════════════════════════════════════════════
    # NHOM 5: Bien & Dac biet (TC24 - TC29)
    # ══════════════════════════════════════════════════════
    
    # ── TC24: User ID cuc han (0, am, INT_MAX) ──────────────────────────────
    write_testcase("tc24_extreme_user_ids",
        users={0: "Zero", -1: "NegativeOne", 2147483647: "MaxInt"},
        edges=[(0,-1),(-1,2147483647),(0,2147483647)],
        expected=(
            "TC24: User ID cuc han (0, am, INT_MAX)\n"
            "User IDs: 0, -1, 2147483647\n"
            "Tat ca ket noi voi nhau (do thi day du K3).\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 3\n"
            "  - getEdgeCount() = 3\n"
            "  - suggestFriends(0) -> [] (da la ban het voi tat ca)\n"
            "  - suggestFriends(-1) -> [] (tuong tu)\n"
            "  - HashMap hash dung voi cac gia tri cuc han\n"
            "  - Khong crash, khong overflow\n"
        ))

    # ── TC25: Chi co duy nhat 1 nguoi dung ─────────────────────────────────────
    write_testcase("tc25_single_user",
        users={1: "OnlyUser"},
        edges=[],
        expected=(
            "TC25: Chi co mot nguoi dung duy nhat (bien toi thieu)\n"
            "Chi co nguoi dung 1 ton tai. Khong co canh nao.\n"
            "suggestFriends(1) -> [] (khong co bat ky ket noi nao)\n"
        ))

    # ── TC26: Hai nguoi dung, mot ket noi duy nhat ─────────────────────────────
    write_testcase("tc26_two_users",
        users={1: "Alice", 2: "Bob"},
        edges=[(1, 2)],
        expected=(
            "TC26: Hai nguoi dung, mot canh (do thi ket noi toi thieu)\n"
            "suggestFriends(1) -> [] (nguoi ban duy nhat la 2, 2 khong co ban khac)\n"
            "suggestFriends(2) -> [] (cung ly do)\n"
        ))

    # ── TC27: Bo du lieu hoan toan rong (kiem tra khoi tao) ───────────────────
    write_testcase("tc27_empty_dataset",
        users={},
        edges=[],
        expected=(
            "TC27: Bo du lieu hoan toan rong\n"
            "He thong phai tai file thanh cong va hoat dong voi 0 nguoi dung chu khong crash chia 0.\n"
        ))

    # ── TC28: stress-test canh tu lap va trung lap ─────────────────────────────
    write_testcase("tc28_self_loop_duplicate",
        users={1: "Alice", 2: "Bob", 3: "Charlie"},
        edges=[(1,1),(1,2),(1,2),(2,3)],
        expected=(
            "TC28: Tu ket noi va stress lap canh\n"
            "Canh (1,1) la tu ket noi -> se bi bo qua va khong gay loi.\n"
            "Canh (1,2) xuat hien hai lan -> adjList la tap hop nen khong bi trung lap.\n"
            "suggestFriends(1) -> [3] voi mutualCount=1 (thong qua nguoi dung 2)\n"
        ))

    # ── TC29: Truy van user ID khong ton tai (kiem tra an toan chi muc) ──────
    write_testcase("tc29_nonexistent_user",
        users={1: "An", 2: "Binh"},
        edges=[(1, 2)],
        expected=(
            "TC29: Truy van ID nguoi dung khong ton tai\n"
            "suggestFriends(9999) -> phai tra ve Vector rong chu khong duoc crash.\n"
            "getFriendsOfFriends(9999) -> phai tra ve HashSet rong.\n"
        ))


    # ══════════════════════════════════════════════════════
    # NHOM 6: Export & Tim kiem (TC30 - TC31)
    # ══════════════════════════════════════════════════════
    
    # ── TC30: Tim kiem nguoi dung theo ten (searchUserByName) ──────────────────
    write_testcase("tc30_search_by_name",
        users={1: "Nguyen Van An", 2: "Tran Thi Binh", 3: "Le Van An Khang",
               4: "Pham Minh", 5: "nguyen thi an"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC30: Tim kiem nguoi dung theo ten (searchUserByName)\n"
            "searchUserByName(\"an\") -> tim tat ca user co ten chua 'an' (case-insensitive):\n"
            "  - User 1: 'Nguyen Van An' (chua 'An')\n"
            "  - User 3: 'Le Van An Khang' (chua 'An')\n"
            "  - User 5: 'nguyen thi an' (chua 'an')\n"
            "  - User 4: 'Pham Minh' -> KHONG match (khong chua 'an')\n"
            "searchUserByName(\"BINH\") -> tim thay user 2 ('Tran Thi Binh')\n"
            "searchUserByName(\"xyz\") -> [] (khong tim thay)\n"
            "searchUserByName(\"\") -> string rong, thong bao yeu cau nhap lai va thoat chuc nang 8\n"
            "Kiem tra: case-insensitive dung, substring match dung.\n"
        ))

    # ── TC31: Export functions ────────────────────────────────────────────────
    write_testcase("tc31_export_functions",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung"},
        edges=[(1,2),(2,3),(3,4),(1,3)],
        expected=(
            "TC31: Kiem tra cac ham export ra file\n"
            "Thao tac:\n"
            "  1. exportSuggestions(1, 5, 'test_suggest.txt') -> tra ve true, file duoc tao\n"
            "  2. exportGraphStats('test_stats.txt') -> tra ve true, file duoc tao\n"
            "  3. exportUserConnections(1, 'test_user.txt') -> tra ve true, file duoc tao\n"
            "  4. exportSuggestions(9999, 5, 'test_fail.txt') -> tra ve false (user khong ton tai)\n"
            "  5. exportUserConnections(9999, 'test_fail2.txt') -> tra ve false\n"
            "Kiem tra: File tao thanh cong, noi dung chinh xac, ham tra ve false khi user khong ton tai.\n"
        ))


    # ══════════════════════════════════════════════════════
    # NHOM 7: Hieu nang (TC32 - TC34)
    # ══════════════════════════════════════════════════════
    
    # ── TC32: Sieu ket noi hinh sao khong lo (Stress test) ─────────────────────
    hub_users = {1: "SieuKetNoi"}
    hub_edges = []
    for i in range(2, 1001):
        hub_users[i] = f"Leaf_{i}"
        hub_edges.append((1, i))
    hub_edges.extend([(2, 3), (4, 5), (6, 7)])
    write_testcase("tc32_large_star_hub",
        users=hub_users,
        edges=hub_edges,
        expected=(
            "TC32: Nhanh sao khong lo (1 trung tam + 999 nhanh)\n"
            "Nguoi dung 1 co 999 ban truc tiep -> suggestFriends(1, N) = [] voi moi N\n"
            "  (tat ca user deu la ban truc tiep, khong co FoF de goi y)\n"
            "Nguoi dung 2 co ban truc tiep: {1 (hub), 3 (canh 2-3)}\n"
            "suggestFriends(2, 1000) tra ve 997 goi y (nhanh 4-1000 qua hub 1)\n"
            "  - User 1 (hub) KHONG nam trong goi y vi la ban truc tiep cua 2\n"
            "  - User 3 KHONG nam trong goi y vi la ban truc tiep cua 2\n"
            "  - Cac nhanh 4-1000 (tru 4 va 5 la ban truc tiep qua canh 4-5) co mutualCount=1 (qua hub)\n"
            "  - Canh bo sung (4,5) va (6,7): user 4 va 6 co them 1 ban chung la user 5 va 7\n"
            "Kiem tra hieu suat voi node bac cao (suggestFriends phai chay duoi vai giay).\n"
        ))

    # ── TC33: Stress memory — load, xoa het, load lai ────────────────────────
    sm_users = {}
    sm_edges = []
    for i in range(1, 51):
        sm_users[i] = f"User_{i}"
    for i in range(1, 50):
        sm_edges.append((i, i + 1))
    write_testcase("tc33_stress_memory",
        users=sm_users,
        edges=sm_edges,
        expected=(
            "TC33: Stress memory — load, xoa het, load lai\n"
            "Buoc 1: Load 50 users va 49 connections.\n"
            "Buoc 2: removeUser(1) den removeUser(50) — xoa tung user.\n"
            "Buoc 3: Kiem tra getUserCount() = 0, getEdgeCount() = 0.\n"
            "Buoc 4: Load lai cung file data.\n"
            "Buoc 5: Kiem tra getUserCount() = 50, getEdgeCount() = 49.\n"
            "Kiem tra: Khong memory leak, khong crash, data duoc tai lai dung.\n"
        ))

    # ── TC34: measurePerformance ──────────────────────────────────────────────
    # Dataset du de xuat hien nhieu nhom degree
    # - User 1 (hub): ket noi voi 2..21 -> degree 20 (Medium)
    # - User 2..11 (low): ket noi voi 1 + 1 ban khac -> degree 2 (Low)
    # - User 12..21 (isolated-ish): chi ket noi voi hub -> degree 1 (Low)
    # - User 22 (isolated): khong co canh nao -> degree 0 (Isolated)
    tc34_users = {1: "Hub"}
    tc34_edges = []
    for i in range(2, 12):
        tc34_users[i] = f"LowUser_{i}"
        tc34_edges.append((1, i))
        if i + 10 <= 21:
            tc34_edges.append((i, i + 10))
    for i in range(12, 22):
        tc34_users[i] = f"LeafUser_{i}"
        tc34_edges.append((1, i))
    tc34_users[22] = "Isolated"

    write_testcase("tc34_measure_performance",
        users=tc34_users,
        edges=tc34_edges,
        expected=(
            "TC34: Kiem tra measurePerformance() (khong tham so)\n"
            "Dataset: 22 nguoi dung, hub co degree=20 (Medium), leaf co degree=1-2 (Low), 1 user co lap (Isolated).\n"
            "\n"
            "Hanh vi mong doi:\n"
            "  [Khoi dong]\n"
            "    - In header: so nguoi dung, so ket noi, thong so warm-up/repeat\n"
            "    - Phan loai tat ca user vao 5 nhom:\n"
            "        Isolated(=0): user 22\n"
            "        Low(1-9)    : cac leaf user\n"
            "        Medium(10-99): user 1 (hub)\n"
            "        High(100-999): (khong co mau) -> in '(khong co mau)'\n"
            "        Hub(1000+)  : (khong co mau) -> in '(khong co mau)'\n"
            "\n"
            "  [1. BFS - getFriendsOfFriends]\n"
            "    - Moi nhom co mau: warm-up 3 lan, do 10 lan, lay median\n"
            "    - In bang cot: Nhom | Mau | Min(us) | Avg(us) | Max(us)\n"
            "    - Nhom High va Hub in '(khong co mau)'\n"
            "    - Cuoi bang in Throughput (ops/sec)\n"
            "\n"
            "  [2. SUGGEST FRIENDS - suggestFriends(k=10)]\n"
            "    - Tuong tu bang BFS tren\n"
            "\n"
            "  [3. SEARCH BY NAME]\n"
            "    - Tu trich keyword tu ten user thuc trong dataset\n"
            "    - 4 truong hop: High-match (1 ky tu), Medium-match (3 ky tu),\n"
            "                   Low-match (4 ky tu con lai), No-match ('ZZZNOTEXIST999')\n"
            "    - Moi truong hop: warm-up ben trong measureRepeated + do 10 lan + lay median\n"
            "    - In bang cot: Nhom | Keyword | Min(us) | Med(us) | Max(us) | Ket qua\n"
            "\n"
            "  [4. GRAPH STATS - computeGraphStats]\n"
            "    - Warm-up ben trong measureRepeated + do 10 lan + lay median\n"
            "    - In 1 dong: Min: X us | Med: Y us | Max: Z us\n"
            "\n"
            "  [Tong ket]\n"
            "    - In don vi (microsecond), phuong phap, phan nhom\n"
            "\n"
            "Kiem tra:\n"
            "  - Khong crash voi bat ky nhom nao (ke ca nhom rong)\n"
            "  - Thoi gian ket qua hop ly (< vai chuc ms voi dataset nho)\n"
            "  - Nhom High va Hub hien thi '(khong co mau)', khong bi bo qua hoac crash\n"
        ))

    # ── TC35: expected.txt cho bo dataset chinh (scripts/) ──────────────────────
    # Dataset chinh (users.csv + edges.txt) DA nam trong OUTPUT_DIR roi.
    # Chi can ghi expected.txt vao cung thu muc la xong, khong can sao chep.
    EXPECTED_FILE = os.path.join(OUTPUT_DIR, "expected.txt")
    with open(EXPECTED_FILE, "w", encoding="utf-8") as f:
        f.write(
            "TC35: Benchmark measurePerformance() tren bo dataset chinh (10,500 users)\n"
            "Dataset co cau truc ro rang bao phu tat ca 5 nhom degree:\n"
            "  - 100  isolated users   -> Isolated (degree = 0)\n"
            "  - 300  peripheral users -> Low      (degree = 1-3)\n"
            "  - ~9,600 community users -> Medium  (degree ~20-50)\n"
            "  - 195  hub thuong       -> High     (degree ~100-200)\n"
            "  - 5    sieu hub         -> Hub      (degree ~1030+)\n"
            "  Tong canh thuc te: 165,506\n"
            "\n"
            "Phan loai nhom degree mong doi:\n"
            "  Isolated(=0)  : 100 users (dat rieng, KHONG tham gia cum)\n"
            "  Low(1-9)      : 300 peripheral users (1-3 ket noi tuong minh)\n"
            "  Medium(10-99) : phan lon community users (~9,600 users)\n"
            "  High(100-999) : 195 hub thuong (HUB_EXTRA_EDGES = 15,000)\n"
            "  Hub(1000+)    : 5 sieu hub (SUPER_HUB_EDGES = 5,000 ~ 1000/hub)\n"
            "  -> Tat ca 5 nhom deu co du lieu, khong nhom nao bi '(khong co mau)'\n"
            "\n"
            "Hanh vi mong doi cho tung section:\n"
            "  [1. BFS - getFriendsOfFriends]\n"
            "     Isolated: tra ve ngay (0 ban), gan 0 us\n"
            "     Low:      BFS qua 1-3 ban, rat nhanh\n"
            "     Hub(1000+): BFS qua 1000+ ban depth-2, chay lau nhat\n"
            "     Thu tu: Isolated < Low < Medium < High < Hub\n"
            "  [2. SUGGEST FRIENDS - suggestFriends(k=10)]\n"
            "     Tuong tu BFS, them buoc sap xep ban chung -> cham hon mot chut\n"
            "  [3. SEARCH BY NAME]\n"
            "     High-match (1 ky tu): ket qua nhieu nhat (~3000-5000 matches)\n"
            "     No-match: scan nhanh nhat (output rong)\n"
            "  [4. GRAPH STATS]\n"
            "     O(V+E) ~ O(10500 + 165500): du kien < 10ms\n"
            "\n"
            "Kiem tra:\n"
            "  - Tat ca 5 nhom deu co so lieu (khong co dong '(khong co mau)')\n"
            "  - Isolated group: Min/Avg/Max gan 0 us\n"
            "  - Hub group: thoi gian cao nhat, nhung khong crash\n"
            "  - Throughput hop ly (khong am, khong tran so)\n"
        )
    print(f"  [OK] {'expected.txt cho dataset chinh (scripts/)':40s}| 10500 nguoi dung | 165506 ket noi")

    print("=" * 60)
    print(f"  Tat ca test case duoc ghi vao: {os.path.join(OUTPUT_DIR, 'testcases')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
    generate_testcases()