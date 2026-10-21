#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
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
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: Θ(n²) в худшем и среднем случае, Θ(n) в лучшем
    (упорядоченный вход: один проход без обменов) — обоснование в отчёте, п. 1.1.

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    a = list(a)
    comparisons = swaps = 0
    for end in range(len(a) - 1, 0, -1):  # a[end+1:] уже на своих местах
        swapped = False
        for j in range(end):
            comparisons += 1
            if a[j] > a[j + 1]:  # строгое сравнение: равные не меняются местами
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Ожидаемая сложность: Θ(n) в лучшем случае (упорядоченный вход),
    Θ(n²) в среднем и худшем (обратный порядок).

    Перемещение — сдвиг одного элемента на позицию вправо; запись вставляемого
    элемента на своё место перемещением не считается (обоснование в отчёте, п. 1.2).
    """
    a = list(a)
    comparisons = moves = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > key:  # строгое сравнение: равные не обгоняются
                a[j + 1] = a[j]
                moves += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return a, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: Θ(n²) на любом входе — число сравнений
    n(n−1)/2 не зависит от данных, обменов не больше n − 1."""
    a = list(a)
    comparisons = swaps = 0
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[m]:
                m = j
        if m != i:  # обмен только если минимум не на своём месте
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return a, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем Θ(n log n), в худшем случае Θ(n²)
    (обосновать в отчёте, объяснить роль рандомизации). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    # Цикл со стеком границ вместо рекурсии: нет ограничения глубины Python.
    # Трёхстороннее разбиение (<, ==, >) по опорному: массив из равных
    # элементов обрабатывается за один проход, а не за Θ(n²).
    a = list(a)
    stack = [(0, len(a))]  # полуинтервалы [lo, hi)
    while stack:
        lo, hi = stack.pop()
        if hi - lo < 2:  # подмассивы длины 0 и 1 уже отсортированы
            continue
        pivot = a[rng.randrange(lo, hi)]
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
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    class KeyPair:
        """Пара (ключ, метка), все сравнения — только по ключу."""

        __slots__ = ("key", "label")

        def __init__(self, key: int, label: str) -> None:
            self.key, self.label = key, label

        def __lt__(self, other: "KeyPair") -> bool:
            return self.key < other.key

        def __gt__(self, other: "KeyPair") -> bool:
            return self.key > other.key

    def labels(a: list) -> str:
        return " ".join(f"({p.key},{p.label})" for p in a)

    def keep_order(res: list, src: list) -> bool:
        """Метки при каждом ключе идут в том же порядке, что и во входе."""
        for key in {p.key for p in src}:
            if [p.label for p in res if p.key == key] != \
                    [p.label for p in src if p.key == key]:
                return False
        return True

    sorts = {
        "bubble_sort": lambda a: bubble_sort(a)[0],
        "insertion_sort": lambda a: insertion_sort(a)[0],
        "selection_sort": lambda a: selection_sort(a)[0],
        "quick_sort": lambda a: quick_sort(a, random.Random(1)),
    }
    pairs = [KeyPair(k, c) for k, c in [(2, "a"), (1, "b"), (2, "c"), (1, "d")]]
    print("\nСтабильность (пары (ключ, метка), сравнение только по ключу):")
    print(f"  вход: {labels(pairs)}")
    for name, fn in sorts.items():
        res = fn(pairs)
        verdict = "порядок меток сохранён" if keep_order(res, pairs) else "порядок меток нарушен"
        print(f"  {name:<15} {labels(res)}  — {verdict}")

    # Один пример мог бы сохранить порядок случайно, поэтому — серия входов:
    # сортировка стабильна, если порядок сохранён на всех 1000 массивах.
    rng = random.Random(0)
    print("  серия из 1000 случайных массивов (длина 12, ключи 0..3), нарушений порядка:")
    for name, fn in sorts.items():
        broken = 0
        for _ in range(1000):
            src = [KeyPair(rng.randint(0, 3), chr(97 + i)) for i in range(12)]
            broken += not keep_order(fn(src), src)
        print(f"    {name:<15} {broken:>4} из 1000 → "
              f"{'стабильна' if broken == 0 else 'нестабильна'}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def check_algorithm(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(is_sorted(res), f"нарушен порядок на {a}: получено {res}")
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        res = fn(list(a))
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_counters() -> None:
    """Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе."""
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    expect(comparisons == 10,
           f"selection_sort: неверный счётчик сравнений — {comparisons}, ожидалось 10")


def count_inversions(a: list) -> int:
    """Число инверсий (пар i < j, a[i] > a[j]) прямым перебором."""
    return sum(a[i] > a[j] for i in range(len(a)) for j in range(i + 1, len(a)))


def check_own_counters() -> None:
    """Счётчики пузырька, вставок и выбора на предсказуемых входах (формулы — в отчёте)."""
    n = 30
    asc, desc = list(range(n)), list(range(n, 0, -1))
    full = n * (n - 1) // 2
    got = bubble_sort(asc)[1:]
    expect(got == (n - 1, 0), f"bubble на упорядоченном: ожидалось ({n - 1}, 0), получено {got}")
    got = bubble_sort(desc)[1:]
    expect(got == (full, full), f"bubble на обратном: ожидалось ({full}, {full}), получено {got}")
    got = insertion_sort(asc)[1:]
    expect(got == (n - 1, 0), f"insertion на упорядоченном: ожидалось ({n - 1}, 0), получено {got}")
    got = insertion_sort(desc)[1:]
    expect(got == (full, full), f"insertion на обратном: ожидалось ({full}, {full}), получено {got}")
    got = selection_sort(desc)[1:]
    expect(got == (full, n // 2), f"selection на обратном: ожидалось ({full}, {n // 2}), получено {got}")
    # Инвариант: пузырёк делает ровно один обмен на инверсию, вставки — один сдвиг.
    rng = random.Random(1)
    for _ in range(100):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 40))]
        inv = count_inversions(a)
        expect(bubble_sort(a)[2] == inv, f"bubble: обменов не равно числу инверсий {inv} на {a}")
        expect(insertion_sort(a)[2] == inv, f"insertion: сдвигов не равно числу инверсий {inv} на {a}")
        n_a = len(a)
        expect(selection_sort(a)[1] == n_a * (n_a - 1) // 2, f"selection: сравнений не n(n-1)/2 на {a}")
        expect(selection_sort(a)[2] <= max(n_a - 1, 0), f"selection: обменов больше n-1 на {a}")


def check_input_untouched() -> None:
    """Все сортировки работают с копией: исходный список не меняется."""
    src = [5, 3, 5, 1, 4, 2]
    for name, fn in ALGORITHMS.items():
        a = list(src)
        fn(a)
        expect(a == src, f"{name}: изменил входной список — {a}")


def check_stability() -> None:
    """Пузырёк и вставки стабильны, выбор нестабилен (контрпример (2,a),(1,b),(2,c),(1,d))."""
    class Pair:
        def __init__(self, key, label):
            self.key, self.label = key, label

        def __lt__(self, other):
            return self.key < other.key

        def __gt__(self, other):
            return self.key > other.key

    src = [Pair(k, c) for k, c in [(2, "a"), (1, "b"), (2, "c"), (1, "d")]]
    order = lambda res: "".join(p.label for p in res)  # noqa: E731
    expect(order(bubble_sort(src)[0]) == "bdac", "bubble_sort нарушил стабильность")
    expect(order(insertion_sort(src)[0]) == "bdac", "insertion_sort нарушил стабильность")
    expect(order(selection_sort(src)[0]) == "bdca", "selection_sort: ожидался контрпример bdca")


def check_quick_properties() -> None:
    """QuickSort: воспроизводимость по seed, массивы из равных, длинные упорядоченные входы."""
    rng = random.Random(5)
    a = [rng.randint(0, 50) for _ in range(500)]
    expect(quick_sort(a, random.Random(3)) == quick_sort(a, random.Random(3)),
           "quick_sort не воспроизводим при одинаковом seed")
    n = 50_000  # Θ(n²) на таких входах не уложилось бы во время; рекурсии нет
    for data in ([7] * n, list(range(n)), list(range(n, 0, -1))):
        expect(quick_sort(data, random.Random(0)) == sorted(data),
               "quick_sort ошибся на длинном вырожденном входе")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_algorithm(fn)) for name, fn in ALGORITHMS.items()]
    checks.append(("счётчики", check_counters))
    checks.append(("счётчики пузырька и вставок", check_own_counters))
    checks.append(("вход не изменяется", check_input_untouched))
    checks.append(("стабильность", check_stability))
    checks.append(("свойства QuickSort", check_quick_properties))
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
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def log_log_slope(points: list[tuple[int, float]]) -> float:
    """Наклон МНК-прямой log t от log n — оценка показателя степени k в t ~ n^k."""
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(t) for _, t in points]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            / sum((x - mx) ** 2 for x in xs))


