#include "SocialMedia.h"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

// ============================================================================
// Quản lý người dùng & kết nối
// ============================================================================

bool SocialMedia::addUser(int userID, const std::string &name) {
  if (users.contains(userID)) {
    std::cerr << "[CANH BAO] User ID " << userID << " da ton tai, bo qua!\n";
    return false;
  }
  users.put(userID, name);
  return true;
}

void SocialMedia::addConnection(int userID_1, int userID_2) {
  if (userID_1 == userID_2) {
    std::cerr << "[CANH BAO] Tu ket noi toi chinh minh: " << userID_1 << "\n";
    return;
  }
  if (!users.contains(userID_1) || !users.contains(userID_2)) {
    std::cerr << "[CANH BAO] Ket noi toi nguoi dung khong ton tai: " << userID_1
              << " <-> " << userID_2 << "\n";
    return;
  }
  // Kiểm tra kết nối đã tồn tại chưa
  if (adjList.contains(userID_1) && adjList.get(userID_1).contains(userID_2)) {
    std::cerr << "[CANH BAO] Ket noi " << userID_1 << " <-> " << userID_2
              << " da ton tai, bo qua!\n";
    return;
  }
  adjList[userID_1].insert(userID_2);
  adjList[userID_2].insert(userID_1);
}

void SocialMedia::removeUser(int userID) {
  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return;
  }

  // Xóa userID khỏi danh sách bạn bè của tất cả người kết nối
  if (adjList.contains(userID)) {
    Vector<int> neighbors = adjList.get(userID).toVector();
    for (size_t i = 0; i < neighbors.size(); ++i) {
      if (adjList.contains(neighbors[i])) {
        adjList.get(neighbors[i]).remove(userID);
      }
    }
    adjList.remove(userID);
  }

  users.remove(userID);
  std::cout << "[OK] Da xoa nguoi dung " << userID << ".\n";
}

void SocialMedia::removeConnection(int userID_1, int userID_2) {
  if (!users.contains(userID_1) || !users.contains(userID_2)) {
    std::cerr << "[LOI] Nguoi dung khong ton tai!\n";
    return;
  }
  // Kiểm tra kết nối có tồn tại không
  bool exists = adjList.contains(userID_1) &&
                adjList.get(userID_1).contains(userID_2);
  if (!exists) {
    std::cerr << "[LOI] Ket noi " << userID_1 << " <-> " << userID_2
              << " khong ton tai!\n";
    return;
  }
  adjList.get(userID_1).remove(userID_2);
  if (adjList.contains(userID_2))
    adjList.get(userID_2).remove(userID_1);
  std::cout << "[OK] Da xoa ket noi " << userID_1 << " <-> " << userID_2
            << ".\n";
}

// ============================================================================
// Tải dữ liệu từ file
// ============================================================================

bool SocialMedia::loadUsersFromFile(const std::string &filepath) {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the mo duoc file: " << filepath << "\n";
    return false;
  }
  std::string line;
  while (std::getline(file, line)) {
    if (line.empty())
      continue;
    std::stringstream ss(line);
    std::string strUserID, name;
    if (std::getline(ss, strUserID, ',') && std::getline(ss, name)) {
      try {
        int id = std::stoi(strUserID);
        addUser(id, name);
      } catch (const std::exception &e) {
        std::cerr << "[CANH BAO] Dong khong hop le, bo qua: \"" << line
                  << "\"\n";
      }
    }
  }
  return true;
}

bool SocialMedia::loadConnectionsFromFile(const std::string &filepath) {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the mo duoc file: " << filepath << "\n";
    return false;
  }
  std::string line;
  while (std::getline(file, line)) {
    if (line.empty())
      continue;
    std::stringstream ss(line);
    int userID_1, userID_2;
    if (ss >> userID_1 >> userID_2) {
      addConnection(userID_1, userID_2);
    } else {
      std::cerr << "[CANH BAO] Dong khong hop le, bo qua: \"" << line << "\"\n";
    }
  }
  return true;
}

