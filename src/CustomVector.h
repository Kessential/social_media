#pragma once
#include <cstddef>

template <typename T> class Vector {
private:
  T *data;
  size_t cap;
  size_t len;

  void reserve(size_t newCap) {
    if (newCap <= cap)
      return;
    T *temp = new T[newCap];
    for (size_t i = 0; i < len; ++i) {
      temp[i] = data[i];
    }
    delete[] data;
    data = temp;
    cap = newCap;
  }

public:
  Vector() : data(nullptr), cap(0), len(0) {}

  ~Vector() { clear(); }

  Vector(const Vector &other)
      : cap(other.cap), len(other.len),
        data(other.cap > 0 ? new T[other.cap] : nullptr) {
    for (size_t i = 0; i < other.len; ++i) {
      data[i] = other.data[i];
    }
  }

  Vector &operator=(const Vector &other) {
    if (this != &other) {
      delete[] data;
      len = other.len;
      cap = other.cap;
      data = cap > 0 ? new T[other.cap] : nullptr;
      for (size_t i = 0; i < other.len; ++i)
        data[i] = other.data[i];
    }
    return *this;
  }

  void push_back(const T &value) {
    if (len == cap) {
      reserve(cap == 0 ? 1 : cap * 2);
    }
    data[len] = value;
    ++len;
  };

  void pop_back() {
    if (len > 0)
      --len;
  };

  T &operator[](size_t index) { return data[index]; };

  const T &operator[](size_t index) const { return data[index]; };

  size_t size() const { return len; }

  size_t capacity() const { return cap; }

  bool empty() const { return len == 0; }

  void clear() {
    delete[] data;
    data = nullptr;
    len = 0;
    cap = 0;
  }
};
