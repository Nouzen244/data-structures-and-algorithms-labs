#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций.

Каркас взят из стартовой заготовки КИМ-02 (Cases); заполнены только TODO
в соответствии с методикой эксперимента и верификации (docs/ai-verification.md).

Запуск: python dz02_bst_height.py --variant 17
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень дерева.

    Дубликаты игнорируются (ключи в эксперименте уникальны).
    """
    if root is None:
        return Node(key)
    cur = root
    while True:
        if key < cur.key:
            if cur.left is None:
                cur.left = Node(key)
                return root
            cur = cur.left
        elif key > cur.key:
            if cur.right is None:
                cur.right = Node(key)
                return root
            cur = cur.right
        else:
            return root


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------


def tree_height(root: Node | None) -> int:
    """Высота дерева: число рёбер на самом длинном пути от корня до листа.

    Пустое дерево: -1; один узел: 0. Реализовано итеративно.
    """
    if root is None:
        return -1
    max_depth = 0
    stack: list[tuple[Node, int]] = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > max_depth:
            max_depth = depth
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return max_depth


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно."""
    if root is None:
        return 0
    total = 0
    stack: list[tuple[Node, int]] = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        total += depth
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return total


def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно."""
    if root is None:
        return 0
    count = 0
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        count += 1
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return count


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла: sum_depths / count_nodes (0.0 для пустого)."""
    n = count_nodes(root)
    if n == 0:
        return 0.0
    return sum_depths(root) / n


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком) — для верификации."""
    result: list[int] = []
    stack: list[Node] = []
    cur = root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        result.append(cur.key)
        cur = cur.right
    return result


# ---------------------------------------------------------------------------
# 3. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    # Граничные случаи: пустое дерево и один узел
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1

    # Типовой случай: [2, 1, 3] — идеально сбалансированное дерево из 3 узлов
    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2  # 0 (корень) + 1 + 1

    # Вырожденный случай: упорядоченные ключи 1..n дают "список"
    n = 100
    degenerate = build_bst(list(range(1, n + 1)))
    assert tree_height(degenerate) == n - 1
    assert avg_depth(degenerate) == (n - 1) / 2  # (0+1+...+(n-1)) / n

    # Сверка с эталоном стандартной библиотеки: инвариант BST —
    # in-order-обход совпадает с sorted() на случайных наборах ключей
    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и каркас замеров (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]  # геометрический шаг, n до 10^4
REPEATS = 5
SEARCH_QUERIES = 300


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей (детерминированно по seed варианта)."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n — худший поток вставок для BST."""
    return list(range(1, n + 1))


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""

    def run() -> None:
        for q in queries:
            node = root
            while node is not None and node.key != q:
                node = node.left if q < node.key else node.right

    run()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def save_plots(rows: list[tuple[int, int, float, int, float, float, float]], out_dir: Path) -> None:
    """Строит графики высоты h(n), средней глубины d(n) и времени поиска."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    ns = [r[0] for r in rows]
    h_rand = [r[1] for r in rows]
    d_rand = [r[2] for r in rows]
    h_ord = [r[3] for r in rows]
    d_ord = [r[4] for r in rows]
    t_rand = [r[5] for r in rows]
    t_ord = [r[6] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    ax1.loglog(ns, h_rand, "o-", label="h(n) случайный поток")
    ax1.loglog(ns, h_ord, "s-", label="h(n) упорядоченный поток")
    ax1.loglog(ns, [math.log2(n) for n in ns], "--", label="log₂(n)")
    ax1.loglog(ns, [1.44 * math.log2(n) for n in ns], ":", label="1,44·log₂(n) (граница AVL)")
    ax1.loglog(ns, ns, "-.", label="n")
    ax1.set_title("Высота BST h(n) (log-log)")
    ax1.set_xlabel("Число узлов n")
    ax1.set_ylabel("Высота дерева h")
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend(fontsize=8)

    ax2.loglog(ns, d_rand, "o-", label="d(n) случайный поток")
    ax2.loglog(ns, d_ord, "s-", label="d(n) упорядоченный поток")
    ax2.loglog(ns, [math.log2(n) for n in ns], "--", label="log₂(n)")
    ax2.loglog(ns, [(n - 1) / 2 for n in ns], "-.", label="(n − 1) / 2")
    ax2.set_title("Средняя глубина узла d(n) (log-log)")
    ax2.set_xlabel("Число узлов n")
    ax2.set_ylabel("Средняя глубина d")
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out_dir / "dz02_bst_height.png", dpi=150)
    plt.close(fig)

    fig2, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.loglog(ns, t_rand, "o-", label=f"случайное BST ({SEARCH_QUERIES} поисков)")
    ax.loglog(ns, t_ord, "s-", label=f"вырожденное BST ({SEARCH_QUERIES} поисков)")
    ax.set_title("Время поиска в случайном и вырожденном BST (log-log)")
    ax.set_xlabel("Число узлов n")
    ax.set_ylabel("Медианное время, с")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.legend()
    fig2.tight_layout()
    fig2.savefig(out_dir / "dz02_search_time.png", dpi=150)
    plt.close(fig2)


def run_experiment(seed: int, out_dir: Path | None = None) -> None:
    """Таблица: n, высота, средняя глубина и время поиска для двух потоков."""
    rng = random.Random(seed)
    header = (
        f"{'n':>7} {'h_случ':>8} {'d_случ':>8} "
        f"{'h_упор':>8} {'d_упор':>8} {'log2(n)':>8} "
        f"{'t_случ, с':>11} {'t_упор, с':>11}"
    )
    print(header)
    rows: list[tuple[int, int, float, int, float, float, float]] = []
    for n in SIZES:
        r_keys = random_keys(n, rng)
        o_keys = ordered_keys(n)
        root_rand = build_bst(r_keys)
        root_ord = build_bst(o_keys)

        # Одинаковые по структуре запросы: половина присутствующих, половина отсутствующих
        q_rand = [r_keys[rng.randrange(n)] for _ in range(SEARCH_QUERIES // 2)] + [
            rng.randint(0, 10 * n) for _ in range(SEARCH_QUERIES // 2)
        ]
        q_ord = [o_keys[rng.randrange(n)] for _ in range(SEARCH_QUERIES // 2)] + [
            rng.randint(1, 2 * n) for _ in range(SEARCH_QUERIES // 2)
        ]

        hr = tree_height(root_rand)
        dr = avg_depth(root_rand)
        ho = tree_height(root_ord)
        do = avg_depth(root_ord)
        tr = bench_search(root_rand, q_rand)
        to = bench_search(root_ord, q_ord)
        rows.append((n, hr, dr, ho, do, tr, to))
        print(
            f"{n:>7} {hr:>8} {dr:>8.1f} {ho:>8} {do:>8.1f} "
            f"{math.log2(n):>8.1f} {tr:>11.6f} {to:>11.6f}"
        )

    if out_dir is not None:
        save_plots(rows, out_dir)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", type=Path, default=Path("report"), help="каталог для графиков")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed, args.out)


if __name__ == "__main__":
    main()