// ============================================================================
// Hiển thị
// ============================================================================

void SocialMedia::listUsers() const {
  struct UserListEntry {
    int userID;
    std::string username;
    int friendCount;
  };

  Vector<UserListEntry> userList;
  users.forEach([&](const int &userID, const std::string &username) {
    int friendCount = 0;
    if (adjList.contains(userID)) {
      friendCount = static_cast<int>(adjList.get(userID).size());
    }
    userList.push_back({userID, username, friendCount});
  });

  Sort::sort(userList, [](const UserListEntry &a, const UserListEntry &b) {
    return a.userID < b.userID;
  });

  size_t totalUsers = userList.size();
  if (totalUsers == 0) {
    std::cout << "\n[Thong bao] Khong co nguoi dung nao trong mang xa hoi!\n";
    return;
  }

  size_t pageSize = 50;
  size_t totalPages = (totalUsers + pageSize - 1) / pageSize;
  if (totalPages == 0)
    totalPages = 1;

  size_t currentPage = 0;
  while (true) {
    std::cout << "\n==================================================\n";
    std::cout << "              DANH SACH NGUOI DUNG                \n";
    std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
              << " (Hien thi " << (currentPage * pageSize + 1) << " - "
              << std::min((currentPage + 1) * pageSize, totalUsers) << " / "
              << totalUsers << " nguoi)\n";
    std::cout << "--------------------------------------------------\n";
    std::cout << "  " << std::left << std::setw(12) << "ID" << std::setw(25)
              << "Ten" << "So ban be\n";
    std::cout << "--------------------------------------------------\n";

    size_t start = currentPage * pageSize;
    size_t end = start + pageSize;
    if (end > totalUsers)
      end = totalUsers;

    for (size_t i = start; i < end; ++i) {
      std::cout << "  " << std::left << std::setw(12) << userList[i].userID
                << std::setw(25) << userList[i].username
                << userList[i].friendCount << "\n";
    }

    std::cout << "--------------------------------------------------\n";
    std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu "
                 "chinh\n";
    std::cout << "Lua chon cua ban: ";
    std::string choice;
    std::getline(std::cin, choice);
    if (choice == "n" || choice == "N") {
      if (currentPage + 1 < totalPages) {
        currentPage++;
      } else {
        std::cout << "[Thong bao] Da o trang cuoi cung!\n";
      }
    } else if (choice == "p" || choice == "P") {
      if (currentPage > 0) {
        currentPage--;
      } else {
        std::cout << "[Thong bao] Da o trang dau tien!\n";
      }
    } else {
      break;
    }
  }
}

void SocialMedia::printUserInfo(int userID) const {
  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return;
  }

  std::cout << "\n==================================================\n";
  std::cout << "              THONG TIN NGUOI DUNG               \n";
  std::cout << "==================================================\n";
  std::cout << std::left << std::setw(15) << "  ID:" << userID << "\n";
  std::cout << std::left << std::setw(15) << "  Ten:" << users.get(userID)
            << "\n";

  if (adjList.contains(userID)) {
    const HashSet<int> &friends = adjList.get(userID);
    std::cout << std::left << std::setw(15) << "  So ban be:" << friends.size()
              << "\n";
    std::cout << "==================================================\n";
    std::cout << "                DANH SACH BAN BE                  \n";
    std::cout << "--------------------------------------------------\n";
    std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(12)
              << "ID" << "Ten\n";
    std::cout << "--------------------------------------------------\n";

    Vector<int> sortedFriends = friends.toVector();
    Sort::sort(sortedFriends);

    for (size_t i = 0; i < sortedFriends.size(); ++i) {
      int fid = sortedFriends[i];
      std::string fname = users.contains(fid) ? users.get(fid) : "User co lap";
      std::cout << "  " << std::left << std::setw(6) << (i + 1) << std::setw(12)
                << fid << fname << "\n";
    }
    std::cout << "--------------------------------------------------\n";
  } else {
    std::cout << std::left << std::setw(15) << "  So ban be:" << 0 << "\n";
    std::cout << "==================================================\n";
  }
}

