#pragma once
#include "CustomHashMap.h"

template <typename T> class HashSet {
private:
  HashMap<T, bool> map;

public:
  bool insert(const T &value) {
    if (map.contains(value))
      return false;
    map.put(value, true);
    return true;
  }
  bool contains(const T &value) const { return map.contains(value); }
  void remove(const T &value) { map.remove(value); }
  size_t size() const { return map.size(); }
  bool empty() const { return map.empty(); }
  void clear() { map.clear(); }
};
