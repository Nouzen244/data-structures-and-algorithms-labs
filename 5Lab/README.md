# СИАОД — ЛР 5. Вариант 17

Лабораторная работа 5 «Построение бинарного дерева поиска и реализация обходов;
вставка и удаление элементов» по дисциплине «Структуры и алгоритмы обработки данных».
Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab05_bst.py`](lab05_bst.py) | стартовая заготовка КИМ-05 с заполненными TODO |
| [`report/README.md`](report/README.md) | отчёт: обходы, удаление, верификация, замеры поиска, выводы |
| [`report/lab05_run.log`](report/lab05_run.log) | протокол запуска, на котором построен отчёт |
| [`report/lab05_bst_search.png`](report/lab05_bst_search.png) | графики времени поиска (`BST` против `list`) и высоты `h(n)` |

## Воспроизведение

```bash
pip install matplotlib
python lab05_bst.py --variant 17 --out report
```