// ============================================================================
// Tìm kiếm
// ============================================================================

Vector<int> SocialMedia::searchUserByName(const std::string &keyword) const {
  Vector<int> results;
  std::string lowerKeyword = keyword;
  for (size_t i = 0; i < keyword.size(); ++i) {
    lowerKeyword = static_cast<char>(tolower(lowerKeyword[i]));
  }

  users.forEach([&](const int &userID, const std::string &name) {
    std::string lowerName = name;
    for (size_t i = 0; i < name.size(); ++i) {
      lowerName = static_cast<char>(tolower(lowerName[i]));
    }
    // Tìm substring
    if (lowerName.find(lowerKeyword) != std::string::npos) {
      results.push_back(userID);
    }
  });
  return results;
}

// ============================================================================
// Thuật toán lõi — BFS
// ============================================================================

HashSet<int> SocialMedia::getDirectConnections(int userID) const {
  if (!adjList.contains(userID))
    return HashSet<int>();
  return adjList.get(userID);
}

HashSet<int> SocialMedia::getFriendsOfFriends(int userID) const {
  HashSet<int> friendsOfFriends;
  if (!adjList.contains(userID))
    return friendsOfFriends;

  HashSet<int> visited;
  Queue<BFSNode> q;

  visited.insert(userID);
  q.push({userID, 0});

  while (!q.empty()) {
    BFSNode curr = q.front();
    q.pop();

    if (curr.depth == 2) {
      friendsOfFriends.insert(curr.userID);
      continue;
    }

    if (curr.depth < 2 && adjList.contains(curr.userID)) {
      adjList.get(curr.userID).forEach([&](int neighbor) {
        if (!visited.contains(neighbor)) {
          visited.insert(neighbor);
          q.push({neighbor, curr.depth + 1});
        }
      });
    }
  }
  return friendsOfFriends;
}

Vector<FriendSuggestion> SocialMedia::suggestFriends(int userID,
                                                     int maxSuggestions) const {
  if (maxSuggestions < 0 || !adjList.contains(userID))
    return Vector<FriendSuggestion>();

  const HashSet<int> &directConns = adjList.get(userID);
  HashMap<int, Vector<int>> mutualMap;

  // Duyệt từng bạn trực tiếp
  directConns.forEach([&](int friendID) {
    if (!adjList.contains(friendID))
      return;
    // Duyệt bạn của bạn
    adjList.get(friendID).forEach([&](int fofID) {
      if (fofID != userID && !directConns.contains(fofID)) {
        mutualMap[fofID].push_back(friendID);
      }
    });
  });

  // Xây dựng danh sách kết quả
  Vector<FriendSuggestion> results;
  mutualMap.forEach([&](const int &candidateID, const Vector<int> &mutuals) {
    FriendSuggestion fs;
    fs.suggestedUserID = candidateID;
    fs.mutualConnectionsCount = static_cast<int>(mutuals.size());
    fs.mutualConnectionsIDs = mutuals;
    results.push_back(fs);
  });

  // Sắp xếp giảm dần theo số bạn chung
  Sort::sort(results, [](const FriendSuggestion &a, const FriendSuggestion &b) {
    return a.mutualConnectionsCount > b.mutualConnectionsCount;
  });

  if (static_cast<int>(results.size()) > maxSuggestions) {
    results.resize(static_cast<size_t>(maxSuggestions));
  }
  return results;
}

