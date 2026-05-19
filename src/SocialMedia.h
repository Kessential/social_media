#pragma once
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct FriendSuggestion {
  int suggestedUserID;
  int mutualConnectionsCount;
  std::vector<int> mutualConnectionsIDs;
};

class SocialMedia {
private:
  std::unordered_map<int, std::string> users;
  std::unordered_map<int, std::unordered_set<int>> adjList;

public:
  void addUser(int userID, const std::string &name);
  void addConnection(int userID_1, int userID_2);
  bool loadUsersFromFile(const std::string &filepath);
  bool loadConnectionsFromFile(const std::string &filepath);
  void listUsers();

  [[nodiscard]] std::unordered_set<int> getDirectConnections(int userID) const;
  [[nodiscard]] std::unordered_set<int> getFriendsOfFriends(int userID) const;
  [[nodiscard]] std::vector<FriendSuggestion>
  suggestFriends(int userID, int maxSuggestions = 5) const;

  void printSuggestions(int userID, int maxSuggestions = 5) const;
};
