"""
Generate a realistic social network dataset for the FriendsSuggestion project.

Output files:
  - users.csv   : userID,name       (10,000+ users)
  - edges.txt   : userID_1 userID_2 (friendship edges)

The script creates a graph that mimics real social networks:
  - Power-law (scale-free) degree distribution via preferential attachment
  - Community clusters with denser internal connections
  - A small number of "influencer" hubs with many connections

Usage:
    python generate_dataset.py
"""

import random
import os

# ─── Configuration ──────────────────────────────────────────────────────────────
NUM_USERS = 10_500                # Total number of users
NUM_COMMUNITIES = 50              # Number of community clusters
INTRA_COMMUNITY_EDGES = 80_000    # Edges within communities (dense)
INTER_COMMUNITY_EDGES = 20_000    # Edges between communities (sparse bridges)
HUB_COUNT = 100                   # Number of "influencer" hubs
HUB_EXTRA_EDGES = 15_000          # Extra edges attached to hubs
SEED = 42                         # Reproducible randomness

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(OUTPUT_DIR, "users.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.txt")

# ─── Name pools ─────────────────────────────────────────────────────────────────
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
    """Generate a random full name (70% Vietnamese, 30% English)."""
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

    # ── 1. Generate users ───────────────────────────────────────────────────────
    print(f"[1/4] Generating {NUM_USERS} users...")
    users: dict[int, str] = {}
    for uid in range(1, NUM_USERS + 1):
        users[uid] = generate_name(rng)

    # ── 2. Assign users to communities ──────────────────────────────────────────
    print(f"[2/4] Partitioning into {NUM_COMMUNITIES} communities...")
    user_ids = list(range(1, NUM_USERS + 1))
    rng.shuffle(user_ids)

    communities: list[list[int]] = [[] for _ in range(NUM_COMMUNITIES)]
    for i, uid in enumerate(user_ids):
        communities[i % NUM_COMMUNITIES].append(uid)

    # ── 3. Generate edges ───────────────────────────────────────────────────────
    edges: set[tuple[int, int]] = set()

    def add_edge(u: int, v: int):
        if u != v:
            edge = (min(u, v), max(u, v))
            edges.add(edge)

    # 3a. Intra-community edges (dense connections within groups)
    print(f"[3/4] Creating edges ({INTRA_COMMUNITY_EDGES} intra + "
          f"{INTER_COMMUNITY_EDGES} inter + {HUB_EXTRA_EDGES} hub)...")

    for _ in range(INTRA_COMMUNITY_EDGES):
        comm = rng.choice(communities)
        if len(comm) >= 2:
            u, v = rng.sample(comm, 2)
            add_edge(u, v)

    # 3b. Inter-community edges (bridges between groups)
    for _ in range(INTER_COMMUNITY_EDGES):
        c1, c2 = rng.sample(range(NUM_COMMUNITIES), 2)
        u = rng.choice(communities[c1])
        v = rng.choice(communities[c2])
        add_edge(u, v)

    # 3c. Hub / influencer edges (power-law tail)
    hubs = rng.sample(user_ids, HUB_COUNT)
    for _ in range(HUB_EXTRA_EDGES):
        hub = rng.choice(hubs)
        target = rng.randint(1, NUM_USERS)
        add_edge(hub, target)

    # ── 4. Write output files ───────────────────────────────────────────────────
    print(f"[4/4] Writing files... ({len(users)} users, {len(edges)} edges)")

    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for uid in range(1, NUM_USERS + 1):
            f.write(f"{uid},{users[uid]}\n")

    with open(EDGES_FILE, "w", encoding="utf-8") as f:
        for u, v in sorted(edges):
            f.write(f"{u} {v}\n")

    # ── Summary ─────────────────────────────────────────────────────────────────
    total_edges = len(edges)
    avg_degree = 2 * total_edges / NUM_USERS
    print(f"\n{'='*50}")
    print(f"  Dataset generated successfully!")
    print(f"  Users:       {NUM_USERS:>10,}")
    print(f"  Edges:       {total_edges:>10,}")
    print(f"  Avg degree:  {avg_degree:>10.1f}")
    print(f"  Communities: {NUM_COMMUNITIES:>10}")
    print(f"  Hub users:   {HUB_COUNT:>10}")
    print(f"{'='*50}")
    print(f"  -> {USERS_FILE}")
    print(f"  -> {EDGES_FILE}")


# =============================================================================
# TEST CASES & BOUNDARY CONDITIONS
# =============================================================================