void SocialMedia::printSuggestions(int userID, int maxSuggestions) const {
  if (maxSuggestions < 0) {
    std::cerr << "[LOI] So nhap vao khong hop le!\n";
    return;
  }

  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return;
  }

  Vector<FriendSuggestion> suggestions = suggestFriends(userID, maxSuggestions);

  if (suggestions.empty()) {
    std::cout << "\n[Thong bao] Khong co goi y ket ban nao phu hop!\n";
    return;
  }

  // In danh sách gợi ý theo trang
  size_t totalSuggestions = suggestions.size();
  size_t pageSize = 50;
  size_t totalPages = (totalSuggestions + pageSize - 1) / pageSize;
  if (totalPages == 0)
    totalPages = 1;
  size_t currentPage = 0;

  while (true) {
    std::cout << "\n==================================================\n";
    std::cout << "              GOI Y KET BAN CHO:                 \n";
    std::cout << "  " << users.get(userID) << " (ID: " << userID << ")\n";
    std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
              << " (Hien thi " << (currentPage * pageSize + 1) << " - "
              << std::min((currentPage + 1) * pageSize, totalSuggestions)
              << " / " << totalSuggestions << " goi y)\n";
    std::cout << "==================================================\n";

    size_t start = currentPage * pageSize;
    size_t end = start + pageSize;
    if (end > totalSuggestions)
      end = totalSuggestions;

    for (size_t i = start; i < end; ++i) {
      const FriendSuggestion &s = suggestions[i];
      std::string sname = users.contains(s.suggestedUserID)
                              ? users.get(s.suggestedUserID)
                              : "Unknown User";

      std::string idStr = "(ID: " + std::to_string(s.suggestedUserID) + ")";
      std::cout << " " << std::right << std::setw(3) << (i + 1) << ". "
                << std::left << std::setw(25) << sname << " " << std::left
                << std::setw(12) << idStr << " | "
                << "Ban chung: " << s.mutualConnectionsCount << "\n";

      std::cout << "    [Goi y qua: ";
      size_t printCount = std::min(s.mutualConnectionsIDs.size(), size_t(3));
      for (size_t j = 0; j < printCount; ++j) {
        int mid = s.mutualConnectionsIDs[j];
        std::string mname =
            users.contains(mid) ? users.get(mid) : std::to_string(mid);
        std::cout << mname;
        if (j + 1 < printCount)
          std::cout << ", ";
      }
      if (s.mutualConnectionsIDs.size() > printCount) {
        std::cout << " va " << (s.mutualConnectionsIDs.size() - printCount)
                  << " nguoi khac";
      }
      std::cout << "]\n\n";
    }

    std::cout << "--------------------------------------------------\n";
    std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu "
                 "chinh\n";
    std::cout << "Lua chon cua ban: ";
    std::string choice;
    std::getline(std::cin, choice);
    if (choice == "n" || choice == "N") {
      if (currentPage + 1 < totalPages) {
        currentPage++;
      } else {
        std::cout << "[Thong bao] Da o trang cuoi cung!\n";
      }
    } else if (choice == "p" || choice == "P") {
      if (currentPage > 0) {
        currentPage--;
      } else {
        std::cout << "[Thong bao] Da o trang dau tien!\n";
      }
    } else {
      break;
    }
  }
}

// ============================================================================
// Thống kê đồ thị
// ============================================================================
GraphStats SocialMedia::computeGraphStats() const {
  GraphStats stats;
  stats.totalUsers = static_cast<int>(users.size());
  stats.totalEdges = getEdgeCount();
  stats.minDegree = stats.totalUsers + 1;
  long long degreeSum = 0;
  users.forEach([&](const int &userID, const std::string &) {
    int degree = 0;
    if (adjList.contains(userID))
      degree = static_cast<int>(adjList.get(userID).size());
    degreeSum += degree;
    if (degree > stats.maxDegree) {
      stats.maxDegree = degree;
      stats.maxDegreeUser = userID;
    }
    if (degree < stats.minDegree) {
      stats.minDegree = degree;
      stats.minDegreeUser = userID;
    }
    if (degree == 0)
      ++stats.isolatedCount;
  });
  stats.avgDegree = stats.totalUsers > 0
                        ? static_cast<double>(degreeSum) / stats.totalUsers
                        : 0.0;
  return stats;
}

