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
            "Nguoi dung 2 co ban truc tiep: {1 (hub), 3 (canh 2-3)}\n"
            "suggestFriends(2) tra ve 997 goi y (nhanh 4-1000 qua hub)\n"
            "  - User 3 KHONG nam trong goi y vi 3 da la ban truc tiep cua 2\n"
            "  - Moi nhanh (4-1000) co mutualCount=1 (qua hub)\n"
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

    # ── TC18: Xoa nguoi dung roi goi y ket ban (stale reference) ──────────────
    # Chain 1-2-3-4-5. Xoa user 3 -> adjList doi xung phai duoc cap nhat.
    write_testcase("tc18_remove_then_suggest",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung", 5: "Em"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC18: Xoa nguoi dung roi goi y ket ban (kiem tra stale reference)\n"
            "Do thi ban dau: 1-2-3-4-5 (chain)\n"
            "Thao tac: removeUser(3) -> xoa user 3 khoi he thong.\n"
            "Sau khi xoa:\n"
            "  - adjList[2] khong con chua 3\n"
            "  - adjList[4] khong con chua 3\n"
            "  - suggestFriends(1) -> [] (ban duy nhat cua 1 la 2, 2 khong co ban khac)\n"
            "  - suggestFriends(4) -> [] (ban duy nhat cua 4 la 5, 5 khong co ban khac)\n"
            "  - getUserCount() -> 4 (da xoa 1 user)\n"
            "  - getEdgeCount() -> 2 (canh 1-2 va 4-5 con lai)\n"
            "Kiem tra: Khong crash, khong co user 3 trong bat ky ket qua nao.\n"
        ))

    # ── TC19: Xoa ket noi roi kiem tra BFS cap nhat ──────────────────────────
    # Chain 1-2-3. Xoa canh 1-2 -> BFS tu 1 phai rong.
    write_testcase("tc19_remove_connection_bfs",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2),(2,3)],
        expected=(
            "TC19: Xoa ket noi roi kiem tra BFS cap nhat dung\n"
            "Do thi ban dau: 1-2-3 (chain)\n"
            "getFriendsOfFriends(1) ban dau -> {3} (qua 2)\n"
            "Thao tac: removeConnection(1, 2)\n"
            "Sau khi xoa:\n"
            "  - getFriendsOfFriends(1) -> {} (1 khong con ban nao)\n"
            "  - suggestFriends(1) -> [] (khong con ket noi)\n"
            "  - getEdgeCount() -> 1 (chi con canh 2-3)\n"
            "Kiem tra: BFS cap nhat dung sau khi xoa connection.\n"
        ))

    # ── TC20: Them ket noi giua nguoi dung khong ton tai ─────────────────────
    # Chi co user 1 va 2. Them canh (999,888) va (1,999) -> canh bao, bo qua.
    write_testcase("tc20_connection_nonexistent",
        users={1: "An", 2: "Binh"},
        edges=[(1,2),(999,888),(1,999)],
        expected=(
            "TC20: Them ket noi giua nguoi dung khong ton tai\n"
            "Chi co user 1 va 2 ton tai.\n"
            "addConnection(1, 2) -> thanh cong (ca 2 ton tai)\n"
            "addConnection(999, 888) -> canh bao, bo qua (ca 2 khong ton tai)\n"
            "addConnection(1, 999) -> canh bao, bo qua (999 khong ton tai)\n"
            "Ket qua: getEdgeCount() = 1 (chi co canh 1-2)\n"
            "Kiem tra: Khong crash, chi canh hop le duoc them.\n"
        ))

    # ── TC21: Tai file khong ton tai ──────────────────────────────────────────
    # Du lieu hop le nhung test case nay kiem tra khi duong dan file SAI.
    write_testcase("tc21_file_not_found",
        users={1: "An", 2: "Binh"},
        edges=[(1,2)],
        expected=(
            "TC21: Tai file khong ton tai\n"
            "Goi loadUsersFromFile(\"khong_ton_tai.csv\") -> tra ve false, xuat loi, KHONG crash.\n"
            "Goi loadConnectionsFromFile(\"khong_ton_tai.txt\") -> tra ve false, xuat loi, KHONG crash.\n"
            "He thong van hoat dong binh thuong sau khi load that bai.\n"
        ))

    # ── TC22: CSV va edges co dong trong xen ke ──────────────────────────────
    # Dong trong phai duoc bo qua an toan.
    # Ghi file thu cong de chen dong trong xen ke (write_testcase khong lam duoc).
    tc22_dir = os.path.join(OUTPUT_DIR, "testcases", "tc22_blank_lines_whitespace")
    os.makedirs(tc22_dir, exist_ok=True)
    with open(os.path.join(tc22_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Alice\n\n3,Charlie\n")
    with open(os.path.join(tc22_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("\n1 3\n\n")
    with open(os.path.join(tc22_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC22: CSV co dong trong va khoang trang\n"
            "File users.csv co dong trong xen ke giua user 1 va user 3.\n"
            "File edges.txt co dong trong o dau va cuoi file.\n"
            "Ket qua mong doi:\n"
            "  - Dong trong duoc bo qua (skip), khong crash\n"
            "  - getUserCount() = 2 (chi co user 1 va 3)\n"
            "  - getEdgeCount() = 1 (canh 1-3)\n"
            "  - Khong xuat loi cho dong trong\n"
        )
    print(f"  [OK] {'tc22_blank_lines_whitespace':40s} |     2 nguoi dung |     1 ket noi")

    # ── TC23: User ID cuc han (0, am, INT_MAX) ──────────────────────────────
    # Kiem tra HashMap hash voi cac gia tri bien.
    write_testcase("tc23_extreme_user_ids",
        users={0: "Zero", -1: "NegativeOne", 2147483647: "MaxInt"},
        edges=[(0,-1),(-1,2147483647),(0,2147483647)],
        expected=(
            "TC23: User ID cuc han (0, am, INT_MAX)\n"
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

    # ── TC24: suggestFriends voi maxSuggestions = 0 ──────────────────────────
    # Giong TC12 nhung maxSuggestions = 0, phai tra ve Vector rong.
    ms0_users = {1: "Alice", 2: "Hub"}
    ms0_edges = [(1, 2)]
    for i in range(3, 13):
        ms0_users[i] = f"Friend_{i}"
        ms0_edges.append((2, i))
    write_testcase("tc24_max_suggestions_zero",
        users=ms0_users,
        edges=ms0_edges,
        expected=(
            "TC24: suggestFriends voi maxSuggestions = 0\n"
            "suggestFriends(1, 0) -> [] (Vector rong, khong crash)\n"
            "Ly do: dieu kien 'maxSuggestions <= 0' trong suggestFriends()\n"
            "  tra ve Vector rong ngay lap tuc (early return).\n"
            "printSuggestions(1, 0) -> xuat '[LOI] So nhap vao khong hop le!'\n"
        ))

    # ── TC25: Do thi vong tron thuan tuy (cycle) ─────────────────────────────
    # 1-2-3-4-1. suggestFriends(1) -> [{3, mutualCount=2}] (qua 2 VA 4).
    write_testcase("tc25_cycle_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(2,3),(3,4),(4,1)],
        expected=(
            "TC25: Do thi vong tron thuan tuy (1-2-3-4-1)\n"
            "Ban truc tiep cua 1: {2, 4}\n"
            "getFriendsOfFriends(1) -> {3} (qua 2 VA qua 4)\n"
            "suggestFriends(1) -> [{3, mutualCount=2}]\n"
            "  (goi y qua ca 2 lan duong: 1->2->3 va 1->4->3)\n"
            "suggestFriends(2) -> [{4, mutualCount=2}]\n"
            "  (goi y qua: 2->1->4 va 2->3->4)\n"
            "Kiem tra: tong hop so ban chung dung khi co nhieu duong di.\n"
        ))

    # ── TC26: Goi tat ca cac ham khi khong co ket noi ────────────────────────
    # 3 users ton tai nhung khong co connection nao.
    write_testcase("tc26_empty_operations",
        users={1: "NoFriend", 2: "AlsoNoFriend", 3: "Lonely"},
        edges=[],
        expected=(
            "TC26: Goi tat ca cac ham tren du lieu khong co ket noi\n"
            "3 users ton tai nhung khong co connection nao.\n"
            "Goi cac ham sau va kiem tra khong crash:\n"
            "  - printGraphStats() -> Tong users=3, edges=0, avgDegree=0.00, isolated=3\n"
            "  - listUsers() -> Hien thi 3 users, tat ca co 0 ban be\n"
            "  - searchUserByName(\"NoFriend\") -> tim thay user 1\n"
            "  - getEdgeCount() -> 0\n"
            "  - suggestFriends(1) -> [] (khong co ban, khong co adjList entry)\n"
            "  - getFriendsOfFriends(1) -> {} (rong)\n"
            "  - getDirectConnections(1) -> {} (rong)\n"
            "Kiem tra: Tat ca cac ham tra ve ket qua hop ly, khong crash, khong chia 0.\n"
        ))

    # ── TC27: Ten nguoi dung co ky tu dac biet (dau phay, ngoac kep) ─────────
    # CSV parser dung dau phay lam delimiter -> ten chua dau phay se bi cat sai.
    tc27_dir = os.path.join(OUTPUT_DIR, "testcases", "tc27_special_chars_name")
    os.makedirs(tc27_dir, exist_ok=True)
    with open(os.path.join(tc27_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Nguyen Van A\n")
        f.write("2,Tran, Thi B\n")        # Dau phay trong ten!
        f.write("3,Le \"Nickname\" C\n")   # Ngoac kep trong ten
    with open(os.path.join(tc27_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("1 2\n2 3\n")
    with open(os.path.join(tc27_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC27: Ten nguoi dung co ky tu dac biet\n"
            "User 1: \"Nguyen Van A\" -> ten binh thuong, OK\n"
            "User 2: \"Tran, Thi B\" -> ten chua dau phay!\n"
            "  Parser: getline(ss, strUserID, ',') -> strUserID = \"2\", name = \" Thi B\"\n"
            "  Phan \"Tran\" bi mat vi parser cat tai dau phay dau tien trong ten.\n"
            "  => Day la han che cua CSV parser don gian.\n"
            "User 3: \"Le \\\"Nickname\\\" C\" -> ngoac kep, parser van OK\n"
            "Kiem tra: Khong crash.\n"
        )
    print(f"  [OK] {'tc27_special_chars_name':40s} |     3 nguoi dung |     2 ket noi")

    # ── TC28: User ID trung lap trong CSV ────────────────────────────────────
    # Dong dau: "1,Alice", dong sau: "1,AliceDuplicate" -> bo qua dong trung.
    write_testcase("tc28_duplicate_user_id",
        users={1: "Alice", 2: "Bob"},
        edges=[(1,2)],
        expected=(
            "TC28: User ID trung lap trong CSV\n"
            "Dong 1: \"1,Alice\" -> them thanh cong\n"
            "Dong 2: \"1,AliceDuplicate\" -> bo qua + canh bao (SAU KHI FIX addUser)\n"
            "Dong 3: \"2,Bob\" -> them thanh cong\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 2\n"
            "  - getUserName(1) = \"Alice\" (giu ten dau tien, khong bi ghi de)\n"
            "  - getUserName(2) = \"Bob\"\n"
            "  - Xuat canh bao cho dong trung ID\n"
        ))
    # Ghi de file users.csv de co dong trung (write_testcase sort theo key nen chi giu 1 ban)
    tc28_dir = os.path.join(OUTPUT_DIR, "testcases", "tc28_duplicate_user_id")
    with open(os.path.join(tc28_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,Alice\n1,AliceDuplicate\n2,Bob\n")

    # ── TC29: User ton tai nhung khong co trong adjList ──────────────────────
    # User 3 chua bao gio co connection -> suggestFriends(3) rong.
    write_testcase("tc29_user_no_adjlist",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2)],
        expected=(
            "TC29: User ton tai nhung khong co trong adjList\n"
            "User 3 co trong users nhung chua bao gio co connection.\n"
            "suggestFriends(3) -> [] (adjList khong chua key 3, tra ve Vector rong)\n"
            "getFriendsOfFriends(3) -> {} (rong)\n"
            "getDirectConnections(3) -> {} (rong)\n"
            "printUserInfo(3) -> Hien thi ten \"Chi\", so ban be: 0\n"
            "printSuggestions(3) -> \"Khong co goi y ket ban nao phu hop!\"\n"
            "Kiem tra: Khong crash, user duoc nhan dien nhung khong co du lieu ket noi.\n"
        ))

    # ── TC30: Edges file chua du lieu sai dinh dang ──────────────────────────
    # Dong co du lieu thua, chu cai, chi 1 so, v.v.
    tc30_dir = os.path.join(OUTPUT_DIR, "testcases", "tc30_malformed_edges")
    os.makedirs(tc30_dir, exist_ok=True)
    with open(os.path.join(tc30_dir, "users.csv"), "w", encoding="utf-8") as f:
        f.write("1,An\n2,Binh\n")
    with open(os.path.join(tc30_dir, "edges.txt"), "w", encoding="utf-8") as f:
        f.write("1 2 extra_data\nabc def\n1\n1 2\n")
    with open(os.path.join(tc30_dir, "expected.txt"), "w", encoding="utf-8") as f:
        f.write(
            "TC30: Edges file chua du lieu sai dinh dang\n"
            "Dong 1: \"1 2 extra_data\" -> ss >> userID_1 >> userID_2 thanh cong (bo qua extra), them canh 1-2\n"
            "Dong 2: \"abc def\" -> ss >> int fail -> canh bao, bo qua\n"
            "Dong 3: \"1\" -> chi co 1 so -> ss >> userID_2 fail -> canh bao, bo qua\n"
            "Dong 4: \"1 2\" -> thanh cong (nhung canh 1-2 da co, HashSet bo qua trung lap)\n"
            "Ket qua mong doi:\n"
            "  - getEdgeCount() = 1 (chi co canh 1-2 hop le)\n"
            "  - Xuat 2 canh bao cho dong 2 va dong 3\n"
            "  - Khong crash\n"
        )
    print(f"  [OK] {'tc30_malformed_edges':40s} |     2 nguoi dung |     4 ket noi")

    # ── TC31: Them roi xoa, kiem tra adjList doi xung ────────────────────────
    # 1-2, 2-3, 3-4, 4-5, 1-3. Xoa user 2 -> kiem tra cac canh con lai.
    write_testcase("tc31_add_remove_symmetry",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung", 5: "Em"},
        edges=[(1,2),(2,3),(3,4),(4,5),(1,3)],
        expected=(
            "TC31: Them roi xoa ket noi, kiem tra doi xung adjList\n"
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

    # ── TC32: Tim kiem nguoi dung theo ten (searchUserByName) ──────────────────
    # Kiem tra search case-insensitive va tim substring.
    write_testcase("tc32_search_by_name",
        users={1: "Nguyen Van An", 2: "Tran Thi Binh", 3: "Le Van An Khang",
               4: "Pham Minh", 5: "nguyen thi an"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC32: Tim kiem nguoi dung theo ten (searchUserByName)\n"
            "searchUserByName(\"an\") -> tim tat ca user co ten chua 'an' (case-insensitive):\n"
            "  - User 1: 'Nguyen Van An' (chua 'An')\n"
            "  - User 3: 'Le Van An Khang' (chua 'An')\n"
            "  - User 5: 'nguyen thi an' (chua 'an')\n"
            "  - User 4: 'Pham Minh' -> KHONG match (khong chua 'an')\n"
            "searchUserByName(\"BINH\") -> tim thay user 2 ('Tran Thi Binh')\n"
            "searchUserByName(\"xyz\") -> [] (khong tim thay)\n"
            "searchUserByName(\"\") -> tat ca user (empty string la substring cua moi string)\n"
            "Kiem tra: case-insensitive dung, substring match dung.\n"
        ))

    # ── TC33: Export functions ────────────────────────────────────────────────
    # Kiem tra exportSuggestions, exportGraphStats, exportUserConnections
    write_testcase("tc33_export_functions",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung"},
        edges=[(1,2),(2,3),(3,4),(1,3)],
        expected=(
            "TC33: Kiem tra cac ham export ra file\n"
            "Thao tac:\n"
            "  1. exportSuggestions(1, 5, 'test_suggest.txt') -> tra ve true, file duoc tao\n"
            "  2. exportGraphStats('test_stats.txt') -> tra ve true, file duoc tao\n"
            "  3. exportUserConnections(1, 'test_user.txt') -> tra ve true, file duoc tao\n"
            "  4. exportSuggestions(9999, 5, 'test_fail.txt') -> tra ve false (user khong ton tai)\n"
            "  5. exportUserConnections(9999, 'test_fail2.txt') -> tra ve false\n"
            "Kiem tra: File tao thanh cong, noi dung chinh xac, ham tra ve false khi user khong ton tai.\n"
        ))

    # ── TC34: Them user sau khi load file ─────────────────────────────────────
    # Load tu file, sau do them user va connection bang tay.
    write_testcase("tc34_add_after_load",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2),(2,3)],
        expected=(
            "TC34: Them user va connection sau khi load file\n"
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

    # ── TC35: Do thi hai phan (bipartite graph) ──────────────────────────────
    # Nhom A = {1,2,3}, Nhom B = {4,5,6}. Moi node nhom A ket noi tat ca node nhom B.
    bp_users = {1: "A1", 2: "A2", 3: "A3", 4: "B1", 5: "B2", 6: "B3"}
    bp_edges = []
    for a in [1, 2, 3]:
        for b in [4, 5, 6]:
            bp_edges.append((a, b))
    write_testcase("tc35_bipartite_graph",
        users=bp_users,
        edges=bp_edges,
        expected=(
            "TC35: Do thi hai phan (bipartite graph)\n"
            "Nhom A = {1,2,3}, Nhom B = {4,5,6}\n"
            "Moi node nhom A ket noi tat ca node nhom B (9 canh).\n"
            "suggestFriends(1) -> [{2, mutualCount=3}, {3, mutualCount=3}]\n"
            "  (2 va 3 deu co 3 ban chung voi 1: qua 4, 5, 6)\n"
            "suggestFriends(4) -> [{5, mutualCount=3}, {6, mutualCount=3}]\n"
            "  (5 va 6 deu co 3 ban chung voi 4: qua 1, 2, 3)\n"
            "Khong co goi y cheo nhom (da la ban truc tiep).\n"
        ))

    # ── TC36: Stress memory — load, xoa het, load lai ────────────────────────
    # Kiem tra memory management khi clear roi reload.
    sm_users = {}
    sm_edges = []
    for i in range(1, 51):
        sm_users[i] = f"User_{i}"
    for i in range(1, 50):
        sm_edges.append((i, i + 1))
    write_testcase("tc36_stress_memory",
        users=sm_users,
        edges=sm_edges,
        expected=(
            "TC36: Stress memory — load, xoa het, load lai\n"
            "Buoc 1: Load 50 users va 49 connections.\n"
            "Buoc 2: removeUser(1) den removeUser(50) — xoa tung user.\n"
            "Buoc 3: Kiem tra getUserCount() = 0, getEdgeCount() = 0.\n"
            "Buoc 4: Load lai cung file data.\n"
            "Buoc 5: Kiem tra getUserCount() = 50, getEdgeCount() = 49.\n"
            "Kiem tra: Khong memory leak, khong crash, data duoc tai lai dung.\n"
        ))

    # ── TC37: measurePerformance ──────────────────────────────────────────────
    # Kiem tra ham do hieu suat khong crash.
    write_testcase("tc37_measure_performance",
        users={1: "An", 2: "Binh", 3: "Chi", 4: "Dung"},
        edges=[(1,2),(2,3),(3,4),(1,3)],
        expected=(
            "TC37: Kiem tra measurePerformance\n"
            "Thao tac:\n"
            "  1. measurePerformance(1) -> in thoi gian BFS, goi y, export (khong crash)\n"
            "  2. measurePerformance(9999) -> xuat '[LOI] Nguoi dung 9999 khong ton tai!'\n"
            "Kiem tra: Ham chay binh thuong, khong crash, xuat ket qua hop ly.\n"
        ))

    # ── TC38: removeUser user khong ton tai ───────────────────────────────────
    # Goi removeUser voi ID khong co trong he thong.
    write_testcase("tc38_remove_nonexistent_user",
        users={1: "An", 2: "Binh"},
        edges=[(1,2)],
        expected=(
            "TC38: removeUser voi user khong ton tai\n"
            "removeUser(9999) -> xuat '[LOI] Nguoi dung 9999 khong ton tai!'\n"
            "removeUser(0) -> xuat loi tuong tu\n"
            "Ket qua mong doi:\n"
            "  - getUserCount() = 2 (khong thay doi)\n"
            "  - getEdgeCount() = 1 (khong thay doi)\n"
            "  - Khong crash, chi xuat thong bao loi\n"
        ))

    # ── TC39: removeConnection ket noi khong ton tai ──────────────────────────
    # Goi removeConnection voi canh khong co hoac user khong co.
    write_testcase("tc39_remove_nonexistent_connection",
        users={1: "An", 2: "Binh", 3: "Chi"},
        edges=[(1,2)],
        expected=(
            "TC39: removeConnection voi ket noi khong ton tai\n"
            "removeConnection(1, 3) -> xuat '[LOI] Ket noi 1 <-> 3 khong ton tai!'\n"
            "  (user 1 va 3 ton tai nhung khong co canh)\n"
            "removeConnection(1, 9999) -> xuat '[LOI] Nguoi dung khong ton tai!'\n"
            "  (user 9999 khong ton tai)\n"
            "removeConnection(9999, 8888) -> xuat '[LOI] Nguoi dung khong ton tai!'\n"
            "Ket qua mong doi:\n"
            "  - getEdgeCount() = 1 (chi co canh 1-2, khong thay doi)\n"
            "  - Khong crash, chi xuat thong bao loi\n"
        ))

    print("=" * 60)
    print(f"  Tat ca test case duoc ghi vao: {os.path.join(OUTPUT_DIR, 'testcases')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
    generate_testcases()
