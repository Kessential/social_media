# Mô Phỏng Mạng Xã Hội — BFS Friend Suggestion

Ứng dụng console C++ mô phỏng mạng xã hội, sử dụng thuật toán **BFS (Breadth-First Search)** để tìm "bạn của bạn" và gợi ý kết bạn dựa trên số bạn chung.

---

## Cấu trúc thư mục

```
social_media/
├── Makefile
├── README.md
├── scripts/
│   ├── generate_dataset.py   # Sinh dữ liệu 10,500+ người dùng & 34 test cases
│   ├── printpath.py          # Tiện ích in đường dẫn
│   ├── run_tests.py          # Chạy toàn bộ test cases tự động
│   └── run_tc33.py           # Chạy riêng TC33 (stress test bộ nhớ)
└── src/
    ├── main.cpp              # Entry point, menu tương tác 14 chức năng
    ├── SocialMedia.h         # Khai báo class SocialMedia, struct BFSNode, FriendSuggestion, GraphStats
    ├── SocialMedia.cpp       # Toàn bộ logic nghiệp vụ
    ├── CustomHashMap.h       # HashMap tự cài (separate chaining, auto-rehash)
    ├── CustomHashSet.h       # HashSet tự cài (wrapper trên HashMap)
    ├── CustomVector.h        # Vector tự cài (dynamic array)
    ├── CustomQueue.h         # Queue tự cài (linked-list FIFO, dùng cho BFS)
    └── CustomSort.h          # Hybrid Quicksort (Hoare + Insertion Sort)
```

---

## Tính năng

| # | Chức năng | Mô tả |
|---|-----------|-------|
| 1 | Tải dữ liệu từ file | Đọc `users.csv` (ID,tên) và `edges.txt` (ID1 ID2) |
| 2 | Thêm người dùng | Thêm user mới với ID và tên |
| 3 | Thêm kết nối | Thêm cạnh vô hướng giữa hai user |
| 4 | Xóa người dùng | Xóa user và tự động xóa toàn bộ kết nối liên quan |
| 5 | Xóa kết nối | Xóa cạnh giữa hai user |
| 6 | Hiển thị danh sách người dùng | Phân trang 20/trang, sắp xếp theo ID tăng dần, hiển thị số bạn bè |
| 7 | Xem thông tin người dùng | ID, tên, danh sách bạn bè phân trang sắp xếp theo ID |
| 8 | Tìm kiếm theo tên | Không phân biệt hoa/thường, tìm substring; nhập ID để xem chi tiết |
| 9 | Xem bạn bè trực tiếp | Danh sách bạn bậc 1 kèm tên, phân trang 20/trang |
| 10 | Tìm bạn của bạn (BFS) | BFS độ sâu 2, phân trang 20/trang, điều hướng [n]/[p]/[Enter] |
| 11 | Gợi ý kết bạn | Sắp xếp giảm dần theo số bạn chung (tie-breaker: ID tăng dần), phân trang, hiển thị tối đa 3 bạn chung |
| 12 | Thống kê đồ thị | Tổng user/cạnh, bậc TB, **tất cả** user nhiều/ít bạn nhất, user cô lập |
| 13 | Export ra file | Export gợi ý / thống kê / thông tin user ra file `.txt` |
| 14 | Đo hiệu suất | Benchmark tự động 4 thuật toán theo nhóm bậc, warm-up + median của 10 lần đo |

---

## Cấu trúc dữ liệu tự cài

Toàn bộ project **không dùng STL containers** (vector, unordered_map, queue).

### `HashMap<K, V>` — `CustomHashMap.h`
- Separate chaining với mảng con trỏ `HashNode*`
- Auto-rehash khi load factor vượt `0.75` (gấp đôi số bucket)
- Hỗ trợ: `put`, `get`, `contains`, `remove`, `operator[]`, `forEach`, `forEachMut`
- Đầy đủ copy/move constructor & assignment operator

### `HashSet<T>` — `CustomHashSet.h`
- Wrapper mỏng trên `HashMap<T, bool>`
- Hỗ trợ: `insert`, `contains`, `remove`, `forEach`, `toVector`, `size`

