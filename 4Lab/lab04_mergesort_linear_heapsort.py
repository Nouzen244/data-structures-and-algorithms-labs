#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
import time
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.

    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Ожидаемая сложность: Θ(len(left) + len(right)) — каждый элемент
    переносится в результат ровно один раз (обоснование в отчёте, п. 2.1).
    """
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Именно <= (а не <) даёт стабильность: при равных ключах первым
        # уходит элемент левой половины, то есть стоявший во входе раньше.
        if key(left[i]) <= key(right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])   # одна из половин исчерпана, хвост другой
    out.extend(right[j:])  # уже упорядочен и целиком больше выписанного
    return out


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. Ожидаемая сложность:
    Θ(n log n) на любом входе, дополнительная память Θ(n), стабильна."""
    if len(a) <= 1:
        return list(a)  # копия: вход не меняется и результат — новый список
    mid = len(a) // 2   # глубина рекурсии ⌈log2 n⌉ — лимит Python не грозит
    return merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].

    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: Θ(n + k), где k = key_max + 1, — массив
    счётчиков длины k плюс выходной массив длины n; ограничение диапазона
    ключей — отчёт, п. 2.2.
    """
    count = [0] * (key_max + 1)
    for x in a:
        if not 0 <= x <= key_max:  # иначе отрицательный индекс тихо испортил бы результат
            raise ValueError(f"ключ {x} вне диапазона [0, {key_max}]")
        count[x] += 1
    for v in range(1, key_max + 1):  # count[v] — число ключей <= v,
        count[v] += count[v - 1]     # то есть позиция за последним ключом v
    out = [0] * len(a)
    for x in reversed(a):  # с конца: последний из равных встаёт на последнее место
        count[x] -= 1
        out[count[x]] = x
    return out


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.

    Поверх устойчивой поразрядной counting-сортировки: от младшего разряда
    к старшему. Ожидаемая сложность: Θ(d·(n + 10)), d — число десятичных
    разрядов максимума; дополнительная память Θ(n + 10).
    """
    if any(x < 0 for x in a):
        raise ValueError("radix_sort_lsd: поддерживаются только неотрицательные ключи")
    out = list(a)
    biggest = max(out, default=0)
    exp = 1
    while biggest // exp > 0:  # d проходов; для пустого входа и [0] — ни одного
        out = counting_by_digit(out, exp)
        exp *= 10
    # Почему проход обязан быть устойчивым — отчёт, п. 2.3; демонстрация —
    # check_radix_needs_stability().
    return out


