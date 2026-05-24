#pragma once
#include "CustomHashMap.h"
#include "CustomVector.h"

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

  // Duyệt qua tất cả các phần tử trong HashSet
  template <typename Func> void forEach(Func fn) const {
    map.forEach([&fn](const T &key, const bool &) { fn(key); });
  }

  // Chuyển HashSet thành Vector
  Vector<T> toVector() const {
    Vector<T> result;
    forEach([&result](const T &val) { result.push_back(val); });
    return result;
  }
};