### `Vector<T>` — `CustomVector.h`
- Dynamic array, tự động tăng gấp đôi capacity khi đầy
- Hỗ trợ: `push_back`, `pop_back`, `operator[]`, `resize`, `clear`, `shrink`, `empty`, `size`
- Đầy đủ copy/move constructor & assignment operator

### `Queue<T>` — `CustomQueue.h`
- Linked-list FIFO, dùng cho BFS
- Hỗ trợ: `push`, `pop`, `front`, `empty`, `size`
- Copy/assignment bị xóa (`= delete`)

### `Sort` namespace — `CustomSort.h`
- **Hybrid Quicksort**: Hoare partition + median-of-three pivot selection
- Fallback sang **Insertion Sort** khi đoạn còn ≤ 10 phần tử
- Tail-call optimization (iterative cho nhánh lớn hơn)
- Overload: `sort(arr)` tăng dần và `sort(arr, comparator)` tùy chỉnh

---

## Các struct chính

### `BFSNode` — `SocialMedia.h`
```cpp
struct BFSNode {
    int userID;
    int depth;
};
```
Dùng thay `std::pair<int,int>` trong hàng đợi BFS.

### `FriendSuggestion` — `SocialMedia.h`
```cpp
struct FriendSuggestion {
    int suggestedUserID;
    int mutualConnectionsCount;
    Vector<int> mutualConnectionsIDs;
};
```

### `GraphStats` — `SocialMedia.h`
```cpp
struct GraphStats {
    int totalUsers;
    int totalEdges;
    int maxDegree;
    Vector<int> maxDegreeUsers; // Tất cả user có bậc cao nhất
    int minDegree;
    Vector<int> minDegreeUsers; // Tất cả user có bậc thấp nhất
    int isolatedCount;
    double avgDegree;
};
```
`maxDegreeUsers` và `minDegreeUsers` lưu **toàn bộ** danh sách (không chỉ 1 user) để xử lý trường hợp nhiều user cùng bậc.

---

## Thuật toán lõi

### BFS — `getFriendsOfFriends(userID)`

Duyệt BFS từ `userID` đến độ sâu tối đa 2. Trả về tập hợp tất cả user ở đúng cấp 2 (loại trừ user gốc và bạn trực tiếp).

```
visited = {userID}
queue   = [(userID, depth=0)]

while queue không rỗng:
    (curr, depth) = dequeue
    if depth == 2:
        thêm curr vào kết quả; continue
    for neighbor in adjList[curr]:
        if neighbor chưa visited:
            enqueue (neighbor, depth+1)
            visited.add(neighbor)
```

### Gợi ý kết bạn — `suggestFriends(userID, maxSuggestions)`

1. Lấy danh sách bạn trực tiếp `directConns`
2. Với mỗi bạn `f` trong `directConns`, duyệt bạn `fof` của `f`:
   - Nếu `fof ≠ userID` và `fof ∉ directConns` → ghi nhận `f` là bạn chung của `fof`
3. Xây dựng `Vector<FriendSuggestion>`, sắp xếp theo tiêu chí:
   - **Giảm dần** theo `mutualConnectionsCount`
   - Tie-breaker: **tăng dần** theo `suggestedUserID`
4. Cắt kết quả về `maxSuggestions`

Khi in ra màn hình (`printSuggestions`): mỗi gợi ý hiển thị tối đa **3 bạn chung** đầu tiên, phần còn lại ghi "và N người khác".

### Thống kê đồ thị — `computeGraphStats()`

- Duyệt toàn bộ `users`, tính bậc từng node qua `adjList`
- Cập nhật `maxDegreeUsers` / `minDegreeUsers` theo dạng **Vector** để giữ tất cả user cùng bậc cực trị
- `getEdgeCount()`: tổng kích thước `adjList` / 2 (mỗi cạnh đếm 2 lần do vô hướng)

### Đo hiệu suất — `measurePerformance()`

Benchmark **tự động** (không cần nhập User ID), phân loại toàn bộ user thành 5 nhóm theo số bạn (bậc đồ thị):

