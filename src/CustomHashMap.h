#pragma once
#include <cstddef>
#include <functional>
#include <stdexcept>

template <typename K, typename V> class HashMap {
private:
  struct HashNode {
    K key;
    V value;
    HashNode *next;
    HashNode(const K &k, const V &v) : key(k), value(v), next(nullptr) {}
  };

  HashNode **table;

  size_t bucketCount;
  size_t count;

  float maxLoadFactor;

  size_t getBucketIndex(const K &key) const {
    std::hash<K> hashFn;
    return hashFn(key) % bucketCount;
  }

  void rehash(size_t newBucketCount) {
    HashNode **newTable = new HashNode *[newBucketCount]();

    for (size_t i = 0; i < bucketCount; ++i) {
      HashNode *curr = table[i];
      while (curr != nullptr) {
        HashNode *next = curr->next;

        std::hash<K> hashFn;
        size_t newIdx = hashFn(curr->key) % newBucketCount;

        curr->next = newTable[newIdx];
        newTable[newIdx] = curr;

        curr = next;
      }
    }

    delete[] table;
    table = newTable;
    bucketCount = newBucketCount;
  }

public:
  HashMap(size_t initialBuckets = 16, float loadFactor = 0.75f)
      : bucketCount(initialBuckets), count(0), maxLoadFactor(loadFactor) {
    table = new HashNode *[bucketCount]();
  }

  ~HashMap() {
    clear();
    delete[] table;
  }

  HashMap(const HashMap &other) = delete;
  HashMap &operator=(const HashMap &other) = delete;

  void put(const K &key, const V &value) {
    if (static_cast<float>(count) / bucketCount >= maxLoadFactor) {
      rehash(bucketCount * 2);
    }
    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    while (curr != nullptr) {
      if (curr->key == key) {
        curr->value = value;
        return;
      }
      curr = curr->next;
    }
    HashNode *newNode = new HashNode(key, value);
    newNode->next = table[idx];
    table[idx] = newNode;
    ++count;
  }

  bool contains(const K &key) const {
    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    while (curr != nullptr) {
      if (curr->key == key) {
        return true;
      }
      curr = curr->next;
    }
    return false;
  }

  V &get(const K &key) {
    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    while (curr != nullptr) {
      if (curr->key == key) {
        return curr->value;
      }
      curr = curr->next;
    }
    throw std::out_of_range("Key khong ton tai trong HashMap!");
  }

  const V &get(const K &key) const {
    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    while (curr != nullptr) {
      if (curr->key == key) {
        return curr->value;
      }
      curr = curr->next;
    }
    throw std::out_of_range("Key khong ton tai trong HashMap!");
  }

  V &operator[](const K &key) {
    if (static_cast<float>(count) / bucketCount >= maxLoadFactor) {
      rehash(bucketCount * 2);
    }

    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    while (curr != nullptr) {
      if (curr->key == key) {
        return curr->value; // Nếu có sẵn, trả về luôn
      }
      curr = curr->next;
    }

    // Nếu chưa có, tự động tạo node mới với giá trị mặc định V()
    HashNode *newNode = new HashNode(key, V());
    newNode->next = table[idx];
    table[idx] = newNode;
    ++count;
    return table[idx]->value;
  }

  // Xóa cặp key-value khỏi HashMap
  void remove(const K &key) {
    size_t idx = getBucketIndex(key);
    HashNode *curr = table[idx];
    HashNode *prev = nullptr;

    while (curr != nullptr) {
      if (curr->key == key) {
        if (prev == nullptr) {
          table[idx] = curr->next; // Node cần xóa ở đầu danh sách kề
        } else {
          prev->next = curr->next; // Node cần xóa ở giữa hoặc cuối
        }
        delete curr;
        --count;
        return;
      }
      prev = curr;
      curr = curr->next;
    }
  }

  size_t size() const { return count; }
  bool empty() const { return count == 0; }

  // Giải phóng toàn bộ các node trong HashMap nhưng giữ lại mảng table
  void clear() {
    for (size_t i = 0; i < bucketCount; ++i) {
      HashNode *curr = table[i];
      while (curr != nullptr) {
        HashNode *temp = curr;
        curr = curr->next;
        delete temp;
      }
      table[i] = nullptr;
    }
    count = 0;
  }
};
