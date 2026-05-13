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
    "An", "Bảo", "Chi", "Dũng", "Đức", "Giang", "Hà", "Hiếu", "Hoa", "Hoàng",
    "Hùng", "Hương", "Khánh", "Lan", "Linh", "Long", "Mai", "Minh", "Nam", "Ngân",
    "Ngọc", "Nhung", "Phong", "Phúc", "Phương", "Quân", "Quỳnh", "Sơn", "Thảo",
    "Thanh", "Thắng", "Thiên", "Thịnh", "Thu", "Thuỷ", "Tiến", "Trang", "Trung",
    "Tuấn", "Tùng", "Uyên", "Vân", "Việt", "Vũ", "Xuân", "Yến",
]

LAST_NAMES_VN = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
    "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Trịnh", "Đinh",
]

MIDDLE_NAMES_VN = [
    "Văn", "Thị", "Hữu", "Minh", "Đức", "Quốc", "Thanh", "Ngọc",
    "Hoàng", "Xuân", "Bảo", "Anh", "Tuấn", "Phương", "Hồng",
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


if __name__ == "__main__":
    main()