| Nhóm | Bậc |
|------|-----|
| Isolated | = 0 |
| Low | 1 – 9 |
| Medium | 10 – 99 |
| High | 100 – 999 |
| Hub | ≥ 1000 |

Với mỗi nhóm, lấy tối đa **10 mẫu** phân bố đều. Mỗi mẫu được đo **10 lần** sau **3 vòng warm-up**, kết quả báo cáo theo **median** (tránh nhiễu từ các đột biến thời gian).

4 thuật toán được benchmark:

1. **BFS** — `getFriendsOfFriends` (depth = 2): báo cáo Min/Avg(median)/Max theo nhóm + throughput (ops/sec)
2. **Suggest Friends** — `suggestFriends(k=10)`: cùng định dạng theo nhóm
3. **Search by Name** — `searchUserByName`: 4 loại keyword (High-match / Medium-match / Low-match / No-match), báo cáo Min/Avg/Max + số kết quả tìm được
4. **Graph Stats** — `computeGraphStats()`: báo cáo Min/Med/Max cho toàn bộ đồ thị

---

## Định dạng file dữ liệu

### `users.csv`
```
<userID>,<tên>
```
Ví dụ:
```
1,Nguyen Van An
2,Tran Thi Binh
3,Mary Johnson
```

### `edges.txt`
```
<userID_1> <userID_2>
```
Ví dụ:
```
1 2
1 3
2 4
```

- Đồ thị **vô hướng** — mỗi cạnh chỉ cần khai báo một chiều
- Dòng trống và dòng không hợp lệ bị bỏ qua kèm cảnh báo
- Kết nối trùng lặp và tự kết nối (`1 1`) bị từ chối với cảnh báo

---

## Build & Chạy

Dự án được thiết kế **cross-platform**, có thể biên dịch mượt mà trên Windows, Linux và macOS. Script `Makefile` sẽ tự động nhận diện hệ điều hành để đưa ra luồng build phù hợp.

**Yêu cầu:** Trình biên dịch hỗ trợ **C++17** (như `g++`, `clang++`) và `make`.

```bash
# Build
make

# Xóa các file thực thi và object files cũ
make clean

# Xóa sạch và biên dịch lại từ đầu
make rebuild
```

**Cách chạy chương trình:**
- **Trên Linux/macOS:**
  ```bash
  ./SocialMedia
  ```
- **Trên Windows (cmd/PowerShell):**
  ```cmd
  .\SocialMedia.exe
  ```

*Lưu ý: Khi chạy trên Windows, chương trình sẽ tự động thiết lập Console thành UTF-8 (`SetConsoleOutputCP(CP_UTF8)`) để hiển thị tốt mã Unicode.*

---

## Các Script hỗ trợ (Thư mục `scripts/`)

Dự án cung cấp sẵn một số script Python để tự động hóa việc khởi tạo dữ liệu, kiểm thử toàn diện và đánh giá hiệu năng. Tất cả các script cần được chạy từ thư mục gốc của dự án.

### 1. `generate_dataset.py` - Sinh dữ liệu và Test cases
Script này thực hiện 2 nhiệm vụ chính:
- Sinh ra bộ dữ liệu đồ thị mạng xã hội (Scale-free network) quy mô vừa gồm khoảng **10,500 người dùng** (`users.csv`) và **~166,000 kết nối** (`edges.txt`).
- Tự động sinh ra 34 thư mục kịch bản kiểm thử (test cases) để test các tình huống ngoại lệ.

**Cách chạy:**
```bash
python scripts/generate_dataset.py
```

**Ví dụ Output:**
```text
[1/5] Dang tao 10500 nguoi dung...
[5/5] Ghi file... (10500 users, 165506 edges)
...
=======================================================
  Da tao bo du lieu thanh cong!
  Tong nguoi dung:          10,500
  ...
  Tong canh ket noi:       165,506
=======================================================
...
```

<details>
<summary><b>Danh sách 34 Test Cases được sinh ra (bấm để xem chi tiết)</b></summary>

