#include "SocialMedia.h"
#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <sstream>
#include <utility>

void SocialMedia::addUser(int userID, const std::string &name) {
  users.insert({userID, name});
}

void SocialMedia::addConnection(int userID_1, int userID_2) {
  if (userID_1 == userID_2) {
    std::cerr << "[CANH BAO] Tu ket noi toi chinh minh: " << userID_1 << "\n";
    return;
  }
  if (users.find(userID_1) == users.end() ||
      users.find(userID_2) == users.end()) {
    std::cerr << "[CANH BAO] Ket noi toi nguoi dung khong ton tai: " << userID_1
              << "<->" << userID_2 << "\n";
    return;
  }
  adjList[userID_1].insert(userID_2);
  adjList[userID_2].insert(userID_1);
}

bool SocialMedia::loadUsersFromFile(const std::string &filepath) {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    std::cerr << "[LOI] Khong the mo duoc file: " << filepath << "\n";
    return false;
  }
  std::string line;
  while (std::getline(file, line)) {
    std::stringstream ss(line);
    std::string strUserID, name;
    if (std::getline(ss, strUserID, ',') && std::getline(ss, name)) {
      addUser(std::stoi(strUserID), name);
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
    std::stringstream ss(line);
    int userID_1, userID_2;
    if (ss >> userID_1 >> userID_2) {
      addConnection(userID_1, userID_2);
    }
  }
  return true;
}

void SocialMedia::listUsers() {
  for (const auto &[userID, username] : users) {
    std::cout << "User ID: " << std::setw(15) << userID
              << ", Username: " << std::setw(32) << username << "\n";
  }
}

std::unordered_set<int> SocialMedia::getDirectConnections(int userID) const {
  auto it = adjList.find(userID);
  if (it == adjList.end())
    return {};
  return it->second;
}

std::unordered_set<int> SocialMedia::getFriendsOfFriends(int userID) const {
  std::unordered_set<int> friendsOfFriends;
  if (adjList.find(userID) == adjList.end())
    return friendsOfFriends;

  std::unordered_set<int> visited;
  std::queue<std::pair<int, int>> q;

  visited.insert(userID);
  q.push({userID, 0});

  while (!q.empty()) {
    const auto [currUser, depth] = q.front();
    q.pop();

    if (depth == 2) {
      friendsOfFriends.insert(currUser);
      continue;
    }

    if (depth < 2) {
      auto adjListIt = adjList.find(currUser);
      if (adjListIt == adjList.end())
        continue;
      for (int neighbor : adjListIt->second) {
        if (visited.find(neighbor) == visited.end()) {
          visited.insert(neighbor);
          q.push({neighbor, depth + 1});
        }
      }
    }
  }
  return friendsOfFriends;
}

std::vector<FriendSuggestion>
SocialMedia::suggestFriends(int userID, int maxSuggestions) const {
  auto it = adjList.find(userID);
  if (it == adjList.end())
    return {};
  const auto &directConnections = it->second;

  std::vector<FriendSuggestion> results;
  std::unordered_map<int, std::vector<int>> mutualConnectionsMap;

  for (int friendID : directConnections) {
    for (int fofID : adjList.at(friendID)) {
      if (fofID != userID &&
          directConnections.find(fofID) == directConnections.end()) {
        mutualConnectionsMap[fofID].push_back(friendID);
      }
    }
  }

  for (const auto &[candidateID, mutuals] : mutualConnectionsMap) {
    results.push_back({candidateID, static_cast<int>(mutuals.size()), mutuals});
  }

  std::sort(results.begin(), results.end(),
            [](const FriendSuggestion &a, const FriendSuggestion &b) {
              return a.mutualConnectionsCount > b.mutualConnectionsCount;
            });

  if (results.size() > static_cast<size_t>(maxSuggestions)) {
    results.resize(maxSuggestions);
  }

  return results;
}

void SocialMedia::printSuggestions(int userID, int maxSuggestions) const {
  auto suggestions = suggestFriends(userID, maxSuggestions);

  if (suggestions.empty()) {
    std::cout << "No friend suggestions for this user!\n";
    return;
  }

  for (const auto &suggest : suggestions) {
    std::cout << "Suggested User ID: " << suggest.suggestedUserID
              << " | Mutual Connections: " << suggest.mutualConnectionsCount
              << " | Mutual Connection IDs: ";
    for (size_t i = 0; i < suggest.mutualConnectionsIDs.size(); ++i) {
      std::cout << suggest.mutualConnectionsIDs[i];
      if (i != suggest.mutualConnectionsIDs.size() - 1) {
        std::cout << ", ";
      }
    }
    std::cout << "\n";
  }
}