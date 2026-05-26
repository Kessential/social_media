#pragma once
#include <cstddef>

template <typename T> class Queue {
private:
  struct Node {
    T data;
    Node *next;
    Node(const T &val) : data(val), next(nullptr) {}
  };

  Node *head;
  Node *tail;
  size_t count;

public:
  Queue() : head(nullptr), tail(nullptr), count(0) {}

  ~Queue() { clear(); }

  Queue(const Queue &other) = delete;
  Queue &operator=(const Queue &other) = delete;

  Queue(Queue &&other) noexcept
      : head(other.head), tail(other.tail), count(other.count) {
    other.head = nullptr;
    other.tail = nullptr;
    other.count = 0;
  }
  Queue &operator=(Queue &&other) noexcept {
    if (this != &other) {
      clear();
      head = other.head;
      tail = other.tail;
      count = other.count;
      other.head = nullptr;
      other.tail = nullptr;
      other.count = 0;
    }
    return *this;
  }

  void push(const T &value) {
    Node *newNode = new Node(value);
    if (empty()) {
      head = newNode;
      tail = newNode;
    } else {
      tail->next = newNode;
      tail = newNode;
    }
    ++count;
  }

  void pop() {
    if (empty())
      return;
    Node *temp = head;
    head = head->next;
    delete temp;
    if (head == nullptr) {
      tail = nullptr;
    }
    --count;
  }

  T &front() { return head->data; }

  const T &front() const { return head->data; }

  bool empty() const { return count == 0; }
  size_t size() const { return count; }

  void clear() {
    while (!empty()) {
      pop();
    }
  }
};