| # | Tên | Mô tả |
|---|-----|-------|
| TC01 | `connection_nonexistent` | Thêm kết nối khi một trong hai user không tồn tại |
| TC02 | `duplicate_user_id` | File CSV có ID trùng lặp |
| TC03 | `remove_nonexistent_user` | Xóa user không tồn tại |
| TC04 | `remove_nonexistent_connection` | Xóa kết nối không tồn tại |
| TC05 | `remove_connection_bfs` | Xóa kết nối rồi kiểm tra lại BFS |
| TC06 | `add_remove_symmetry` | Kiểm tra tính đối xứng của adjList sau thêm/xóa |
| TC07 | `add_after_load` | Thêm user/kết nối sau khi tải file |
| TC08 | `file_not_found` | File đầu vào không tồn tại |
| TC09 | `blank_lines_whitespace` | File có dòng trống và khoảng trắng thừa |
| TC10 | `malformed_csv` | File CSV sai định dạng |
| TC11 | `special_chars_name` | Tên chứa ký tự đặc biệt (dấu phẩy, Unicode) |
| TC12 | `malformed_edges` | File edges sai định dạng |
| TC13 | `chain_graph` | Đồ thị dạng chuỗi (1–2–3–…–N) |
| TC14 | `diamond_graph` | Đồ thị kim cương (2 bạn chung) |
| TC15 | `cycle_graph` | Đồ thị vòng tròn |
| TC16 | `triangle_with_tail` | Tam giác + đuôi |
| TC17 | `bipartite_graph` | Đồ thị hai phía |
| TC18 | `isolated_user` | User cô lập (không có kết nối) |
| TC19 | `single_friend` | User chỉ có đúng 1 bạn |
| TC20 | `complete_clique` | Đồ thị đầy đủ K-n (clique) |
| TC21 | `star_graph` | Đồ thị sao (1 hub nối tất cả) |
| TC22 | `disconnected_components` | Nhiều thành phần rời rạc |
| TC23 | `max_suggestions_limit` | Kiểm tra giới hạn `maxSuggestions` |
| TC24 | `extreme_user_ids` | ID cực hạn (0, âm, INT_MAX) |
| TC25 | `single_user` | Chỉ có 1 user trong hệ thống |
| TC26 | `two_users` | Chỉ có 2 user, không có kết nối |
| TC27 | `empty_dataset` | Dataset rỗng |
| TC28 | `self_loop_duplicate` | Tự kết nối và kết nối trùng lặp |
| TC29 | `nonexistent_user` | Truy vấn user không tồn tại |
| TC30 | `search_by_name` | Tìm kiếm theo tên (có/không có kết quả) |
| TC31 | `export_functions` | Kiểm tra export gợi ý / thống kê / thông tin user |
| TC32 | `large_star_hub` | Hub lớn với 999 nhánh (stress test kết nối) |
| TC33 | `stress_memory` | Stress test bộ nhớ với dataset lớn |
| TC34 | `measure_performance` | Test chức năng hàm `measurePerformance()` |

</details>

### 2. `run_tests.py` - Kiểm thử tự động (Auto-test)
Tự động gọi file thực thi `./SocialMedia` (yêu cầu chạy lệnh `make` trước) và giả lập thao tác nhập liệu từ người dùng (qua `stdin`) để kiểm thử **toàn bộ 14 chức năng** của menu chính trên bộ dataset lớn.

**Cách chạy:**
```bash
python scripts/run_tests.py
```

**Ví dụ Output:**
```text
════════════════════════════════════════════════════════════════════════
  KIEM THU TU DONG – SOCIAL NETWORK BFS SIMULATION
  ...
════════════════════════════════════════════════════════════════════════
  >> NHOM 1 – TAI DU LIEU (Menu 1)
  --> PASS : 1a. Tai thanh cong dataset chinh
...
════════════════════════════════════════════════════════════════════════
  KET QUA TONG HOP
  PASS : 33/33
  FAIL : 0/33
  --> Toan bo test deu PASS! Chuong trinh hoat dong on dinh.
```

### 3. `run_tc33.py` - Stress test bộ nhớ (TC33)
Script chuyên biệt để kiểm tra memory leak. Nó chạy vòng đời khắc nghiệt: Tải 50 người dùng $\rightarrow$ Xóa sạch 50 người dùng từng người một $\rightarrow$ Tải lại file từ đầu. Mục tiêu xem C++ có giải phóng bộ nhớ triệt để hay không.