void SocialMedia::printGraphStats() const {
  GraphStats s = computeGraphStats();

  std::cout << "\n=== THONG KE DO THI ===\n";
  std::cout << std::string(40, '-') << "\n";
  std::cout << "Tong so nguoi dung:    " << s.totalUsers << "\n";
  std::cout << "Tong so ket noi:       " << s.totalEdges << "\n";
  std::cout << "Bac trung binh:        " << std::fixed << std::setprecision(2)
            << s.avgDegree << "\n";

  if (s.maxDegreeUser != -1 && users.contains(s.maxDegreeUser))
    std::cout << "Nguoi co nhieu ban nhat: " << users.get(s.maxDegreeUser)
              << " (ID: " << s.maxDegreeUser << ", " << s.maxDegree
              << " ban)\n";

  if (s.minDegreeUser != -1 && users.contains(s.minDegreeUser))
    std::cout << "Nguoi co it ban nhat:    " << users.get(s.minDegreeUser)
              << " (ID: " << s.minDegreeUser << ", " << s.minDegree
              << " ban)\n";

  std::cout << "Nguoi dung co lap:     " << s.isolatedCount << "\n";
  std::cout << std::string(40, '-') << "\n";
}

// ============================================================================
// Export kết quả ra file
// ============================================================================

bool SocialMedia::exportSuggestions(int userID, int maxSuggestions,
                                    const std::string &filepath) const {
  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return false;
  }

  std::ofstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the tao file: " << filepath << "\n";
    return false;
  }

  Vector<FriendSuggestion> suggestions = suggestFriends(userID, maxSuggestions);

  file << "=== GOI Y KET BAN cho " << users.get(userID) << " (ID: " << userID
       << ") ===\n";
  file << "Tong so goi y: " << suggestions.size() << "\n\n";

  for (size_t i = 0; i < suggestions.size(); ++i) {
    const FriendSuggestion &s = suggestions[i];
    file << (i + 1) << ". ";
    if (users.contains(s.suggestedUserID))
      file << users.get(s.suggestedUserID);
    else
      file << "User " << s.suggestedUserID;

    file << " (ID: " << s.suggestedUserID << ")"
         << " | Ban chung: " << s.mutualConnectionsCount << " | Qua: ";

    for (size_t j = 0; j < s.mutualConnectionsIDs.size(); ++j) {
      int mid = s.mutualConnectionsIDs[j];
      if (users.contains(mid))
        file << users.get(mid) << "(" << mid << ")";
      else
        file << mid;
      if (j + 1 < s.mutualConnectionsIDs.size())
        file << ", ";
    }
    file << "\n";
  }

  file.close();
  return true;
}

bool SocialMedia::exportGraphStats(const std::string &filepath) const {
  std::ofstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the tao file: " << filepath << "\n";
    return false;
  }

  GraphStats s = computeGraphStats();

  file << "=== THONG KE DO THI ===\n";
  file << std::string(40, '-') << "\n";
  file << "Tong so nguoi dung:    " << s.totalUsers << "\n";
  file << "Tong so ket noi:       " << s.totalEdges << "\n";
  file << "Bac trung binh:        " << std::fixed << std::setprecision(2)
       << s.avgDegree << "\n";

  if (s.maxDegreeUser != -1 && users.contains(s.maxDegreeUser))
    file << "Nguoi co nhieu ban nhat: " << users.get(s.maxDegreeUser)
         << " (ID: " << s.maxDegreeUser << ", " << s.maxDegree << " ban)\n";

  if (s.minDegreeUser != -1 && users.contains(s.minDegreeUser))
    file << "Nguoi co it ban nhat:    " << users.get(s.minDegreeUser)
         << " (ID: " << s.minDegreeUser << ", " << s.minDegree << " ban)\n";

  file << "Nguoi dung co lap:     " << s.isolatedCount << "\n";
  file << std::string(40, '-') << "\n";

  // Xuất danh sách tất cả người dùng kèm số bạn bè
  file << "\n=== DANH SACH NGUOI DUNG ===\n";
  users.forEach([&](const int &uid, const std::string &name) {
    int deg = 0;
    if (adjList.contains(uid))
      deg = static_cast<int>(adjList.get(uid).size());
    file << "ID: " << uid << " | Ten: " << name << " | Ban be: " << deg << "\n";
  });

  file.close();
  return true;
}

