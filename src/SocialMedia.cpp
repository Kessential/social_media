#include "SocialMedia.h"
#include <chrono>
#include <climits>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

// ============================================================================
// Quản lý người dùng & kết nối
// ============================================================================

bool SocialMedia::addUser(int userID, const std::string &name) {
  if (users.contains(userID)) {
    std::cerr << "[CANH BAO] User ID " << userID
              << " da ton tai trong he thong, bo qua!\n";
    return false;
  }
  users.put(userID, name);
  return true;
}

bool SocialMedia::addConnection(int userID_1, int userID_2) {
  if (userID_1 == userID_2) {
    std::cerr << "[CANH BAO] Khong the tu ket noi toi chinh minh (User ID: "
              << userID_1 << ")\n";
    return false;
  }
  if (!users.contains(userID_1) || !users.contains(userID_2)) {
    std::cerr << "[CANH BAO] Mot trong hai User ID khong ton tai: " << userID_1
              << " <-> " << userID_2 << ". Bo qua ket noi nay.\n";
    return false;
  }
  // Kiểm tra kết nối đã tồn tại chưa
  if (adjList.contains(userID_1) && adjList.get(userID_1).contains(userID_2)) {
    std::cerr << "[CANH BAO] Ket noi giua User ID " << userID_1
              << " va User ID " << userID_2 << " da ton tai. Bo qua.\n";
    return false;
  }
  adjList[userID_1].insert(userID_2);
  adjList[userID_2].insert(userID_1);
  return true;
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
  std::cout << "[OK] Da xoa nguoi dung co ID " << userID << " khoi he thong.\n";
}

void SocialMedia::removeConnection(int userID_1, int userID_2) {
  if (!users.contains(userID_1) || !users.contains(userID_2)) {
    std::cerr << "[LOI] Mot trong hai User ID khong ton tai. Khong the xoa ket "
                 "noi.\n";
    return;
  }
  // Kiểm tra kết nối có tồn tại không
  bool exists =
      adjList.contains(userID_1) && adjList.get(userID_1).contains(userID_2);
  if (!exists) {
    std::cerr << "[LOI] Ket noi giua User ID " << userID_1 << " va User ID "
              << userID_2 << " khong ton tai.\n";
    return;
  }
  adjList.get(userID_1).remove(userID_2);
  if (adjList.contains(userID_2))
    adjList.get(userID_2).remove(userID_1);
  std::cout << "[OK] Da xoa ket noi giua User ID " << userID_1 << " va User ID "
            << userID_2 << ".\n";
}

// ============================================================================
// Tải dữ liệu từ file
// ============================================================================

bool SocialMedia::loadUsersFromFile(const std::string &filepath) {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the mo file \"" << filepath
              << "\". Vui long kiem tra duong dan.\n";
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
        std::cerr << "[CANH BAO] Dinh dang dong khong hop le, bo qua: \""
                  << line << "\"\n";
      }
    }
  }
  return true;
}

