#pragma once
#include <cstddef>
#include <stdexcept>
#include <utility>

template <typename T> class Vector {
private:
  T *data;
  size_t cap;
  size_t len;

  void grow(size_t newCap) {
    if (newCap <= cap)
      return;
    T *temp = new T[newCap];
    for (size_t i = 0; i < len; ++i) {
      temp[i] = std::move_if_noexcept(data[i]);
    }
    delete[] data;
    data = temp;
    cap = newCap;
  }

public:
  Vector() : data(nullptr), cap(0), len(0) {}

  ~Vector() {
    delete[] data;
    data = nullptr;
    len = 0;
    cap = 0;
  }

  // Copy constructor
  Vector(const Vector &other)
      : data(other.cap > 0 ? new T[other.cap] : nullptr), cap(other.cap),
        len(other.len) {
    for (size_t i = 0; i < other.len; ++i) {
      data[i] = other.data[i];
    }
  }

  // Copy assignment
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

  // Move constructor
  Vector(Vector &&other) noexcept
      : data(other.data), cap(other.cap), len(other.len) {
    other.data = nullptr;
    other.cap = 0;
    other.len = 0;
  }

  // Move assignment
  Vector &operator=(Vector &&other) noexcept {
    if (this != &other) {
      delete[] data;
      data = other.data;
      cap = other.cap;
      len = other.len;
      other.data = nullptr;
      other.cap = 0;
      other.len = 0;
    }
    return *this;
  }

  void push_back(const T &value) {
    if (len == cap) {
      grow(cap == 0 ? 1 : cap * 2);
    }
    data[len] = value;
    ++len;
  }

  void push_back(T &&value) {
    if (len == cap)
      grow(cap == 0 ? 1 : cap * 2);
    data[len] = std::move(value);
    ++len;
  }

  void pop_back() {
    if (len > 0)
      --len;
  }

  T &operator[](size_t index) { return data[index]; }

  const T &operator[](size_t index) const { return data[index]; }

  T &back() {
    if (empty())
      throw std::out_of_range("Vector rong!");
    return data[len - 1];
  }

  const T &back() const {
    if (empty())
      throw std::out_of_range("Vector rong!");
    return data[len - 1];
  }

  size_t size() const { return len; }

  size_t capacity() const { return cap; }

  bool empty() const { return len == 0; }

  // Thay đổi kích thước Vector, khởi tạo giá trị mặc định cho phần tử mới
  void resize(size_t newLen) {
    if (newLen >= len) {
      if (newLen > cap)
        grow(newLen);
      for (size_t i = len; i < newLen; ++i)
        data[i] = T();
    }
    len = newLen;
  }

  // Xóa tất cả phần tử nhưng giữ bộ nhớ đã cấp phát
  void clear() { len = 0; }

  // Giải phóng toàn bộ bộ nhớ
  void shrink() {
    delete[] data;
    data = nullptr;
    len = 0;
    cap = 0;
  }
};