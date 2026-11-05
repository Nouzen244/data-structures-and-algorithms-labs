# СИАОД — ЛР 4. Вариант 17

Лабораторная работа 4 «MergeSort, Counting, Radix и HeapSort:
оценка производительности» по дисциплине «Структуры и
алгоритмы обработки данных». Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab04_mergesort_linear_heapsort.py`](lab04_mergesort_linear_heapsort.py) | стартовая заготовка КИМ-04 с заполненными TODO |
| [`report/README.md`](report/README.md) | отчёт: анализ алгоритмов, таблица свойств, графики, выводы |
| [`report/Saymanov_LR4_report.docx`](report/Saymanov_LR4_report.docx) | отчёт в формате docx |
| [`report/lab04_run.log`](report/lab04_run.log) | протокол запуска, на котором построен отчёт |

Входные массивы генерирует сама заготовка (`make_datasets`, детерминированно по
seed), отдельные файлы данных не нужны.

## Воспроизведение

```bash
pip install matplotlib
python lab04_mergesort_linear_heapsort.py --variant 17 --out report
```
