# СИАОД — ЛР 2. Вариант 17

Лабораторная работа 2 «Реализация рекурсивных функций и динамического массива,
стека и дека» по дисциплине «Структуры и алгоритмы обработки данных».
Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab02_recursion_structures.py`](lab02_recursion_structures.py) | стартовая заготовка КИМ-02 с заполненными TODO |
| [`report/README.md`](report/README.md) | отчёт: число вызовов, графики, амортизированный анализ, выводы |
| [`report/lab02_run.log`](report/lab02_run.log) | протокол запуска, на котором построен отчёт |
| [`scripts/generate_data.py`](scripts/generate_data.py) | генератор данных варианта (копия из курсового репозитория) |
| `data/generated/` | данные варианта; в git не коммитятся, воспроизводятся по seed |

## Воспроизведение

```bash
pip install numpy matplotlib
python scripts/generate_data.py --variant 17 --only ops --out data/generated
python lab02_recursion_structures.py --variant 17 --out report
```

Скрипт сверяет номер варианта с паспортом данных `data/generated/manifest.json`
и откажется работать на чужих данных.
