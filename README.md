# Mô Phỏng Mạng Xã Hội — BFS Friend Suggestion

Ứng dụng console C++ mô phỏng mạng xã hội, sử dụng thuật toán **BFS (Breadth-First Search)** để tìm "bạn của bạn" và gợi ý kết bạn dựa trên số bạn chung.

---

## Cấu trúc thư mục

```
FS/
├── Makefile
├── README.md
├── scripts/
│   ├── generate_dataset.py   # Sinh dữ liệu 10,500+ người dùng & 31 test cases
│   └── printpath.py
└── src/
    ├── main.cpp              # Entry point, menu tương tác 14 chức năng
    ├── SocialMedia.h         # Khai báo class SocialMedia, struct BFSNode, FriendSuggestion, GraphStats
    ├── SocialMedia.cpp       # Toàn bộ logic nghiệp vụ (~764 dòng)
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
| 6 | Hiển thị danh sách người dùng | Phân trang 50/trang, sắp xếp theo ID tăng dần, hiển thị số bạn bè |
| 7 | Xem thông tin người dùng | ID, tên, danh sách bạn bè sắp xếp theo ID |
| 8 | Tìm kiếm theo tên | Không phân biệt hoa/thường, tìm substring |
| 9 | Xem bạn bè trực tiếp | Danh sách bạn bậc 1 kèm tên |
| 10 | Tìm bạn của bạn (BFS) | BFS độ sâu 2, phân trang 50/trang, điều hướng [n]/[p]/[Enter] |
| 11 | Gợi ý kết bạn | Sắp xếp giảm dần theo số bạn chung (tie-breaker: ID tăng dần), phân trang, hiển thị tối đa 3 bạn chung |
| 12 | Thống kê đồ thị | Tổng user/cạnh, bậc TB, **tất cả** user nhiều/ít bạn nhất, user cô lập |
| 13 | Export ra file | Export gợi ý / thống kê / thông tin user ra file `.txt` |
| 14 | Đo hiệu suất | Benchmark BFS, gợi ý kết bạn và export (đơn vị microsecond) |

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

**Yêu cầu:** `g++` hỗ trợ C++17, `make`

```bash
# Build
make

# Chạy (Windows)
.\SocialMedia.exe

# Chạy (Linux/macOS)
./SocialMedia

# Rebuild sạch
make rebuild

# Dọn build artifacts
make clean
```

Output binary: `SocialMedia.exe` (Windows) / `SocialMedia` (Linux/macOS)  
Object files: `build/*.o`

---

## Sinh dữ liệu kiểm thử

```bash
python scripts/generate_dataset.py
```

Script tạo 2 file chính tại `scripts/`:
- `users.csv` — **10,500 người dùng** (70% tên tiếng Việt, 30% tiếng Anh)
- `edges.txt` — khoảng **~100,000+ cạnh kết nối**

Mô hình đồ thị mô phỏng mạng xã hội thực tế (scale-free):
- **50 cộng đồng** với 80,000 cạnh nội bộ dày đặc (intra-community)
- **20,000 cạnh inter-community** làm cầu nối giữa các cộng đồng
- **100 node "influencer/hub"** với 15,000 cạnh siêu kết nối (phân phối lũy thừa)

### 31 Test Cases

Script cũng sinh **31 test cases** vào `scripts/testcases/<tên>/`, mỗi thư mục gồm `users.csv`, `edges.txt`, `expected.txt`.

| Nhóm | Test cases | Mô tả |
|------|-----------|-------|
| Cấu trúc đồ thị | TC01–TC06, TC25 | User cô lập, clique K5, đồ thị sao, chuỗi, thành phần rời rạc, vòng tròn |
| Biên & đặc biệt | TC07–TC09, TC23 | Tự kết nối, trùng cạnh, user duy nhất, ID cực hạn (0, âm, INT_MAX) |
| Stress test | TC10, TC12, TC24 | Hub 999 nhánh, giới hạn `maxSuggestions`, `maxSuggestions=0` |
| Xóa & cập nhật | TC18, TC19, TC31 | Xóa user rồi gợi ý, xóa kết nối rồi BFS, kiểm tra đối xứng adjList |
| Xử lý lỗi input | TC14–TC17, TC20–TC22, TC27–TC30 | `maxSuggestions` âm, user không tồn tại, file không tìm thấy, CSV lỗi định dạng, tên có dấu phẩy |
| Tính đúng đắn | TC11, TC13, TC26 | Tam giác + đuôi, đồ thị kim cương (2 bạn chung), gọi hàm khi không có kết nối |

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

**Tải dữ liệu và đo hiệu suất:**
```
Chao mung ban den voi chuong trinh Mo phong Mang Xa Hoi!
He thong su dung thuat toan BFS de tim ban cua ban va goi y ket ban.

Lua chon cua ban: 1
Nhap duong dan file users (vd: users.csv): scripts/users.csv
Nhap duong dan file edges (vd: edges.txt): scripts/edges.txt
[OK] Tai du lieu thanh cong: 10500 nguoi dung, 103247 ket noi.

Lua chon cua ban: 14
Nhap User ID de do hieu suat: 1
=== DO HIEU SUAT — User ID: 1 ===
--------------------------------------------------
BFS (ban cua ban):            312 us  | Ket qua: 847 nguoi
Goi y ket ban (top 10):       198 us  | Ket qua: 10 goi y
Export goi y (top 10):         45 us
--------------------------------------------------
Tong so nguoi dung: 10500 | Tong so ket noi: 103247
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
```

**Phân trang (điều hướng):**
```
Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu chinh
Lua chon cua ban: n
[Thong bao] Day la trang cuoi. Nhan [p] de quay lai hoac [Enter] de thoat.
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

**Export kết quả:**
```
Lua chon cua ban: 13
╔═════════════════════════════════════════════════╗
║               EXPORT KET QUA RA FILE            ║
╠═════════════════════════════════════════════════╣
║  1. Export danh sach goi y ket ban              ║
║  2. Export bao cao thong ke do thi              ║
║  3. Export chi tiet thong tin & ban be user     ║
║  0. Quay lai menu chinh                         ║
╚═════════════════════════════════════════════════╝
```

---

## Độ phức tạp thuật toán

| Thao tác | Trung bình | Tệ nhất |
|----------|-----------|---------| 
| `addUser` / `addConnection` | O(1) amortized | O(n) |
| `removeUser` | O(deg(u)) | O(n) |
| `getFriendsOfFriends` BFS depth-2 | O(deg(u) × avg\_deg) | O(E) |
| `suggestFriends` | O(deg(u) × avg\_deg + k log k) | O(E + n log n) |
| `searchUserByName` | O(n × \|keyword\|) | O(n × L) |
| `computeGraphStats` | O(n) | O(n) |
| `HashMap get/put/contains` | O(1) amortized | O(n) |
| `Sort::sort` | O(n log n) | O(n²) |

> n = số người dùng, E = số cạnh, deg(u) = bậc của user u, L = độ dài tên trung bình, k = số ứng viên gợi ý