bool SocialMedia::loadConnectionsFromFile(const std::string &filepath) {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the mo file \"" << filepath
              << "\". Vui long kiem tra duong dan.\n";
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
      std::cerr << "[CANH BAO] Dinh dang dong khong hop le, bo qua: \"" << line
                << "\"\n";
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
    std::cout << "\n[Thong bao] Chua co nguoi dung nao trong he thong.\n";
    return;
  }

  size_t pageSize = 20;
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
    if (totalPages <= 1)
      break;

    std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu "
                 "chinh\n";
    std::cout << "Lua chon cua ban: ";
    std::string choice;
    std::getline(std::cin, choice);
    if (choice == "n" || choice == "N") {
      if (currentPage + 1 < totalPages) {
        currentPage++;
      } else {
        std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai hoac "
                     "[Enter] de thoat.\n";
      }
    } else if (choice == "p" || choice == "P") {
      if (currentPage > 0) {
        currentPage--;
      } else {
        std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang tiep "
                     "theo.\n";
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

    Vector<int> sortedFriends = friends.toVector();
    Sort::sort(sortedFriends);

    size_t totalFriends = sortedFriends.size();
    size_t pageSize = 20;
    size_t totalPages = (totalFriends + pageSize - 1) / pageSize;
    size_t currentPage = 0;

    while (true) {
      std::cout << "\n==================================================\n";
      std::cout << "                DANH SACH BAN BE                  \n";
      std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
                << " (Hien thi " << (currentPage * pageSize + 1) << " - "
                << std::min((currentPage + 1) * pageSize, totalFriends) << " / "
                << totalFriends << " nguoi)\n";
      std::cout << "--------------------------------------------------\n";
      std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(12)
                << "ID" << "Ten\n";
      std::cout << "--------------------------------------------------\n";

      size_t start = currentPage * pageSize;
      size_t end = std::min(start + pageSize, totalFriends);

      for (size_t i = start; i < end; ++i) {
        int fid = sortedFriends[i];
        std::string fname =
            users.contains(fid) ? users.get(fid) : "User co lap";
        std::cout << "  " << std::left << std::setw(6) << (i + 1)
                  << std::setw(12) << fid << fname << "\n";
      }
      std::cout << "--------------------------------------------------\n";

      if (totalPages <= 1)
        break;

      std::cout
          << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Thoat\n";
      std::cout << "Lua chon cua ban: ";
      std::string choice;
      std::getline(std::cin, choice);
      if (choice == "n" || choice == "N") {
        if (currentPage + 1 < totalPages) {
          currentPage++;
        } else {
          std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai "
                       "hoac [Enter] de thoat.\n";
        }
      } else if (choice == "p" || choice == "P") {
        if (currentPage > 0) {
          currentPage--;
        } else {
          std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang "
                       "tiep theo.\n";
        }
      } else {
        break;
      }
    }
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
    lowerKeyword[i] =
        static_cast<char>(tolower(static_cast<unsigned char>(lowerKeyword[i])));
  }

  users.forEach([&](const int &userID, const std::string &name) {
    std::string lowerName = name;
    for (size_t i = 0; i < name.size(); ++i) {
      lowerName[i] =
          static_cast<char>(tolower(static_cast<unsigned char>(lowerName[i])));
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

const HashSet<int> *SocialMedia::getDirectConnections(int userID) const {
  if (!adjList.contains(userID))
    return nullptr;
  return &adjList.get(userID);
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
  if (maxSuggestions <= 0 || !adjList.contains(userID))
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
    if (a.mutualConnectionsCount != b.mutualConnectionsCount)
      return a.mutualConnectionsCount > b.mutualConnectionsCount;
    return a.suggestedUserID < b.suggestedUserID; // tie-breaker
  });

  if (static_cast<int>(results.size()) > maxSuggestions) {
    results.resize(static_cast<size_t>(maxSuggestions));
  }
  return results;
}

void SocialMedia::printSuggestions(int userID, int maxSuggestions) const {
  if (maxSuggestions <= 0) {
    std::cerr << "[LOI] So luong goi y phai lon hon 0.\n";
    return;
  }

  if (!users.contains(userID)) {
    std::cerr << "[LOI] Nguoi dung " << userID << " khong ton tai!\n";
    return;
  }

  Vector<FriendSuggestion> suggestions = suggestFriends(userID, maxSuggestions);

  if (suggestions.empty()) {
    std::cout << "\n[Thong bao] Khong tim thay goi y ket ban nao cho nguoi "
                 "dung nay.\n";
    return;
  }

  // In danh sách gợi ý theo trang
  size_t totalSuggestions = suggestions.size();
  size_t pageSize = 20;
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
    if (totalPages <= 1)
      break;

    std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu "
                 "chinh\n";
    std::cout << "Lua chon cua ban: ";
    std::string choice;
    std::getline(std::cin, choice);
    if (choice == "n" || choice == "N") {
      if (currentPage + 1 < totalPages) {
        currentPage++;
      } else {
        std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai hoac "
                     "[Enter] de thoat.\n";
      }
    } else if (choice == "p" || choice == "P") {
      if (currentPage > 0) {
        currentPage--;
      } else {
        std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang tiep "
                     "theo.\n";
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
    // --- Max degree ---
    if (degree > stats.maxDegree) {
      stats.maxDegree = degree;
      stats.maxDegreeUsers.clear();
      stats.maxDegreeUsers.push_back(userID);
    } else if (degree == stats.maxDegree) {
      stats.maxDegreeUsers.push_back(userID);
    }
    // --- Min degree ---
    if (degree < stats.minDegree) {
      stats.minDegree = degree;
      stats.minDegreeUsers.clear();
      stats.minDegreeUsers.push_back(userID);
    } else if (degree == stats.minDegree) {
      stats.minDegreeUsers.push_back(userID);
    }
    if (degree == 0)
      ++stats.isolatedCount;
  });
  if (stats.totalUsers == 0) {
    stats.minDegree = 0;
  }
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

  // --- Nhieu ban nhat ---
  if (!s.maxDegreeUsers.empty()) {
    std::cout << "Nhieu ban nhat (" << s.maxDegree
              << " ban): " << s.maxDegreeUsers.size() << " nguoi\n";
    for (size_t i = 0; i < s.maxDegreeUsers.size(); ++i) {
      int uid = s.maxDegreeUsers[i];
      if (users.contains(uid))
        std::cout << "  - " << users.get(uid) << " (ID: " << uid << ")\n";
    }
  }

  // --- It ban nhat ---
  if (!s.minDegreeUsers.empty()) {
    std::cout << "It ban nhat    (" << s.minDegree
              << " ban): " << s.minDegreeUsers.size() << " nguoi\n";
    for (size_t i = 0; i < s.minDegreeUsers.size(); ++i) {
      int uid = s.minDegreeUsers[i];
      if (users.contains(uid))
        std::cout << "  - " << users.get(uid) << " (ID: " << uid << ")\n";
    }
  }

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
    std::cerr << "[LOI] Khong the tao file \"" << filepath
              << "\". Vui long kiem tra quyen ghi.\n";
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
    std::cerr << "[LOI] Khong the tao file \"" << filepath
              << "\". Vui long kiem tra quyen ghi.\n";
    return false;
  }

  GraphStats s = computeGraphStats();

  file << "=== THONG KE DO THI ===\n";
  file << std::string(40, '-') << "\n";
  file << "Tong so nguoi dung:    " << s.totalUsers << "\n";
  file << "Tong so ket noi:       " << s.totalEdges << "\n";
  file << "Bac trung binh:        " << std::fixed << std::setprecision(2)
       << s.avgDegree << "\n";

  // --- Nhieu ban nhat ---
  if (!s.maxDegreeUsers.empty()) {
    file << "Nhieu ban nhat (" << s.maxDegree
         << " ban): " << s.maxDegreeUsers.size() << " nguoi\n";
    for (size_t i = 0; i < s.maxDegreeUsers.size(); ++i) {
      int uid = s.maxDegreeUsers[i];
      if (users.contains(uid))
        file << "  - " << users.get(uid) << " (ID: " << uid << ")\n";
    }
  }

  // --- It ban nhat ---
  if (!s.minDegreeUsers.empty()) {
    file << "It ban nhat    (" << s.minDegree
         << " ban): " << s.minDegreeUsers.size() << " nguoi\n";
    for (size_t i = 0; i < s.minDegreeUsers.size(); ++i) {
      int uid = s.minDegreeUsers[i];
      if (users.contains(uid))
        file << "  - " << users.get(uid) << " (ID: " << uid << ")\n";
    }
  }

  file << "Nguoi dung co lap:     " << s.isolatedCount << "\n";
  file << std::string(40, '-') << "\n";

  // Xuất danh sách tất cả người dùng kèm số bạn bè
  file << "\n=== DANH SACH NGUOI DUNG ===\n";
  struct ExportEntry {
    int uid;
    std::string name;
    int deg;
  };
  Vector<ExportEntry> entries;
  users.forEach([&](const int &uid, const std::string &name) {
    int deg = adjList.contains(uid) ? (int)adjList.get(uid).size() : 0;
    entries.push_back({uid, name, deg});
  });
  Sort::sort(entries, [](const ExportEntry &a, const ExportEntry &b) {
    return a.uid < b.uid;
  });
  for (size_t i = 0; i < entries.size(); ++i) {
    file << "ID: " << entries[i].uid << " | Ten: " << entries[i].name
         << " | Ban be: " << entries[i].deg << "\n";
  }

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
    std::cerr << "[LOI] Khong the tao file \"" << filepath
              << "\". Vui long kiem tra quyen ghi.\n";
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
    using namespace std::chrono;

    std::cout << "\n";
    std::cout << "============================================================\n";
    std::cout << "           KET QUA DO HIEU SUAT (PERFORMANCE TEST)          \n";
    std::cout << "============================================================\n";
    std::cout << "  Bo du lieu: " << getUserCount() << " nguoi dung | "
              << getEdgeCount() << " ket noi\n";
    std::cout << "------------------------------------------------------------\n";

    if (!users.contains(testUserID)) {
        std::cerr << "[LOI] Nguoi dung " << testUserID << " khong ton tai!\n";
        return;
    }

    // Thu thap va sap xep toan bo user ID
    Vector<int> allUsers;
    users.forEach([&](const int& uid, const std::string&) {
        allUsers.push_back(uid);
    });
    Sort::sort(allUsers);

    int totalUsers = static_cast<int>(allUsers.size());
    int sampleCount = std::min(totalUsers, 20);

    // Header bang chi tiet
    std::cout << "  " << std::left
              << std::setw(12) << "User ID"
              << std::setw(12) << "So ban"
              << std::setw(18) << "BFS (us)"
              << "Suggest (us)\n";
    std::cout << "  " << std::string(54, '-') << "\n";

    long long bfsMin = LLONG_MAX, bfsMax = 0, bfsSum = 0;
    long long sugMin = LLONG_MAX, sugMax = 0, sugSum = 0;

    for (int i = 0; i < sampleCount; ++i) {
        int idx = (totalUsers / sampleCount) * i;
        int uid = allUsers[idx];
        int deg = adjList.contains(uid)
                      ? static_cast<int>(adjList.get(uid).size()) : 0;

        // Do BFS (getFriendsOfFriends)
        auto t0 = high_resolution_clock::now();
        getFriendsOfFriends(uid);
        auto t1 = high_resolution_clock::now();
        long long bfsUs = duration_cast<microseconds>(t1 - t0).count();

        // Do Suggest (suggestFriends)
        auto t2 = high_resolution_clock::now();
        suggestFriends(uid, 10);
        auto t3 = high_resolution_clock::now();
        long long sugUs = duration_cast<microseconds>(t3 - t2).count();

        bfsSum += bfsUs;
        sugSum += sugUs;
        if (bfsUs < bfsMin) bfsMin = bfsUs;
        if (bfsUs > bfsMax) bfsMax = bfsUs;
        if (sugUs < sugMin) sugMin = sugUs;
        if (sugUs > sugMax) sugMax = sugUs;

        std::cout << "  " << std::left
                  << std::setw(12) << uid
                  << std::setw(12) << deg
                  << std::setw(18) << bfsUs
                  << sugUs << "\n";
    }

    // Thong ke tong hop
    long long bfsAvg = sampleCount > 0 ? bfsSum / sampleCount : 0;
    long long sugAvg = sampleCount > 0 ? sugSum / sampleCount : 0;

    std::cout << "  " << std::string(54, '-') << "\n";
    std::cout << "  " << std::left << std::setw(24) << "Min:"
              << std::setw(18) << bfsMin << sugMin << "\n";
    std::cout << "  " << std::left << std::setw(24) << "Trung binh (avg):"
              << std::setw(18) << bfsAvg << sugAvg << "\n";
    std::cout << "  " << std::left << std::setw(24) << "Max:"
              << std::setw(18) << bfsMax << sugMax << "\n";
    std::cout << "============================================================\n";
    std::cout << "  Don vi: us (microsecond) | 1 ms = 1000 us\n";
    std::cout << "  So user mau: " << sampleCount
              << " (phan bo deu trong " << totalUsers << " user)\n";
    std::cout << "============================================================\n";
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
