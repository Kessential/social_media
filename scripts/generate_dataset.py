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
    python generate_dataset.py
"""

import random
import os

# ─── Cau hinh ──────────────────────────────────────────────────────────────
NUM_USERS = 10_500                # Tong so nguoi dung
NUM_COMMUNITIES = 50              # So luong cum cong dong
INTRA_COMMUNITY_EDGES = 80_000    # Canh trong noi bo cong dong (day dac)
INTER_COMMUNITY_EDGES = 20_000    # Canh noi giua cac cong dong (cau noi thua thot)
HUB_COUNT = 100                   # So luong nguoi dung "nhom trung tam / influencer"
HUB_EXTRA_EDGES = 15_000          # Canh bo sung gan voi cac hub
SEED = 42                         # Hat giong de tai tao ngau nhien giong nhau

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
    print(f"[1/4] Dang tao {NUM_USERS} nguoi dung...")
    users: dict[int, str] = {}
    for uid in range(1, NUM_USERS + 1):
        users[uid] = generate_name(rng)

    # ── 2. Phan chia nguoi dung vao cac cum cong dong ──────────────────────────
    print(f"[2/4] Dang phan chia thanh {NUM_COMMUNITIES} cum cong dong...")
    user_ids = list(range(1, NUM_USERS + 1))
    rng.shuffle(user_ids)

    communities: list[list[int]] = [[] for _ in range(NUM_COMMUNITIES)]
    for i, uid in enumerate(user_ids):
        communities[i % NUM_COMMUNITIES].append(uid)

    # ── 3. Tao cac canh ket noi ───────────────────────────────────────────────────────
    edges: set[tuple[int, int]] = set()

    def add_edge(u: int, v: int):
        if u != v:
            edge = (min(u, v), max(u, v))
            edges.add(edge)

    # 3a. Canh noi bo cum cong dong (ket noi day dac trong nhom)
    print(f"[3/4] Dang tao cac ket noi ({INTRA_COMMUNITY_EDGES} noi bo + "
          f"{INTER_COMMUNITY_EDGES} lien cum + {HUB_EXTRA_EDGES} sieu ket noi)...")

    for _ in range(INTRA_COMMUNITY_EDGES):
        comm = rng.choice(communities)
        if len(comm) >= 2:
            u, v = rng.sample(comm, 2)
            add_edge(u, v)

    # 3b. Canh lien cum cong dong (cau noi giua cac nhom)
    for _ in range(INTER_COMMUNITY_EDGES):
        c1, c2 = rng.sample(range(NUM_COMMUNITIES), 2)
        u = rng.choice(communities[c1])
        v = rng.choice(communities[c2])
        add_edge(u, v)

    # 3c. Canh sieu ket noi / influencer (luat luy thua)
    hubs = rng.sample(user_ids, HUB_COUNT)
    for _ in range(HUB_EXTRA_EDGES):
        hub = rng.choice(hubs)
        target = rng.randint(1, NUM_USERS)
        add_edge(hub, target)

    # ── 4. Ghi cac file ket qua ───────────────────────────────────────────────────
    print(f"[4/4] Dang ghi cac file ket qua... ({len(users)} users, {len(edges)} edges)")

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for uid in range(1, NUM_USERS + 1):
            f.write(f"{uid},{users[uid]}\n")

    with open(EDGES_FILE, "w", encoding="utf-8") as f:
        for u, v in sorted(edges):
            f.write(f"{u} {v}\n")

    # ── Tom tat ─────────────────────────────────────────────────────────────────
    total_edges = len(edges)
    avg_degree = 2 * total_edges / NUM_USERS
    print(f"\n{'='*50}")
    print(f"  Da tao bo du lieu thanh cong!")
    print(f"  Nguoi dung:   {NUM_USERS:>10,}")
    print(f"  Canh ket noi: {total_edges:>10,}")
    print(f"  Bac trung binh: {avg_degree:>10.1f}")
    print(f"  So cum:       {NUM_COMMUNITIES:>10}")
    print(f"  Sieu ket noi: {HUB_COUNT:>10}")
    print(f"{'='*50}")
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
    """Tao cac bo du lieu test bien va dac biet."""
    print("\n" + "=" * 60)
    print("  Dang tao cac kich ban thu nghiem...")
    print("=" * 60)

    # ── TC01: Nguoi dung co lap (0 ban be) ─────────────────────────────────────
    # Nguoi dung 3 co lap -> suggestFriends(3) phai tra ve danh sach rong.
    write_testcase("tc01_isolated_user",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (1, 4), (2, 4)],
        expected=(
            "TC01: Nguoi dung co lap\n"
            "User 3 (Charlie) co 0 ban be.\n"
            "suggestFriends(3) -> [] (Trong, khong co bat ky ket noi nao)\n"
            "suggestFriends(1) -> goi y nguoi dung khong ket noi truc tiep\n"
        ))

    # ── TC02: Chi co duy nhat mot nguoi ban ────────────────────────────────────
    # Nguoi dung 1 co dung 1 ban (nguoi dung 2). Nguoi dung 2 co nhieu ban khac.
    # suggestFriends(1) phai tra ve toan bo ban be cua 2 (tru 1).
    write_testcase("tc02_single_friend",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (2, 3), (2, 4)],
        expected=(
            "TC02: Ban duy nhat\n"
            "User 1 co dung 1 nguoi ban: nguoi dung 2.\n"
            "suggestFriends(1) -> [3, 4] (ban cua nguoi dung 2)\n"
            "mutualConnectionsCount cho ca hai = 1 (thong qua nguoi dung 2)\n"
        ))

    # ── TC03: Nhom hoan hao (K5) ──────────────────────────────────────────
    # Tat ca 5 nguoi deu ket noi truc tiep voi nhau -> khong co goi y nao.
    write_testcase("tc03_complete_clique",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)],
        expected=(
            "TC03: Nhom hoan hao (K5)\n"
            "Moi nguoi deu da la ban cua nhau.\n"
            "suggestFriends(any) -> [] (Trong, khong co goi y moi)\n"
        ))

    # ── TC04: Do thi hinh sao ────────────────────────────────────────────────────
    # Nguoi dung 1 la trung tam. Cac la khong lien ket voi nhau.
    # suggestFriends(2) phai goi y tat ca cac la khac vi deu chung ban 1.
    write_testcase("tc04_star_graph",
        users={1: "Hub", 2: "L1", 3: "L2", 4: "L3", 5: "L4", 6: "L5"},
        edges=[(1,2),(1,3),(1,4),(1,5),(1,6)],
        expected=(
            "TC04: Do thi hinh sao\n"
            "User 1 la trung tam, cac user 2-6 la nhanh.\n"
            "suggestFriends(1) -> [] (Tat ca deu la ban truc tiep, khong co FoF)\n"
            "suggestFriends(2) -> [3,4,5,6] voi mutualCount=1 (thong qua trung tam)\n"
            "suggestFriends(2, maxSuggestions=2) -> chi lay top 2\n"
        ))

    # ── TC05: Do thi dang chuoi / tuyen tinh ──────────────────────────────────
    # 1-2-3-4-5 (duong di thang). FoF chi tim thay den khoang cach 2 buoc nhay.
    write_testcase("tc05_chain_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC05: Do thi hinh xich (1-2-3-4-5)\n"
            "suggestFriends(1) -> [3] (FoF qua 2, mutualCount=1)\n"
            "suggestFriends(3) -> [1, 5] (FoF qua 2 va 4)\n"
            "suggestFriends(5) -> [3] (FoF qua 4)\n"
            "Nguoi dung 1 khong the thay nguoi dung 4 hoac 5 (do sau > 2)\n"
        ))

    # ── TC06: Hai phan lien thong roi rac ───────────────────────────────────
    # {1,2,3} va {4,5,6} co lap hoan toan. Khong the goi y cheo cum.
    write_testcase("tc06_disconnected_components",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F"},
        edges=[(1,2),(2,3),(1,3), (4,5),(5,6),(4,6)],
        expected=(
            "TC06: Hai phan lien thong roi rac\n"
            "Nhom 1: {1,2,3} ket noi hoan toan. Nhom 2: {4,5,6} ket noi hoan toan.\n"
            "suggestFriends(1) -> [] (Da la ban voi tat ca nguoi trong nhom)\n"
            "suggestFriends(4) -> [] (Cung ly do)\n"
            "Khong the goi y cheo giua hai nhom.\n"
        ))

    # ── TC07: stress-test canh tu lap va trung lap ─────────────────────────────
    # Canh (1,1) va canh (1,2) ghi lap phai duoc xu ly an toan.
    write_testcase("tc07_self_loop_duplicate",
        users={1: "Alice", 2: "Bob", 3: "Charlie"},
        edges=[(1,1),(1,2),(1,2),(2,3)],
        expected=(
            "TC07: Tu ket noi va stress lap canh\n"
            "Canh (1,1) la tu ket noi -> se bi bo qua va khong gay loi.\n"
            "Canh (1,2) xuat hien hai lan -> adjList la tap hop nen khong bi trung lap.\n"
            "suggestFriends(1) -> [3] voi mutualCount=1 (thong qua nguoi dung 2)\n"
        ))

    # ── TC08: Chi co duy nhat 1 nguoi dung ─────────────────────────────────────
    # Kich ban bien nho nhat, khong co bat ky ket noi nao.
    write_testcase("tc08_single_user",
        users={1: "OnlyUser"},
        edges=[],
        expected=(
            "TC08: Chi co mot nguoi dung duy nhat (bien toi thieu)\n"
            "Chi co nguoi dung 1 ton tai. Khong co canh nao.\n"
            "suggestFriends(1) -> [] (khong co bat ky ket noi nao)\n"
        ))

    # ── TC09: Hai nguoi dung, mot ket noi duy nhat ─────────────────────────────
    # Do thi lien thong nho nhat. Khong co FoF.
    write_testcase("tc09_two_users",
        users={1: "Alice", 2: "Bob"},
        edges=[(1, 2)],
        expected=(
            "TC09: Hai nguoi dung, mot canh (do thi ket noi toi thieu)\n"
            "suggestFriends(1) -> [] (nguoi ban duy nhat la 2, 2 khong co ban khac)\n"
            "suggestFriends(2) -> [] (cung ly do)\n"
        ))

    # ── TC10: Sieu ket noi hinh sao khong lo (Stress test) ─────────────────────
    # 1 trung tam noi voi 999 nhanh. Kiem tra hieu nang va gioi han tai cho node bac cao.
    hub_users = {1: "SieuKetNoi"}
    hub_edges = []
    for i in range(2, 1001):
        hub_users[i] = f"Leaf_{i}"
        hub_edges.append((1, i))
    hub_edges.extend([(2, 3), (4, 5), (6, 7)])
    write_testcase("tc10_large_star_hub",
        users=hub_users,
        edges=hub_edges,
        expected=(
            "TC10: Nhanh sao khong lo (1 trung tam + 999 nhanh)\n"
            "Nguoi dung 1 co 999 ban truc tiep -> suggestFriends(1) = []\n"
            "Nguoi dung 2 -> suggestFriends(2) tra ve toi da 998 goi y\n"
            "  (tat ca cac nhanh khac qua trung tam), moi nhanh co mutualCount=1\n"
            "  Rieng nguoi dung 3 co mutualCount=2 (qua trung tam va canh truc tiep 2-3)\n"
            "Kiem tra hieu suat voi node bac cao.\n"
        ))

    # ── TC11: Hinh tam giac co duoi ────────────────────────────────────────────
    # 1-2-3-1 tam giac + 3-4 la duoi. Kiem tra tong hop ban chung chinh xac.
    write_testcase("tc11_triangle_with_tail",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(2,3),(1,3),(3,4)],
        expected=(
            "TC11: Hinh tam giac voi duoi (1-2-3 + 3-4)\n"
            "suggestFriends(1) -> [4] mutualCount=1 (qua 3)\n"
            "suggestFriends(2) -> [4] mutualCount=1 (qua 3)\n"
            "suggestFriends(4) -> [1, 2] moi nguoi mutualCount=1 (qua 3)\n"
        ))

    # ── TC12: Kiem tra chan tren cua so luong goi y (maxSuggestions) ───────────
    # Nguoi dung 1 co 1 ban (2), 2 lai co 10 ban khac (3-12). Kiem tra gioi han cat ket qua.
    ms_users = {1: "Alice", 2: "Hub"}
    ms_edges = [(1, 2)]
    for i in range(3, 13):
        ms_users[i] = f"Friend_{i}"
        ms_edges.append((2, i))
    write_testcase("tc12_max_suggestions_limit",
        users=ms_users,
        edges=ms_edges,
        expected=(
            "TC12: Gioi han maxSuggestions\n"
            "Nguoi dung 1 -> 1 ban (nguoi dung 2). Nguoi dung 2 -> 10 ban khac (3-12).\n"
            "suggestFriends(1, 5) -> dung 5 ket qua (bi gioi han)\n"
            "suggestFriends(1, 20) -> dung 10 ket qua (tat ca ket noi san co)\n"
            "suggestFriends(1, 0) -> 0 ket qua (bien max=0)\n"
        ))

    # ── TC13: Do thi hinh kim cuong ───────────────────────────────────────────
    # 1-2, 1-3, 2-4, 3-4. Nguoi dung 4 co 2 ban chung voi 1.
    write_testcase("tc13_diamond_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(1,3),(2,4),(3,4)],
        expected=(
            "TC13: Do thi hinh kim cuong\n"
            "suggestFriends(1) -> [4] voi mutualCount=2 (qua 2 VA 3)\n"
            "suggestFriends(4) -> [1] voi mutualCount=2 (qua 2 VA 3)\n"
            "Kiem tra tong hop so ban chung dung dan.\n"
        ))

    # ── TC14: maxSuggestions am (kiem tra loi crash cap phat) ────────────────
    # Nhap maxSuggestions = -5. Chuong trinh cu se bi loi std::bad_alloc do ep kieu am sang size_t.
    write_testcase("tc14_negative_max_suggestions",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1, 2), (2, 3)],
        expected=(
            "TC14: Kiem tra maxSuggestions am\n"
            "suggestFriends(1, -5) -> phai tra ve Vector rong chu khong duoc crash.\n"
        ))

    # ── TC15: Truy van user ID khong ton tai (kiem tra an toan chi muc) ──────
    # Truy van ID 9999 khong co trong he thong.
    write_testcase("tc15_nonexistent_user",
        users={1: "An", 2: "Binh"},
        edges=[(1, 2)],
        expected=(
            "TC15: Truy van ID nguoi dung khong ton tai\n"
            "suggestFriends(9999) -> phai tra ve Vector rong chu khong duoc crash.\n"
            "getFriendsOfFriends(9999) -> phai tra ve HashSet rong.\n"
        ))

    # ── TC16: Bo du lieu hoan toan rong (kiem tra khoi tao) ───────────────────
    # File users.csv va edges.txt khong co dong nao.
    write_testcase("tc16_empty_dataset",
        users={},
        edges=[],
        expected=(
            "TC16: Bo du lieu hoan toan rong\n"
            "He thong phai tai file thanh cong va hoat dong voi 0 nguoi dung chu khong crash chia 0.\n"
        ))

    # ── TC17: Du lieu CSV loi dinh dang (kiem tra crash do std::stoi) ──────────
    # File users.csv co tieu de "userID,name" hoac chua ID hop le nhu "abc" thay vi so.
    write_testcase("tc17_malformed_csv",
        users={"abc": "NguoiDungLoiDinhDang", "2": "Binh"},
        edges=[(2, 2)],
        expected=(
            "TC17: File CSV chua ID dang chu (abc) khong hop le\n"
            "std::stoi('abc') se nem ra ngoai le va gay crash chuong trinh neu ko co try-catch.\n"
        ))

    print("=" * 60)
    print(f"  All test cases written to: {os.path.join(OUTPUT_DIR, 'testcases')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
    generate_testcases()
