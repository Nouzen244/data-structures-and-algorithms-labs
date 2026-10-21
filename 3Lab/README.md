# СИАОД — ЛР 3. Вариант 17

Лабораторная работа 3 «Экспериментальное сравнение простых сортировок;
QuickSort с рандомизацией опорного элемента» по дисциплине «Структуры и
алгоритмы обработки данных». Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`lab03_simple_sorts_quicksort.py`](lab03_simple_sorts_quicksort.py) | стартовая заготовка КИМ-03 с заполненными TODO |
| [`report/README.md`](report/README.md) | отчёт: сложность, счётчики, стабильность, графики, выводы |
| [`report/Saymanov_LR3_report.docx`](report/Saymanov_LR3_report.docx) | отчёт в формате docx |
| [`report/lab03_run.log`](report/lab03_run.log) | протокол запуска, на котором построен отчёт |

Входные массивы генерирует сама заготовка (`make_inputs`, детерминированно по
seed), отдельные файлы данных не нужны.

## Воспроизведение

```bash
pip install matplotlib
python lab03_simple_sorts_quicksort.py --variant 17 --out report
```