**Cách chạy:**
```bash
python scripts/run_tc33.py
```

### 4. `printpath.py` - Tiện ích xuất đường dẫn
Quét thư mục `testcases/` và in ra tất cả các đường dẫn dạng text vào file `path.txt`. Phục vụ cho mục đích gõ đường dẫn tự động vào stdin cho các bài test nếu cần thiết.

**Cách chạy:**
```bash
python scripts/printpath.py
```

---

## Xử lý lỗi & tính ổn định

- **Input không hợp lệ**: `readInt()` vòng lặp cho đến khi nhận được số nguyên; xử lý `EOF`
- **File không tồn tại**: `loadUsersFromFile` / `loadConnectionsFromFile` trả về `false`, không crash
- **CSV lỗi định dạng**: Dòng không parse được bị bỏ qua (`try-catch std::stoi`)
- **ID không tồn tại**: Kiểm tra `userExists()` trước mọi thao tác
- **Tự kết nối** (`1 1`): Bị từ chối với cảnh báo
- **Kết nối trùng**: `HashSet` đảm bảo không có cạnh trùng lặp trong `adjList`
- **`maxSuggestions` âm hoặc bằng 0**: Trả về `Vector` rỗng, không crash
- **Windows console**: Tự động `SetConsoleOutputCP(CP_UTF8)` khi build trên Windows

---

## Ví dụ sử dụng

```
╔═════════════════════════════════════════════════╗
║      MANG XA HOI - MO PHONG THUAT TOAN BFS      ║
╠═════════════════════════════════════════════════╣
║  1.  Tai du lieu tu file                        ║
║  2.  Them nguoi dung                            ║
║  3.  Them ket noi                               ║
║  4.  Xoa nguoi dung                             ║
║  5.  Xoa ket noi                                ║
║  6.  Hien thi danh sach nguoi dung              ║
║  7.  Xem thong tin nguoi dung                   ║
║  8.  Tim kiem nguoi dung theo ten               ║
║  9.  Xem ban be truc tiep                       ║
║ 10.  Tim ban cua ban (BFS)                      ║
║ 11.  Goi y ket ban                              ║
║ 12.  Thong ke do thi                            ║
║ 13.  Export ket qua ra file                     ║
║ 14.  Do hieu suat                               ║
║  0.  Thoat                                      ║
╚═════════════════════════════════════════════════╝
```

**Tải dữ liệu:**
```
Lua chon cua ban: 1
Nhap duong dan file users (vd: users.csv): scripts/users.csv
Nhap duong dan file edges (vd: edges.txt): scripts/edges.txt
[OK] Tai du lieu thanh cong: 10500 nguoi dung, 165506 ket noi.
```

**Đo hiệu suất (Option 14):**
```
Lua chon cua ban: 14

============================================================
         KET QUA DO HIEU SUAT (PERFORMANCE TEST)
============================================================
  Bo du lieu: 10500 nguoi dung | 165506 ket noi
  Warm-up: 3 vong | So lan lap do: 10 lan / mau
============================================================

  [1. BFS - getFriendsOfFriends (depth = 2)]
  --------------------------------------------------------------
  Nhom            Mau    Min(us)   Avg(us)   Max(us)
  ----------------------------------------------------
  Isolated (=0)   10     0         0         0
  Low    (1-9)    10     2         9         35
  Medium (10-99)  10     231       407       1031
  High (100-999)  10     636       897       1223
  Hub    (1000+)  1      2792      3223      4127
  ----------------------------------------------------
  Throughput: 2506 ops/sec

  [2. SUGGEST FRIENDS - suggestFriends (k = 10)]
  --------------------------------------------------------------
  Nhom            Mau    Min(us)   Avg(us)   Max(us)
  ----------------------------------------------------
  Isolated (=0)   10     0         0         0
  Low    (1-9)    10     5         20        57
  Medium (10-99)  10     463       780       1923
  High (100-999)  10     1394      1724      2409
  Hub    (1000+)  1      7133      8011      9407
  ----------------------------------------------------
  Throughput: 1232 ops/sec

  [3. SEARCH BY NAME (scan luon O(N), khac o kich thuoc output)]
  --------------------------------------------------------------------
  Nhom          Keyword         Min(us)   Avg(us)   Max(us)   Ket qua
  --------------------------------------------------------------------
  High-match    "N"             602       667       777       8999
  Medium-match  "Hoa"           753       804       843       1138
  Low-match     "nh T"          692       765       908       631
  No-match      "ZZZNOTEXIST"   549       563       629       0
  --------------------------------------------------------------------

  [4. GRAPH STATS - computeGraphStats (O(V+E))]
  ----------------------------------------
  Min: 177 us  |  Med: 195 us  |  Max: 265 us
  ----------------------------------------

============================================================
  Don vi: us (microsecond) | 1ms = 1000 us
  Phuong phap: warm-up 3 vong, do 10 lan/mau, lay median
  Phan nhom: Isolated(0) / Low(1-9) / Medium(10-99) / High(100-999) / Hub(1000+)
============================================================
```

