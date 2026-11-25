#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки.

Каркас взят из стартовой заготовки КИМ-01 (Cases); заполнены только TODO
в соответствии с методикой верификации по шагам 1–4 (docs/ai-verification.md).
Исходный файл dz01-ai-code.py оставлен без изменений.

Запуск:
  python dz01_verification.py --variant 17
  python dz01_verification.py --variant 17 --target dz01_ai_code_fixed.py
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import time
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------

AI_CODE_PATH = Path(__file__).with_name("dz01-ai-code.py")


def load_quicksort(path: Path = AI_CODE_PATH):
    """Загружает функцию quicksort из указанного файла."""
    spec = importlib.util.spec_from_file_location("target_quicksort", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quicksort


quicksort = load_quicksort()

# ---------------------------------------------------------------------------
# 1. Шаг 1 методики: инварианты сортировки
# ---------------------------------------------------------------------------


def is_sorted(a: list[int]) -> bool:
    """Инвариант 1: последовательность упорядочена по неубыванию."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def same_multiset(a: list[int], b: list[int]) -> bool:
    """Инвариант 2: b — перестановка a (мультимножества элементов совпадают)."""
    return len(a) == len(b) and Counter(a) == Counter(b)


def check_invariants(original: list[int], result: list[int]) -> list[str]:
    """Возвращает список нарушенных инвариантов (пустой список — нарушений нет)."""
    violations: list[str] = []
    if not is_sorted(result):
        violations.append("нарушен инвариант 1: выход не упорядочен по неубыванию")
    if not same_multiset(original, result):
        violations.append(
            f"нарушен инвариант 2: выход не является перестановкой входа "
            f"(len: {len(original)} -> {len(result)})"
        )
    return violations


# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------


def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    """Именованные тестовые входы по классам методики."""
    return [
        ("граничный: пустой", []),
        ("граничный: один элемент", [42]),
        ("граничный: два элемента (упорядочены)", [1, 2]),
        ("граничный: два элемента (обратно)", [2, 1]),
        ("граничный: два равных элемента", [5, 5]),
        ("вырожденный: все элементы равны", [7] * 10),
        ("вырожденный: уже отсортированный", list(range(20))),
        ("вырожденный: обратно отсортированный", list(range(20, 0, -1))),
        (
            "типовой: случайный с дубликатами и отрицательными",
            [rng.randint(-10, 10) for _ in range(30)],
        ),
        (
            "типовой: случайный без дубликатов",
            rng.sample(range(-100, 100), 25),
        ),
    ]


def run_representative_tests(rng: random.Random, fn=None) -> None:
    """Прогоняет quicksort по всем классам входов и печатает нарушения инвариантов."""
    if fn is None:
        fn = quicksort
    print("\n--- Шаг 2. Репрезентативные тесты ---")
    for label, data in representative_cases(rng):
        snapshot = list(data)
        try:
            res = fn(data)
        except Exception as err:  # noqa: BLE001
            print(f"  [{label}] ИСКЛЮЧЕНИЕ: {type(err).__name__}: {err}")
            continue
        violations = check_invariants(snapshot, res)
        if data != snapshot:
            violations.append("входной список был изменён на месте")
        if violations:
            print(f"  [{label}] FAIL: {'; '.join(violations)}")
            if len(snapshot) <= 20:
                print(f"      вход={snapshot} -> выход={res}")
        else:
            print(f"  [{label}] OK")


# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------


def compare_with_reference(rng: random.Random, runs: int = 300, fn=None) -> None:
    """Сверка quicksort с sorted() на сотнях случайных входов."""
    if fn is None:
        fn = quicksort
    print(f"\n--- Шаг 3. Сверка с эталоном sorted() ({runs} запусков) ---")
    mismatches = 0
    min_counterexample: tuple[list[int], list[int], list[int]] | None = None
    for _ in range(runs):
        n = rng.randint(0, 30)
        data = [rng.randint(-10, 10) for _ in range(n)]
        expected = sorted(data)
        got = fn(data)
        if got != expected:
            mismatches += 1
            if min_counterexample is None or len(data) < len(min_counterexample[0]):
                min_counterexample = (data, got, expected)
    print(f"  Всего прогонов: {runs}, расхождений: {mismatches}")
    if min_counterexample is not None:
        inp, got, exp = min_counterexample
        print(f"  Минимальный контрпример (len={len(inp)}):")
        print(f"    вход:    {inp}")
        print(f"    выход:   {got}")
        print(f"    эталон:  {exp}")


# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# (методика — docs/reproducibility.md: прогрев, >=5 повторов, медиана)
# ---------------------------------------------------------------------------

SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")


def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    """Вход размера n одного из трёх классов: random / sorted / reversed."""
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a


def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(data)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int, fn=None) -> dict[str, list[tuple[int, float | None]]]:
    """Замеры quicksort на трёх классах входов; аварийные завершения фиксируются."""
    if fn is None:
        fn = quicksort
    print("\n--- Шаг 4. Бенчмарк на трёх классах входов ---")
    rng = random.Random(seed)
    results: dict[str, list[tuple[int, float | None]]] = {k: [] for k in INPUT_KINDS}
    for kind in INPUT_KINDS:
        print(f"\nкласс входа: {kind}")
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                t = bench(fn, data)
                results[kind].append((n, t))
                print(f"  n={n:>6}  t={t:.6f} c")
            except RecursionError:
                results[kind].append((n, None))
                print(f"  n={n:>6}  RecursionError")
    return results


def save_benchmark_plot(
    orig_res: dict[str, list[tuple[int, float | None]]],
    fixed_res: dict[str, list[tuple[int, float | None]]],
    out_dir: Path,
) -> None:
    """Строит график сравнения времени работы исходной и исправленной версий."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.5))

    for kind, fmt in (("random", "o-"), ("sorted", "s-"), ("reversed", "^-")):
        pts = [(n, t) for n, t in orig_res[kind] if t is not None]
        if pts:
            ax1.plot([p[0] for p in pts], [p[1] for p in pts], fmt, label=f"{kind} (исходная)")
        pts_f = [(n, t) for n, t in fixed_res[kind] if t is not None]
        if pts_f:
            ax2.plot([p[0] for p in pts_f], [p[1] for p in pts_f], fmt, label=f"{kind} (исправленная)")

    ax1.set_title("Исходный dz01-ai-code.py (sorted/reversed → RecursionError)")
    ax1.set_xlabel("Размер массива n")
    ax1.set_ylabel("Медианное время, с")
    ax1.grid(True, ls="--", alpha=0.4)
    ax1.legend()

    ax2.set_title("Исправленный dz01_ai_code_fixed.py")
    ax2.set_xlabel("Размер массива n")
    ax2.set_ylabel("Медианное время, с")
    ax2.grid(True, ls="--", alpha=0.4)
    ax2.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "dz01_benchmarks.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Самопроверка каркаса (граничные случаи + сверка с эталоном stdlib)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    rng = random.Random(0)
    for _ in range(100):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
        assert is_sorted(sorted(a))
        assert same_multiset(a, sorted(a))
    print("self_check: OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path("report"), help="каталог для графиков")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()

    print("\n================ ВЕРИФИКАЦИЯ ИСХОДНОГО dz01-ai-code.py ================")
    orig_fn = load_quicksort(Path(__file__).with_name("dz01-ai-code.py"))
    rng = random.Random(seed)
    run_representative_tests(rng, orig_fn)
    compare_with_reference(rng, runs=300, fn=orig_fn)
    orig_res = run_benchmarks(seed, orig_fn)

    fixed_path = Path(__file__).with_name("dz01_ai_code_fixed.py")
    if fixed_path.exists():
        print("\n================ ПОВТОРНАЯ ВЕРИФИКАЦИЯ dz01_ai_code_fixed.py ================")
        fixed_fn = load_quicksort(fixed_path)
        rng_fixed = random.Random(seed)
        run_representative_tests(rng_fixed, fixed_fn)
        compare_with_reference(rng_fixed, runs=300, fn=fixed_fn)
        fixed_res = run_benchmarks(seed, fixed_fn)
        if args.out is not None:
            save_benchmark_plot(orig_res, fixed_res, args.out)


if __name__ == "__main__":
    main()