bool SocialMedia::exportUserConnections(int userID,
                                        const std::string &filepath) const {
  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return false;
  }

  std::ofstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the tao file: " << filepath << "\n";
    return false;
  }

  file << "=== THONG TIN NGUOI DUNG ===\n";
  file << "ID:   " << userID << "\n";
  file << "Ten:  " << users.get(userID) << "\n";

  if (adjList.contains(userID)) {
    const HashSet<int> &friends = adjList.get(userID);
    file << "So ban be: " << friends.size() << "\n";
    file << "\nDanh sach ban be:\n";
    friends.forEach([&](int fid) {
      std::string fname = "";
      if (users.contains(fid))
        fname = users.get(fid);
      file << "  " << fid << " - " << fname << "\n";
    });
  } else {
    file << "So ban be: 0\n";
  }

  // Thêm bạn của bạn (BFS)
  HashSet<int> fof = getFriendsOfFriends(userID);
  file << "\nBan cua ban (BFS, do sau 2): " << fof.size() << " nguoi\n";
  fof.forEach([&](int fid) {
    std::string fname = "";
    if (users.contains(fid))
      fname = users.get(fid);
    file << "  " << fid << " - " << fname << "\n";
  });

  file.close();
  return true;
}

// ============================================================================
// Đo hiệu suất
// ============================================================================

void SocialMedia::measurePerformance(int testUserID) const {
  std::cout << "\n=== DO HIEU SUAT (User ID: " << testUserID << ") ===\n";
  std::cout << std::string(50, '-') << "\n";

  if (!users.contains(testUserID)) {
    std::cerr << "[LOI] Nguoi dung " << testUserID << " khong ton tai!\n";
    return;
  }

  // 1. BFS - Tìm bạn của bạn
  {
    auto start = std::chrono::high_resolution_clock::now();
    HashSet<int> fof = getFriendsOfFriends(testUserID);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration =
        std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "BFS (ban cua ban):       " << std::setw(10)
              << duration.count() << " us | Tim thay: " << fof.size()
              << " nguoi\n";
  }

  // 2. Gợi ý kết bạn
  {
    auto start = std::chrono::high_resolution_clock::now();
    Vector<FriendSuggestion> suggestions = suggestFriends(testUserID, 10);
    auto end = std::chrono::high_resolution_clock::now();
    auto duration =
        std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "Goi y ket ban (top 10):  " << std::setw(10)
              << duration.count() << " us | Ket qua: " << suggestions.size()
              << " goi y\n";
  }

  // 3. Export gợi ý kết bạn ra file
  {
    auto start = std::chrono::high_resolution_clock::now();
#ifdef _WIN32
    exportSuggestions(testUserID, 10, "NUL");
#else
    exportSuggestions(testUserID, 10, "/dev/null");
#endif
    auto end = std::chrono::high_resolution_clock::now();
    auto duration =
        std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "Export goi y (top 10):   " << std::setw(10)
              << duration.count() << " us\n";
  }

  std::cout << std::string(50, '-') << "\n";
  std::cout << "Tong so nguoi dung: " << users.size()
            << " | Tong so ket noi: " << getEdgeCount() << "\n";
}

// ============================================================================
// Helpers
// ============================================================================

bool SocialMedia::userExists(int userID) const {
  return users.contains(userID);
}

std::string SocialMedia::getUserName(int userID) const {
  if (users.contains(userID))
    return users.get(userID);
  return "";
}

int SocialMedia::getUserCount() const { return static_cast<int>(users.size()); }

int SocialMedia::getEdgeCount() const {
  int total = 0;
  adjList.forEach([&](const int &, const HashSet<int> &neighbors) {
    total += static_cast<int>(neighbors.size());
  });
  return total / 2; // Mỗi cạnh được đếm 2 lần (vô hướng)
}