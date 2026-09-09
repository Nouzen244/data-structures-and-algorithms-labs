# СИАОД — лабораторные работы. Вариант 17

Личный репозиторий по дисциплине «Структуры и алгоритмы обработки данных».
Задания и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab01_complexity.py`](lab01_complexity.py) | ЛР 1: стартовая заготовка КИМ-01 с заполненными TODO |
| [`report/README.md`](report/README.md) | ЛР 1: отчёт — аналитические оценки, графики, выводы |
| [`report/lab01_run.log`](report/lab01_run.log) | протокол запуска, на котором построен отчёт |
| [`scripts/generate_data.py`](scripts/generate_data.py) | генератор данных варианта (копия из курсового репозитория) |
| `data/generated/` | данные варианта; в git не коммитятся, воспроизводятся по seed |

## Воспроизведение ЛР 1

```bash
python -m venv .venv && .venv\Scripts\activate
pip install numpy matplotlib
python scripts/generate_data.py --variant 17 --only arrays --out data/generated
python lab01_complexity.py --variant 17 --out report
```

Скрипт сверяет номер варианта с паспортом данных `data/generated/manifest.json`
и откажется работать на чужих данных.

Данные детерминированы: при одном и том же варианте файлы совпадают побайтно,
поэтому каталог `data/generated/` в репозиторий не коммитится (см. `.gitignore`).
