# СИАОД — ДЗ 2 (Кейс 2). Вариант 17

Дополнительное практическое задание 2 «Эксперимент: высота BST и деградация операций»
(КИМ-02, после раздела 3 «Деревья и иерархические структуры», ЛР 5).
Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`dz02_bst_height.py`](dz02_bst_height.py) | стартовая заготовка КИМ-02 с заполненными TODO (итеративное BST, замеры, графики) |
| [`report/README.md`](report/README.md) | отчёт: таблицы, графики, справка об AVL, выводы и рекомендации |
| [`report/dz02_run.log`](report/dz02_run.log) | протокол запуска эксперимента |
| [`report/dz02_bst_height.png`](report/dz02_bst_height.png) | графики высоты `h(n)` и средней глубины `d(n)` на фоне `log₂(n)` и `n` |
| [`report/dz02_search_time.png`](report/dz02_search_time.png) | график сравнения времени поиска в случайном и вырожденном BST |

## Воспроизведение

```bash
pip install matplotlib
python dz02_bst_height.py --variant 17 --out report
```
