#include "SocialMedia.h"
#include <iostream>

int main() {
  SocialMedia test;
  // test.buildGraph();
  bool success = test.loadUsersFromFile("users.csv");
  bool successConnections = test.loadConnectionsFromFile("edges.txt");
  if (!success || !successConnections) {
    std::cerr << "Failed to load data from files\n";
    return 1;
  }
  for (int i = 1; i <= 15; ++i) {
    test.printSuggestions(i);
  }
}
