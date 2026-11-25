# СИАОД — ЛР 6. Вариант 17

Лабораторная работа 6 «Линейный, бинарный и интерполяционный поиск: сравнение»
по дисциплине «Структуры и алгоритмы обработки данных».
Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab06_search.py`](lab06_search.py) | стартовая заготовка КИМ-06 с заполненными TODO |
| [`report/README.md`](report/README.md) | отчёт: сравнение алгоритмов на двух распределениях, верификация, выводы |
| [`report/lab06_run.log`](report/lab06_run.log) | протокол запуска, на котором построен отчёт |
| [`report/lab06_uniform.png`](report/lab06_uniform.png) | графики числа сравнений и времени (равномерное распределение) |
| [`report/lab06_exponential.png`](report/lab06_exponential.png) | графики числа сравнений и времени (экспоненциальное распределение) |

## Воспроизведение

```bash
pip install matplotlib
python lab06_search.py --variant 17 --out report
```