def write_testcase(name: str, users: dict[int, str],
                   edges: list[tuple[int, int]], expected: str):
    """Write a single test case to testcases/<name>/."""
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

    print(f"  [OK] {name:40s} | {len(users):>5} users | {len(edges):>5} edges")


def generate_testcases():
    """Generate boundary / edge-case test datasets."""
    print("\n" + "=" * 60)
    print("  Generating test cases...")
    print("=" * 60)

    # ── TC01: Isolated user (0 friends) ─────────────────────────────────────
    # User 3 has no connections -> suggestFriends(3) must return empty.
    write_testcase("tc01_isolated_user",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (1, 4), (2, 4)],
        expected=(
            "TC01: Isolated user\n"
            "User 3 (Charlie) has 0 friends.\n"
            "suggestFriends(3) -> [] (empty, no connections at all)\n"
            "suggestFriends(1) -> should suggest user not directly connected\n"
        ))

    # ── TC02: Single friend only ────────────────────────────────────────────
    # User 1 has exactly 1 friend (user 2). User 2 has other friends.
    # suggestFriends(1) should return user 2's friends (except user 1).
    write_testcase("tc02_single_friend",
        users={1: "Alice", 2: "Bob", 3: "Charlie", 4: "David"},
        edges=[(1, 2), (2, 3), (2, 4)],
        expected=(
            "TC02: Single friend\n"
            "User 1 has only 1 friend: user 2.\n"
            "suggestFriends(1) -> [3, 4] (friends of user 2)\n"
            "mutualConnectionsCount for both = 1 (through user 2)\n"
        ))

    # ── TC03: Complete clique (K5) ──────────────────────────────────────────
    # All 5 users connected to each other -> no suggestions possible.
    write_testcase("tc03_complete_clique",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)],
        expected=(
            "TC03: Complete clique (K5)\n"
            "Everyone is already friends with everyone.\n"
            "suggestFriends(any) -> [] (empty, no new suggestions)\n"
        ))

    # ── TC04: Star graph ────────────────────────────────────────────────────
    # User 1 (hub) connected to all others. Leaf nodes not connected to each other.
    # suggestFriends(2) should suggest all other leaves via mutual = user 1.
    write_testcase("tc04_star_graph",
        users={1: "Hub", 2: "L1", 3: "L2", 4: "L3", 5: "L4", 6: "L5"},
        edges=[(1,2),(1,3),(1,4),(1,5),(1,6)],
        expected=(
            "TC04: Star graph\n"
            "User 1 is hub, users 2-6 are leaves.\n"
            "suggestFriends(1) -> [] (all neighbors, no FoF)\n"
            "suggestFriends(2) -> [3,4,5,6] each with mutualCount=1 (via hub)\n"
            "suggestFriends(2, maxSuggestions=2) -> top 2 only\n"
        ))

    # ── TC05: Chain / linear graph ──────────────────────────────────────────
    # 1-2-3-4-5 (linear path). FoF only sees 2 hops away.
    write_testcase("tc05_chain_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"},
        edges=[(1,2),(2,3),(3,4),(4,5)],
        expected=(
            "TC05: Chain graph (1-2-3-4-5)\n"
            "suggestFriends(1) -> [3] (FoF via 2, mutualCount=1)\n"
            "suggestFriends(3) -> [1, 5] (FoF via 2 and 4)\n"
            "suggestFriends(5) -> [3] (FoF via 4)\n"
            "User 1 cannot see user 4 or 5 (>2 hops)\n"
        ))

    # ── TC06: Two disconnected components ───────────────────────────────────
    # {1,2,3} and {4,5,6} are separate groups. No cross-suggestions.
    write_testcase("tc06_disconnected_components",
        users={1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F"},
        edges=[(1,2),(2,3),(1,3), (4,5),(5,6),(4,6)],
        expected=(
            "TC06: Two disconnected components\n"
            "Group1: {1,2,3} fully connected. Group2: {4,5,6} fully connected.\n"
            "suggestFriends(1) -> [] (already friends with all in group)\n"
            "suggestFriends(4) -> [] (same reason)\n"
            "No cross-group suggestions possible.\n"
        ))

    # ── TC07: Self-loop & duplicate edge stress ─────────────────────────────
    # addConnection(1,1) and duplicate addConnection(1,2) should be harmless.
    write_testcase("tc07_self_loop_duplicate",
        users={1: "Alice", 2: "Bob", 3: "Charlie"},
        edges=[(1,1),(1,2),(1,2),(2,3)],
        expected=(
            "TC07: Self-loop & duplicate edges\n"
            "Edge (1,1) is a self-loop -> should be ignored or harmless.\n"
            "Edge (1,2) appears twice -> adjList is a set, so no duplicates.\n"
            "suggestFriends(1) -> [3] with mutualCount=1 (via user 2)\n"
        ))

    # ── TC08: Single user in system ─────────────────────────────────────────
    # Only 1 user exists, no edges. Minimum boundary.
    write_testcase("tc08_single_user",
        users={1: "OnlyUser"},
        edges=[],
        expected=(
            "TC08: Single user (minimum boundary)\n"
            "Only user 1 exists. No edges.\n"
            "suggestFriends(1) -> [] or error (user has no entry in adjList)\n"
            "getDirectConnections(1) -> may throw if adjList has no key 1\n"
        ))

    # ── TC09: Two users, one edge ───────────────────────────────────────────
    # Minimum connected graph. No FoF possible.
    write_testcase("tc09_two_users",
        users={1: "Alice", 2: "Bob"},
        edges=[(1, 2)],
        expected=(
            "TC09: Two users, one edge (minimum connected)\n"
            "suggestFriends(1) -> [] (only friend is 2, 2 has no other friends)\n"
            "suggestFriends(2) -> [] (same reason)\n"
        ))

    # ── TC10: Large star hub (stress boundary) ──────────────────────────────
    # 1 hub connected to 999 leaves. Tests performance with high-degree node.
    hub_users = {1: "MegaHub"}
    hub_edges = []
    for i in range(2, 1001):
        hub_users[i] = f"Leaf_{i}"
        hub_edges.append((1, i))
    # Connect a few leaves to create FoF paths
    hub_edges.extend([(2, 3), (4, 5), (6, 7)])
    write_testcase("tc10_large_star_hub",
        users=hub_users,
        edges=hub_edges,
        expected=(
            "TC10: Large star hub (1 hub + 999 leaves)\n"
            "User 1 has 999 direct friends -> suggestFriends(1) = []\n"
            "User 2 -> suggestFriends(2) returns up to 998 suggestions\n"
            "  (all other leaves via hub), each with mutualCount=1\n"
            "  Plus user 3 has mutualCount=2 (via hub AND direct edge 2-3)\n"
            "Tests performance with high-degree node.\n"
        ))

    # ── TC11: Triangle with tail ────────────────────────────────────────────
    # 1-2-3-1 triangle + 3-4 tail. Tests mutual count correctly.
    write_testcase("tc11_triangle_with_tail",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(2,3),(1,3),(3,4)],
        expected=(
            "TC11: Triangle (1-2-3) + tail (3-4)\n"
            "suggestFriends(1) -> [4] mutualCount=1 (via 3)\n"
            "suggestFriends(2) -> [4] mutualCount=1 (via 3)\n"
            "suggestFriends(4) -> [1, 2] each mutualCount=1 (via 3)\n"
        ))

    # ── TC12: maxSuggestions boundary ───────────────────────────────────────
    # User 1 has 1 friend (user 2), user 2 has 10 other friends.
    # suggestFriends(1, 5) should return only 5 out of 10.
    ms_users = {1: "Alice", 2: "Hub"}
    ms_edges = [(1, 2)]
    for i in range(3, 13):
        ms_users[i] = f"Friend_{i}"
        ms_edges.append((2, i))
    write_testcase("tc12_max_suggestions_limit",
        users=ms_users,
        edges=ms_edges,
        expected=(
            "TC12: maxSuggestions boundary\n"
            "User 1 -> 1 friend (user 2). User 2 -> 10 other friends (3-12).\n"
            "suggestFriends(1, 5) -> exactly 5 results (capped)\n"
            "suggestFriends(1, 20) -> exactly 10 results (all available)\n"
            "suggestFriends(1, 0) -> 0 results (edge case: max=0)\n"
        ))

    # ── TC13: Diamond graph ─────────────────────────────────────────────────
    # 1-2, 1-3, 2-4, 3-4. User 4 has 2 mutual connections with user 1.
    write_testcase("tc13_diamond_graph",
        users={1: "A", 2: "B", 3: "C", 4: "D"},
        edges=[(1,2),(1,3),(2,4),(3,4)],
        expected=(
            "TC13: Diamond graph\n"
            "suggestFriends(1) -> [4] with mutualCount=2 (via 2 AND 3)\n"
            "suggestFriends(4) -> [1] with mutualCount=2 (via 2 AND 3)\n"
            "Tests that mutual count aggregates correctly.\n"
        ))

    print("=" * 60)
    print(f"  All test cases written to: {os.path.join(OUTPUT_DIR, 'testcases')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
    generate_testcases()
