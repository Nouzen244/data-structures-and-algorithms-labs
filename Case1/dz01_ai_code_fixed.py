#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исправленная версия quicksort (ДЗ 1, КИМ-01).

Исправлены дефекты исходного файла dz01-ai-code.py:
1. Трёхпутевое разбиение (< pivot, == pivot, > pivot) сохраняет все дубликаты
   и даёт O(n) на массивах из равных элементов.
2. Выбор опорного элемента «медиана из трёх» (первый, средний, последний)
   устраняет деградацию в O(n^2) и RecursionError на упорядоченных и обратно
   упорядоченных массивах.
3. Заявлена фактическая пространственная сложность O(n) (создание новых списков).
"""
from __future__ import annotations


def _median_of_three(a: list[int]) -> int:
    first = a[0]
    mid = a[len(a) // 2]
    last = a[-1]
    if (first <= mid <= last) or (last <= mid <= first):
        return mid
    if (mid <= first <= last) or (last <= first <= mid):
        return first
    return last


def quicksort(data: list[int]) -> list[int]:
    """Сортирует список целых чисел, не изменяя исходный список.

    Средняя сложность по времени: O(n log n); на массивах из равных элементов: O(n).
    Дополнительная память: O(n) за счёт формирования новых списков при разбиении.
    """
    if len(data) <= 1:
        return list(data)
    pivot = _median_of_three(data)
    smaller = [x for x in data if x < pivot]
    equal = [x for x in data if x == pivot]
    larger = [x for x in data if x > pivot]
    return quicksort(smaller) + equal + quicksort(larger)


if __name__ == "__main__":
    example = [5, 2, 9, 1, 7, 2, 5]
    print("Input :", example)
    print("Sorted:", quicksort(example))
