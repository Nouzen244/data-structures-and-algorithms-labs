#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Линейный, бинарный и интерполяционный поиск.

Каркас взят из стартовой заготовки КИМ-06 без изменений; заполнены только TODO
в соответствии с КИМ-06 и методикой верификации (docs/ai-verification.md).

Каждая функция поиска работает с отсортированным по неубыванию массивом
и возвращает пару (индекс найденного элемента или -1, число сравнений ключей).

Запуск: python lab06_search.py --variant 17
"""
from __future__ import annotations

import argparse
import bisect
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска (реализуются вручную, без in/index/bisect в основной части)
# ---------------------------------------------------------------------------


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    """Линейный поиск первого вхождения key.

    Возвращает (индекс первого вхождения или -1, число сравнений ключей).
    Ожидаемая сложность: O(n) в среднем и худшем случае, O(1) в лучшем.
    """
    comps = 0
    for i, val in enumerate(a):
        comps += 1
        if val == key:
            return i, comps
    return -1, comps


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Бинарный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Инвариант границ: если key присутствует в a, то он лежит в отрезке a[lo..hi].
    Ожидаемая сложность: O(log n) в среднем и худшем случае, O(1) в лучшем.
    """
    lo = 0
    hi = len(a) - 1
    comps = 0
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        comps += 1
        val = a[mid]
        if val == key:
            return mid, comps
        if val < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comps


def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    """Интерполяционный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Позиция зонда: mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo]).
    Обязательно защититься от деления на ноль при a[hi] == a[lo] и от выхода
    key за пределы [a[lo], a[hi]].
    Средняя сложность на равномерных данных: O(log log n); худший случай: O(n).
    """
    if not a:
        return -1, 0
    lo = 0
    hi = len(a) - 1
    comps = 0
    while lo <= hi:
        if key < a[lo] or key > a[hi]:
            comps += 1
            return -1, comps
        if a[hi] == a[lo]:
            comps += 1
            return (lo, comps) if a[lo] == key else (-1, comps)
        mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        comps += 1
        val = a[mid]
        if val == key:
            return mid, comps
        if val < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comps


# ---------------------------------------------------------------------------
# 2. Данные по варианту: два распределения, присутствующие/отсутствующие ключи
# ---------------------------------------------------------------------------


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    """Отсортированный массив n ключей: 'uniform' — равномерное распределение,
    'exponential' — неравномерное (экспоненциальное, значения сгущаются у нуля)."""
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    """count ключей для серии поисков: присутствующие берутся из массива,
    отсутствующие подбираются вне множества его значений."""
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]


def self_check() -> None:
    """Граничные случаи + сверка с эталоном (оператор in, list.index, bisect)."""
    for name, fn in ALGORITHMS:
        # Пустой массив: элемент не найден, сравнений нет.
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"
        # Один элемент: найден / не найден.
        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"
        # Все элементы равны (проверка защиты от деления на ноль).
        assert fn([5, 5, 5, 5], 5)[0] != -1, f"{name}: равные элементы, ключ есть"
        assert fn([5, 5, 5, 5], 4)[0] == -1, f"{name}: равные элементы, ключа нет"
        # Первый, последний и отсутствующие ключи (внутри и вне диапазона).
        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона"

    # Сверка с эталоном стандартной библиотеки на случайных массивах.
    rng = random.Random(0)
    for _ in range(300):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)
        # Эталон присутствия ключа — bisect_left (и, эквивалентно, оператор in).
        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                # При дубликатах бинарный/интерполяционный могут вернуть
                # любое вхождение — проверяем значение по индексу.
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"
        # Линейный поиск обязан возвращать первое вхождение — эталон list.index.
        if present:
            assert linear_search(a, key)[0] == a.index(key)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Бенчмарк: сравнения и время от n (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5      # число повторов серии замеров (берётся медиана)
N_KEYS = 200     # число ключей в одной серии поисков


def bench(fn, a: list[int], keys: list[int]) -> float:
    """Медиана времени одной серии поисков по REPEATS запускам, с прогревом."""
    for k in keys:  # прогрев — не учитывается
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    """Среднее число сравнений ключей на один поиск."""
    return statistics.mean(fn(a, k)[1] for k in keys)


def save_plots(results: dict, out_dir: Path) -> None:
    """Строит графики «среднее число сравнений от n» и «время от n» для каждого распределения."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    titles = {
        "uniform": "Равномерное распределение (uniform)",
        "exponential": "Экспоненциальное распределение (exponential)",
    }
    styles = {
        ("linear", True): ("o-", "linear (есть)"),
        ("linear", False): ("o--", "linear (нет)"),
        ("binary", True): ("s-", "binary (есть)"),
        ("binary", False): ("s--", "binary (нет)"),
        ("interpolation", True): ("^-", "interpolation (есть)"),
        ("interpolation", False): ("^--", "interpolation (нет)"),
    }

    for dist in ("uniform", "exponential"):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
        for (name, present), (fmt, label) in styles.items():
            pts = results[dist][(name, present)]
            if not pts:
                continue
            ns = [p[0] for p in pts]
            cmps = [p[1] for p in pts]
            ts = [p[2] for p in pts]
            ax1.loglog(ns, cmps, fmt, label=label)
            ax2.loglog(ns, ts, fmt, label=label)

        ax1.set_title(f"{titles[dist]}: сравнения от n")
        ax1.set_xlabel("Размер массива n")
        ax1.set_ylabel("Среднее число сравнений")
        ax1.grid(True, which="both", ls="--", alpha=0.4)
        ax1.legend(fontsize=8)

        ax2.set_title(f"{titles[dist]}: время {N_KEYS} поисков от n")
        ax2.set_xlabel("Размер массива n")
        ax2.set_ylabel("Медианное время, с")
        ax2.grid(True, which="both", ls="--", alpha=0.4)
        ax2.legend(fontsize=8)

        fig.tight_layout()
        fig.savefig(out_dir / f"lab06_{dist}.png", dpi=150)
        plt.close(fig)


def run_benchmarks(seed: int, out_dir: Path | None = None) -> None:
    rng = random.Random(seed)
    results: dict = {
        d: {(name, p): [] for name, _ in ALGORITHMS for p in (True, False)}
        for d in ("uniform", "exponential")
    }
    for distribution in ("uniform", "exponential"):
        print(f"\nРаспределение: {distribution}")
        for n in SIZES:
            a = make_dataset(n, distribution, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                label = "есть" if present else "нет"
                for name, fn in ALGORITHMS:
                    if name == "linear" and n > 30_000:
                        continue  # линейный поиск: большие n занимают минуты
                    mc = mean_comparisons(fn, a, keys)
                    t = bench(fn, a, keys)
                    results[distribution][(name, present)].append((n, mc, t))
                    print(f"  n={n:>7}  ключ {label:<4}  {name:<13}"
                          f"  сравнений={mc:>10.1f}"
                          f"  t={t:.6f} c")
    if out_dir is not None:
        save_plots(results, out_dir)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path("report"), help="каталог для графиков")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed, args.out)


if __name__ == "__main__":
    main()