def counting_by_digit(a: list[int], exp: int) -> list[int]:
    """Один проход radix: устойчивая counting-сортировка по цифре (x // exp) % 10."""
    count = [0] * 10
    for x in a:
        count[(x // exp) % 10] += 1
    for d in range(1, 10):
        count[d] += count[d - 1]
    out = [0] * len(a)
    for x in reversed(a):  # с конца — устойчивость: порядок равных цифр сохраняется
        d = (x // exp) % 10
        count[d] -= 1
        out[count[d]] = x
    return out


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest = i
        left, right = 2 * i + 1, 2 * i + 2  # потомки в неявном двоичном дереве
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:  # оба потомка не больше — свойство кучи восстановлено
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.

    Схема: построение max-кучи просейками вниз (снизу вверх, O(n)),
    затем обмен вершины с последним элементом и просейка. Сложность:
    Θ(n log n) в худшем случае (построение O(n) + n − 1 просеек по O(log n)),
    дополнительная память O(1); нестабильна.
    """
    build_max_heap(a)
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]  # максимум уходит в конец, хвост a[end:] готов
        sift_down(a, 0, end)         # куча сократилась до a[0:end]


def build_max_heap(a: list[int]) -> None:
    """Построение max-кучи на месте: просейки вниз от последнего внутреннего узла к корню, O(n)."""
    for i in range(len(a) // 2 - 1, -1, -1):  # листья (i >= n // 2) — уже кучи
        sift_down(a, i, len(a))


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с рандомизацией опорного элемента — перенести из своей ЛР 3.

    Перенесён из ЛР 3 без изменений алгоритма: трёхстороннее разбиение,
    цикл со стеком границ. Опорный — random.randrange: модуль random засеивается
    в main() seed-ом варианта, поэтому запуск воспроизводим. В среднем Θ(n log n),
    в худшем Θ(n²), память O(log n) на стек границ; нестабилен.
    """
    a = list(a)
    stack = [(0, len(a))]  # полуинтервалы [lo, hi)
    while stack:
        lo, hi = stack.pop()
        if hi - lo < 2:  # подмассивы длины 0 и 1 уже отсортированы
            continue
        pivot = a[random.randrange(lo, hi)]
        lt, i, gt = lo, lo, hi  # a[lo:lt] < pivot, a[lt:i] == pivot, a[gt:hi] > pivot
        while i < gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                gt -= 1
                a[i], a[gt] = a[gt], a[i]
            else:
                i += 1
        # Сначала кладём большую часть: глубина стека не превышает log2(n).
        parts = [(lo, lt), (gt, hi)]
        parts.sort(key=lambda p: p[1] - p[0], reverse=True)
        stack.extend(parts)
    return a


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")


def is_max_heap(a: list[int]) -> bool:
    """Свойство max-кучи: каждый узел не меньше своих потомков."""
    return all(a[i] >= a[c] for i in range(len(a))
               for c in (2 * i + 1, 2 * i + 2) if c < len(a))


def check_heap() -> None:
    """Свойство кучи после построения, сортировка именно на месте, малые случаи."""
    rng = random.Random(1)
    for _ in range(200):
        a = [rng.randint(0, 50) for _ in range(rng.randint(0, 60))]
        heap = list(a)
        build_max_heap(heap)
        expect(is_max_heap(heap), f"после build_max_heap нарушено свойство кучи: {heap}")
        expect(sorted(heap) == sorted(a), f"build_max_heap потерял элементы: {heap}")
    buf = [3, 1, 2]
    same = buf
    expect(heap_sort(buf) is None and same is buf and buf == [1, 2, 3],
           "heap_sort должен сортировать переданный список на месте и возвращать None")


class KeyOnly:
    """Пара (ключ, номер), сравнение — только по ключу: видно, сохранён ли порядок равных."""

    __slots__ = ("key", "tag")

    def __init__(self, key: int, tag: int) -> None:
        self.key, self.tag = key, tag

    def __lt__(self, other: "KeyOnly") -> bool:
        return self.key < other.key

    def __gt__(self, other: "KeyOnly") -> bool:
        return self.key > other.key

    def __le__(self, other: "KeyOnly") -> bool:
        return self.key <= other.key

    def __ge__(self, other: "KeyOnly") -> bool:
        return self.key >= other.key


def keeps_order(res: list, src: list) -> bool:
    """Номера при каждом ключе идут в том же порядке, что и во входе."""
    tags = {}
    for p in res:
        tags.setdefault(p.key, []).append(p.tag)
    return all(t == sorted(t) for t in tags.values()) and len(res) == len(src)


def check_radix_pass_stability() -> None:
    """Проход counting_by_digit устойчив: равные цифры сохраняют исходный порядок."""
    rng = random.Random(2)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        for exp in (1, 10, 100):
            got = counting_by_digit(a, exp)
            expect(got == sorted(a, key=lambda x, e=exp: (x // e) % 10),
                   f"проход по разряду {exp} неустойчив на {a}: {got}")


def unstable_pass(a: list[int], exp: int) -> list[int]:
    """Тот же проход, но расстановка с НАЧАЛА — порядок равных цифр переворачивается."""
    count = [0] * 10
    for x in a:
        count[(x // exp) % 10] += 1
    for d in range(1, 10):
        count[d] += count[d - 1]
    out = [0] * len(a)
    for x in a:
        d = (x // exp) % 10
        count[d] -= 1
        out[count[d]] = x
    return out


def check_radix_needs_stability() -> None:
    """С неустойчивым проходом radix ошибается: [21, 12, 11] -> [12, 11, 21]."""
    out = [21, 12, 11]
    for exp in (1, 10):
        out = unstable_pass(out, exp)
    expect(out != sorted(out), "контрпример должен ломаться без устойчивости прохода")
    expect(out == [12, 11, 21], f"неожиданный результат контрпримера: {out}")


def check_counting_range() -> None:
    """Ключ вне [0, key_max] — явная ошибка, а не тихо испорченный результат."""
    for bad in ([-1, 2], [5, 1000]):
        try:
            counting_sort(bad, key_max=999)
        except ValueError:
            continue
        raise SelfCheckError(f"counting_sort принял ключи вне диапазона: {bad}")
    try:
        radix_sort_lsd([3, -1])
    except ValueError:
        return
    raise SelfCheckError("radix_sort_lsd принял отрицательный ключ")


def check_stability_claims() -> None:
    """Стабильность там, где заявлена; и что нестабильные действительно нарушают порядок."""
    rng = random.Random(3)
    broken = {"merge_sort": 0, "heap_sort": 0, "quick_sort": 0}
    for _ in range(300):
        src = [KeyOnly(rng.randint(0, 4), i) for i in range(30)]
        broken["merge_sort"] += not keeps_order(merge_sort(src), src)
        buf = list(src)
        heap_sort(buf)
        broken["heap_sort"] += not keeps_order(buf, src)
        broken["quick_sort"] += not keeps_order(quick_sort(src), src)
    expect(broken["merge_sort"] == 0, f"merge_sort нарушил порядок {broken['merge_sort']} раз")
    expect(broken["heap_sort"] > 0, "heap_sort неожиданно сохранил порядок на всех входах")
    expect(broken["quick_sort"] > 0, "quick_sort неожиданно сохранил порядок на всех входах")


def check_input_untouched() -> None:
    """merge, counting, radix и quick возвращают новый список и не меняют вход."""
    src = [5, 3, 5, 0, 999, 2]
    for name in ("merge_sort", "counting_sort", "radix_sort_lsd", "quick_sort"):
        a = list(src)
        res = SORTS[name](a)
        expect(a == src and res is not a, f"{name}: изменил входной список или вернул его же")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    checks.append(("свойство кучи и сортировка на месте", check_heap))
    checks.append(("устойчивость прохода radix", check_radix_pass_stability))
    checks.append(("radix без устойчивости неверен", check_radix_needs_stability))
    checks.append(("диапазон ключей counting/radix", check_counting_range))
    checks.append(("стабильность: merge да, heap и quick нет", check_stability_claims))
    checks.append(("вход не изменяется", check_input_untouched))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def log_log_slope(points: list[tuple[int, float]]) -> float:
    """Наклон МНК-прямой log t от log n — оценка показателя степени k в t ~ n^k."""
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))


COUNTING_N = 10_000
COUNTING_KEY_MAX = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7]


def counting_range_experiment(seed: int) -> list[tuple[int, float, float]]:
    """CountingSort при фиксированном n и растущем k: время counting и sorted()."""
    rng = random.Random(seed)
    print(f"\nCountingSort: n = {COUNTING_N}, растёт диапазон ключей k = key_max + 1")
    rows = []
    for key_max in COUNTING_KEY_MAX:
        data = [rng.randint(0, key_max) for _ in range(COUNTING_N)]
        t_count = bench(lambda a, km=key_max: counting_sort(a, key_max=km), data)
        t_sorted = bench(sorted, data)
        rows.append((key_max, t_count, t_sorted))
        print(f"  key_max = {key_max:>9}: counting t = {t_count:.6f} c, "
              f"sorted() t = {t_sorted:.6f} c, счётчиков {key_max + 1}")
    return rows


PROPERTIES = [
    # (алгоритм, лучший, средний, худший, доп. память, стабильна, ограничения)
    ("merge_sort", "n log n", "n log n", "n log n", "n", "да",
     "нет; нужна память под копии"),
    ("counting_sort", "n + k", "n + k", "n + k", "n + k", "да",
     "целые ключи из [0, key_max]; при k >> n теряет смысл"),
    ("radix_sort_lsd", "d(n + 10)", "d(n + 10)", "d(n + 10)", "n + 10", "да",
     "неотрицательные целые; d — число разрядов"),
    ("heap_sort", "n log n", "n log n", "n log n", "1", "нет",
     "нет; на месте"),
    ("quick_sort (ЛР 3)", "n log n", "n log n", "n²", "log n", "нет",
     "худший случай маловероятен из-за рандомизации"),
    ("sorted() (эталон)", "n", "n log n", "n log n", "n", "да",
     "Timsort; любые сравнимые ключи"),
]


def print_properties() -> None:
    print("\nСводная таблица свойств (время и память — порядок роста, Θ):")
    for row in PROPERTIES:
        print("  " + " | ".join(row))


def plot_results(results: dict, k_rows: list, out_dir: Path) -> None:
    """log-log графики по распределениям и график counting от диапазона ключей."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # сохранение в файл без графической оболочки
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib не установлен — графики пропущены "
              "(pip install -r requirements.txt)")
        return
    dists = list(results)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5), sharey=True)
    for ax, dist in zip(axes.flat, dists):
        for algo, pts in results[dist].items():
            ax.plot([n for n, _ in pts], [t for _, t in pts], marker="o",
                    label=f"{algo} ({log_log_slope(pts):.2f})")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(dist)
        ax.set_xlabel("размер входа n")
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend(fontsize=7, title="алгоритм (наклон)", title_fontsize=7)
    for ax in axes[:, 0]:
        ax.set_ylabel("время, с")
    ax = axes.flat[len(dists)]
    ks = [km + 1 for km, _, _ in k_rows]
    ax.plot(ks, [t for _, t, _ in k_rows], marker="o", label="counting_sort")
    ax.plot(ks, [t for _, _, t in k_rows], marker="s", label="sorted()")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(f"counting_sort: n = {COUNTING_N}, растёт k")
    ax.set_xlabel("диапазон ключей k = key_max + 1")
    ax.grid(True, which="both", linewidth=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = out_dir / "lab04_loglog.png"
    fig.savefig(path, dpi=150)
    print(f"\nГрафик сохранён:\n  {path}")


def run_benchmarks(seed: int, out_dir: Path | None = None) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    results: dict[str, dict[str, list[tuple[int, float]]]] = {}
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                t = bench(fn, data)
                results.setdefault(dist_name, {}).setdefault(algo_name, []).append((n, t))
                print(f"    {algo_name:>18}: t = {t:.6f} c")

    print("\nНаклоны log-log (1 — линейное время, ~1.1 — n log n):")
    for dist_name, by_algo in results.items():
        print(f"  {dist_name}:")
        for algo_name, pts in by_algo.items():
            print(f"    {algo_name:>18}: {log_log_slope(pts):.2f}")
    k_rows = counting_range_experiment(seed)
    print_properties()
    plot_results(results, k_rows, out_dir or Path.cwd())
    # Расхождения замеров с асимптотикой (константы Python против C у sorted(),
    # d = 10 разрядов у radix на широком диапазоне) — отчёт, п. 4.


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path.cwd(),
                    help="каталог для графиков (по умолчанию текущий)")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed, args.out)


if __name__ == "__main__":
    main()
