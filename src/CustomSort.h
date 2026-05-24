#pragma once
#include "CustomVector.h"

namespace Sort {
template <typename T> void swap(T &a, T &b) {
  T temp = a;
  a = b;
  b = temp;
}

template <typename T, typename Compare>
void insertionSort(Vector<T> &arr, int low, int high, Compare comp) {
  for (int i = low + 1; i <= high; ++i) {
    T key = arr[i];
    int j = i - 1;
    while (j >= low && comp(key, arr[j])) {
      arr[j + 1] = arr[j];
      --j;
    }
    arr[j + 1] = key;
  }
}

template <typename T, typename Compare>
int medianOfThree(Vector<T> &arr, int a, int b, int c, Compare comp) {
  if (comp(arr[a], arr[b])) {
    if (comp(arr[b], arr[c]))
      return b;
    if (comp(arr[a], arr[c]))
      return c;
    return a;
  } else {
    if (comp(arr[a], arr[c]))
      return a;
    if (comp(arr[b], arr[c]))
      return c;
    return b;
  }
}

template <typename T, typename Compare>
int HoarePartition(Vector<T> &arr, int low, int high, Compare comp) {
  int mid = low + (high - low) / 2;
  int pivotIdx = medianOfThree(arr, low, mid, high, comp);

  T pivot = arr[pivotIdx];

  int i = low - 1, j = high + 1;

  while (true) {
    do {
      ++i;
    } while (comp(arr[i], pivot));

    do {
      --j;
    } while (comp(pivot, arr[j]));

    if (i >= j)
      return j;

    swap(arr[i], arr[j]);
  }
}

template <typename T, typename Compare>
void HoareQuicksort(Vector<T> &arr, int low, int high, Compare comp) {
  const int CUTOFF = 10;
  while (low < high) {
    if (high - low < CUTOFF) {
      insertionSort(arr, low, high, comp);
      return;
    }

    int p = HoarePartition(arr, low, high, comp);

    if (p - low < high - p) {
      HoareQuicksort(arr, low, p, comp);

      low = p + 1;
    } else {
      HoareQuicksort(arr, p + 1, high, comp);
      high = p;
    }
  }
}
template <typename T> void HoareQuicksort(Vector<T> &arr, int low, int high) {
  HoareQuicksort(arr, low, high, [](const T &a, const T &b) { return a < b; });
}

// Overload thuận tiện: sort toàn bộ Vector với comparator tùy chỉnh
template <typename T, typename Compare>
void sort(Vector<T> &arr, Compare comp) {
  if (arr.size() <= 1)
    return;
  HoareQuicksort(arr, 0, static_cast<int>(arr.size()) - 1, comp);
}

// Overload thuận tiện: sort toàn bộ Vector tăng dần
template <typename T> void sort(Vector<T> &arr) {
  if (arr.size() <= 1)
    return;
  HoareQuicksort(arr, 0, static_cast<int>(arr.size()) - 1);
}
} // namespace Sort