COUNTED = {"bubble_sort": bubble_sort, "insertion_sort": insertion_sort,
           "selection_sort": selection_sort}


def report_counters(seed: int) -> None:
    """Таблицы счётчиков сравнений и обменов простых сортировок (для отчёта)."""
    print("\nСчётчики операций простых сортировок (сравнения / обмены или сдвиги):")
    for name, fn in COUNTED.items():
        print(f"\n{name}:")
        for n in SIZES_QUADRATIC:
            cells = []
            for cls, data in make_inputs(n, seed).items():
                _, cmp_, mov = fn(data)
                cells.append(f"{cls}: {cmp_:>10} / {mov:>10}")
            print(f"  n={n:>5}  " + "   ".join(cells))


def plot_results(results: dict, out_dir: Path) -> None:
    """Три log-log графика (по классу входа) со всеми алгоритмами."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # сохранение в файл без графической оболочки
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib не установлен — графики пропущены "
              "(pip install -r requirements.txt)")
        return
    classes = ["упорядоченный", "случайный", "обратный"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, cls in zip(axes, classes):
        for name, by_class in results.items():
            pts = by_class[cls]
            ax.plot([n for n, _ in pts], [t for _, t in pts], marker="o",
                    label=f"{name} (наклон {log_log_slope(pts):.2f})")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("размер входа n")
        ax.set_title(f"Вход: {cls}")
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("время, с")
    fig.tight_layout()
    path = out_dir / "lab03_loglog.png"
    fig.savefig(path, dpi=150)
    print(f"\nГрафик сохранён:\n  {path}")


def run_benchmarks(seed: int, out_dir: Path | None = None) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    results: dict[str, dict[str, list[tuple[int, float]]]] = {}
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        results[name] = {}
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                results[name].setdefault(cls, []).append((n, t))
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")

    print("\nНаклоны log-log (ожидается: 1 — линейное, ~1.1 — n log n, 2 — квадратичное):")
    for name, by_class in results.items():
        print(f"  {name:<15} " + "  ".join(
            f"{cls}: {log_log_slope(pts):.2f}" for cls, pts in by_class.items()))
    # Сопоставление наклонов с O(n^2) и O(n log n), лучший случай вставок и
    # поведение пузырька на упорядоченном входе — отчёт, п. 4.
    report_counters(seed)
    plot_results(results, out_dir or Path.cwd())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path.cwd(),
                    help="каталог для графиков (по умолчанию текущий)")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed, args.out)


if __name__ == "__main__":
    main()
