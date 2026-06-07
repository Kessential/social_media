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

void SocialMedia::measurePerformance() const {
    using namespace std::chrono;

    // ----------------------------------------------------------------
    // Kiem tra du lieu
    // ----------------------------------------------------------------
    int totalUsers = getUserCount();
    int totalEdges = getEdgeCount();

    std::cout << "\n";
    std::cout << "============================================================\n";
    std::cout << "         KET QUA DO HIEU SUAT (PERFORMANCE TEST)\n";
    std::cout << "============================================================\n";
    std::cout << "  Bo du lieu: " << totalUsers << " nguoi dung | "
              << totalEdges << " ket noi\n";
    std::cout << "  Warm-up: 3 vong | So lan lap do: 10 lan / mau\n";
    std::cout << "============================================================\n";

    if (totalUsers == 0) {
        std::cerr << "[LOI] Chua co du lieu. Hay tai file truoc (Option 1).\n";
        return;
    }

    // ----------------------------------------------------------------
    // Phan loai user theo degree
    // ----------------------------------------------------------------
    const int REPEAT    = 10;   // So lan lap do moi mau
    const int WARMUP    = 3;    // So vong warm-up
    const int PER_GROUP = 10;    // So mau toi da moi nhom

    struct Group {
        std::string name;
        Vector<int> uids;
    };
    Group isolated, low, medium, high, hub;
    isolated.name = "Isolated (=0)";
    low.name      = "Low    (1-9) ";
    medium.name   = "Medium (10-99)";
    high.name     = "High (100-999)";
    hub.name      = "Hub    (1000+)";

    users.forEach([&](const int& uid, const std::string&) {
        int deg = adjList.contains(uid)
                  ? static_cast<int>(adjList.get(uid).size()) : 0;
        if      (deg == 0)    isolated.uids.push_back(uid);
        else if (deg < 10)    low.uids.push_back(uid);
        else if (deg < 100)   medium.uids.push_back(uid);
        else if (deg < 1000)  high.uids.push_back(uid);
        else                  hub.uids.push_back(uid);
    });

    // Lay toi da PER_GROUP mau moi nhom (phan bo deu)
    auto pickSamples = [&](Vector<int>& src) -> Vector<int> {
        Vector<int> picked;
        int n = static_cast<int>(src.size());
        if (n == 0) return picked;
        int step = std::max(1, n / PER_GROUP);
        for (int i = 0; i < n && static_cast<int>(picked.size()) < PER_GROUP; i += step)
            picked.push_back(src[i]);
        return picked;
    };

    // ----------------------------------------------------------------
    // Ham tien ich: do nhieu lan, tra ve danh sach thoi gian (us)
    // ----------------------------------------------------------------
    auto measureRepeated = [&](std::function<void()> fn) -> Vector<long long> {
        // Warm-up
        for (int w = 0; w < WARMUP; ++w) fn();
        // Do that
        Vector<long long> times;
        for (int r = 0; r < REPEAT; ++r) {
            auto t0 = high_resolution_clock::now();
            fn();
            auto t1 = high_resolution_clock::now();
            times.push_back(duration_cast<microseconds>(t1 - t0).count());
        }
        return times;
    };

    // Ham tinh median tu vector da sap xep
    auto median = [](Vector<long long> v) -> long long {
        if (v.empty()) return 0;
        Sort::sort(v);
        size_t n = v.size();
        return (n % 2 == 0) ? (v[n/2 - 1] + v[n/2]) / 2 : v[n/2];
    };

    // Tong hop thong ke cho mot nhom
    struct GroupStat {
        long long minT = LLONG_MAX, maxT = 0, sumT = 0;
        int count = 0;
    };

    auto aggregateGroup = [&](const Vector<int>& uids,
                              std::function<void(int)> fn) -> GroupStat {
        GroupStat gs;
        for (size_t i = 0; i < uids.size(); ++i) {
            Vector<long long> times = measureRepeated([&]{ fn(uids[i]); });
            long long med = median(times);
            long long mn  = times[0], mx = times[0];
            for (size_t j = 1; j < times.size(); ++j) {
                if (times[j] < mn) mn = times[j];
                if (times[j] > mx) mx = times[j];
            }
            gs.minT  = std::min(gs.minT,  mn);
            gs.maxT  = std::max(gs.maxT,  mx);
            gs.sumT += med;
            ++gs.count;
        }
        if (gs.count == 0) { gs.minT = 0; }
        return gs;
    };

    // Ham in bang ket qua theo nhom
    auto printGroupTable = [&](const std::string& title,
                                std::function<void(int)> fn) {
        std::cout << "\n  [" << title << "]\n";
        std::cout << "  " << std::string(62, '-') << "\n";
        std::cout << "  " << std::left
                  << std::setw(16) << "Nhom"
                  << std::setw(7)  << "Mau"
                  << std::setw(10) << "Min(us)"
                  << std::setw(10) << "Avg(us)"
                  << "Max(us)\n";
        std::cout << "  " << std::string(52, '-') << "\n";

        long long totalOps = 0;
        long long totalTime = 0;

        auto printRow = [&](Group& grp) {
            Vector<int> samples = pickSamples(grp.uids);
            if (samples.empty()) {
                std::cout << "  " << std::left << std::setw(16) << grp.name
                          << std::setw(7) << 0
                          << "(khong co mau)\n";
                return;
            }
            GroupStat gs = aggregateGroup(samples, fn);
            long long avg = gs.count > 0 ? gs.sumT / gs.count : 0;
            std::cout << "  " << std::left
                      << std::setw(16) << grp.name
                      << std::setw(7)  << gs.count
                      << std::setw(10) << gs.minT
                      << std::setw(10) << avg
                      << gs.maxT << "\n";
            totalOps  += gs.count;
            totalTime += gs.sumT;
        };

        printRow(isolated);
        printRow(low);
        printRow(medium);
        printRow(high);
        printRow(hub);

        std::cout << "  " << std::string(52, '-') << "\n";
        if (totalTime > 0 && totalOps > 0) {
            double throughput = static_cast<double>(totalOps) /
                                (static_cast<double>(totalTime) / 1e6);
            std::cout << "  Throughput: " << static_cast<long long>(throughput)
                      << " ops/sec\n";
        }
    };

    // ================================================================
    // [1] BFS - getFriendsOfFriends
    // ================================================================
    printGroupTable("1. BFS - getFriendsOfFriends (depth = 2)",
        [&](int uid) { getFriendsOfFriends(uid); });

    // ================================================================
    // [2] SUGGEST FRIENDS - suggestFriends
    // ================================================================
    printGroupTable("2. SUGGEST FRIENDS - suggestFriends (k = 10)",
        [&](int uid) { suggestFriends(uid, 10); });

    // ================================================================
    // [3] SEARCH BY NAME - 4 nhom keyword
    // ================================================================
    // Tu trich keyword tu ten user thuc trong dataset
    Vector<std::string> sampleNames;
    users.forEach([&](const int&, const std::string& name) {
        if (sampleNames.size() < 5 && !name.empty()) sampleNames.push_back(name);
    });

    std::string kwHigh   = (!sampleNames.empty() && sampleNames[0].size() >= 1)
                           ? sampleNames[0].substr(0, 1) : "a";
    std::string kwMedium = (sampleNames.size() >= 2 && sampleNames[1].size() >= 3)
                           ? sampleNames[1].substr(0, 3) : "an";
    std::string kwLow    = (sampleNames.size() >= 3 && sampleNames[2].size() >= 5)
                           ? sampleNames[2].substr(sampleNames[2].size() >= 5 ? 2 : 0, 4)
                           : "uyen";
    std::string kwNone   = "ZZZNOTEXIST999";

    struct SearchCase {
        std::string label;
        std::string keyword;
    };
    SearchCase searchCases[4] = {
        {"High-match ",  kwHigh},
        {"Medium-match", kwMedium},
        {"Low-match  ",  kwLow},
        {"No-match   ",  kwNone}
    };

    std::cout << "\n  [3. SEARCH BY NAME (scan luon O(N), khac o kich thuoc output)]\n";
    std::cout << "  " << std::string(68, '-') << "\n";
    std::cout << "  " << std::left
              << std::setw(14) << "Nhom"
              << std::setw(16) << "Keyword"
              << std::setw(10) << "Min(us)"
              << std::setw(10) << "Avg(us)"
              << std::setw(10) << "Max(us)"
              << "Ket qua\n";
    std::cout << "  " << std::string(68, '-') << "\n";

    for (int c = 0; c < 4; ++c) {
        const std::string& kw = searchCases[c].keyword;
        // Lay so ket qua truoc (dong thoi lam warm-up them 1 lan)
        int resultCount = static_cast<int>(searchUserByName(kw).size());
        // Do bang measureRepeated (da co warm-up WARMUP lan ben trong)
        Vector<long long> times = measureRepeated([&]{ searchUserByName(kw); });
        long long med = median(times);
        long long mn = times[0], mx = times[0];
        for (size_t j = 1; j < times.size(); ++j) {
            if (times[j] < mn) mn = times[j];
            if (times[j] > mx) mx = times[j];
        }
        // Hien thi keyword, cat ngan neu dai
        std::string kwDisplay = "\"" + kw + "\"";
        if (kwDisplay.size() > 13) kwDisplay = kwDisplay.substr(0, 12) + "\"";
        std::cout << "  " << std::left
                  << std::setw(14) << searchCases[c].label
                  << std::setw(16) << kwDisplay
                  << std::setw(10) << mn
                  << std::setw(10) << med
                  << std::setw(10) << mx
                  << resultCount << "\n";
    }
    std::cout << "  " << std::string(68, '-') << "\n";

    // ================================================================
    // [4] GRAPH STATS - computeGraphStats
    // ================================================================
    std::cout << "\n  [4. GRAPH STATS - computeGraphStats (O(V+E))]\n";
    std::cout << "  " << std::string(40, '-') << "\n";
    {
        Vector<long long> statsTimes = measureRepeated([&]{ computeGraphStats(); });
        long long statsMed = median(statsTimes);
        long long statsMn = statsTimes[0], statsMx = statsTimes[0];
        for (size_t j = 1; j < statsTimes.size(); ++j) {
            if (statsTimes[j] < statsMn) statsMn = statsTimes[j];
            if (statsTimes[j] > statsMx) statsMx = statsTimes[j];
        }
        std::cout << "  Min: " << statsMn << " us  |  "
                  << "Med: " << statsMed << " us  |  "
                  << "Max: " << statsMx << " us\n";
    }
    std::cout << "  " << std::string(40, '-') << "\n";

    // ================================================================
    // Tong ket
    // ================================================================
    std::cout << "\n============================================================\n";
    std::cout << "  Don vi: us (microsecond) | 1ms = 1000 us\n";
    std::cout << "  Phuong phap: warm-up " << WARMUP << " vong, do " << REPEAT
              << " lan/mau, lay median\n";
    std::cout << "  Phan nhom: Isolated(0) / Low(1-9) / Medium(10-99)"
              << " / High(100-999) / Hub(1000+)\n";
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