**Thêm người dùng và kết nối:**
```
Lua chon cua ban: 2
Nhap User ID: 9999
Nhap ten: Nguyen Thi Lan
[OK] Da them thanh cong nguoi dung "Nguyen Thi Lan" voi ID 9999.

Lua chon cua ban: 3
Nhap User ID 1: 9999
Nhap User ID 2: 1
[OK] Da ket noi thanh cong: User ID 9999 <-> User ID 1.
```

**Tìm kiếm người dùng:**
```
Lua chon cua ban: 8
Nhap tu khoa tim kiem: nguyen
[OK] Tim thay 312 nguoi dung phu hop voi tu khoa "nguyen":
...
Chon hoac nhap ID nguoi dung de xem chi tiet: 5
```

**Thống kê đồ thị (hỗ trợ nhiều user cùng bậc):**
```
Lua chon cua ban: 12
=== THONG KE DO THI ===
----------------------------------------
Tong so nguoi dung:    10500
Tong so ket noi:       103247
Bac trung binh:        19.67
Nhieu ban nhat (312 ban): 3 nguoi
  - Nguyen Van Hub (ID: 101)
  - Le Thi Lien (ID: 205)
  - Pham Quoc Viet (ID: 430)
It ban nhat    (0 ban): 12 nguoi
  - ...
Nguoi dung co lap:     12
----------------------------------------
```

**Các thông báo lỗi / cảnh báo điển hình:**
```
[LOI] Nguoi dung voi ID 999 khong ton tai!
[LOI] Mot trong hai User ID khong ton tai. Khong the xoa ket noi.
[LOI] Gia tri khong hop le. Vui long nhap mot so nguyen.
[LOI] Khong the mo file "data/missing.csv". Vui long kiem tra duong dan.
[LOI] Khong the tao file "output/report.txt". Vui long kiem tra quyen ghi.
[CANH BAO] Ket noi giua User ID 1 va User ID 2 da ton tai. Bo qua.
[CANH BAO] Khong the tu ket noi toi chinh minh (User ID: 5).
```

---

## Độ phức tạp thuật toán

| Thao tác | Trung bình | Tệ nhất |
|----------|-----------|---------| 
| `addUser` / `addConnection` | O(1) amortized | O(n) |
| `removeUser` | O(deg(u)) | O(deg(u) × n) |
| `getFriendsOfFriends` BFS depth-2 | O(deg(u) × avg\_deg) | O(E) |
| `suggestFriends` | O(deg(u) × avg\_deg + F log F) | O(E + n log n) |
| `searchUserByName` | O(n × L) | O(n × L × \\|keyword\\|) |
| `computeGraphStats` | O(n) | O(n²) |
| `HashMap get/put/contains` | O(1) amortized | O(n) |
| `Sort::sort` | O(n log n) | O(n²) |

> n = số người dùng, E = số cạnh, deg(u) = bậc của user u, L = độ dài tên trung bình, F = tổng số bạn chung (ứng viên gợi ý)
