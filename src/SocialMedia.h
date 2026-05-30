#pragma once
#include "CustomHashMap.h"
#include "CustomHashSet.h"
#include "CustomQueue.h"
#include "CustomSort.h"
#include "CustomVector.h"
#include <string>

// Struct lưu thông tin node BFS (dùng thay std::pair)
struct BFSNode {
  int userID;
  int depth;
};

// Struct lưu thông tin gợi ý kết bạn
struct FriendSuggestion {
  int suggestedUserID;
  int mutualConnectionsCount;
  Vector<int> mutualConnectionsIDs;
};

struct GraphStats {
  int totalUsers = 0;
  int totalEdges = 0;
  int maxDegree = 0;
  Vector<int> maxDegreeUsers; // Tất cả người có bậc cao nhất
  int minDegree = 0;
  Vector<int> minDegreeUsers; // Tất cả người có bậc thấp nhất
  int isolatedCount = 0;
  double avgDegree = 0.0;
};

class SocialMedia {
private:
  HashMap<int, std::string> users;
  HashMap<int, HashSet<int>> adjList;

public:
  // === Quản lý người dùng & kết nối ===
  bool addUser(int userID, const std::string &name);
  bool addConnection(int userID_1, int userID_2);
  void removeUser(int userID);
  void removeConnection(int userID_1, int userID_2);

  // === Tải dữ liệu từ file ===
  bool loadUsersFromFile(const std::string &filepath);
  bool loadConnectionsFromFile(const std::string &filepath);

  // === Hiển thị ===
  void listUsers() const;
  void printUserInfo(int userID) const;

  // === Tìm kiếm ===
  Vector<int> searchUserByName(const std::string &keyword) const;

  // === Thuật toán lõi (BFS) ===
  const HashSet<int>* getDirectConnections(int userID) const;
  HashSet<int> getFriendsOfFriends(int userID) const;
  Vector<FriendSuggestion> suggestFriends(int userID,
                                          int maxSuggestions = 5) const;
  void printSuggestions(int userID, int maxSuggestions = 5) const;

  GraphStats computeGraphStats() const;
  // === Thống kê đồ thị ===
  void printGraphStats() const;

  // === Export kết quả ra file ===
  bool exportSuggestions(int userID, int maxSuggestions,
                         const std::string &filepath) const;
  bool exportGraphStats(const std::string &filepath) const;
  bool exportUserConnections(int userID, const std::string &filepath) const;

  // === Đo hiệu suất ===
  void measurePerformance(int testUserID) const;

  // === Helpers ===
  bool userExists(int userID) const;
  std::string getUserName(int userID) const;
  int getUserCount() const;
  int getEdgeCount() const;
};