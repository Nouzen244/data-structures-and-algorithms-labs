# СИАОД — ДЗ 1 (Кейс 1). Вариант 17

Дополнительное практическое задание 1 «Верификация ИИ-сгенерированной сортировки»
(КИМ-01, после раздела 2 «Алгоритмы сортировки»).
Задание и методики — в курсовом репозитории
[mel0d1an/data-structures-and-algorithms](https://github.com/mel0d1an/data-structures-and-algorithms).

**Вариант 17 → seed генератора данных = 30 + 17 = 47.**

## Состав

| Путь | Содержимое |
| --- | --- |
| [`dz01-ai-code.py`](dz01-ai-code.py) | исходный ИИ-сгенерированный код (без изменений) |
| [`dz01_ai_code_fixed.py`](dz01_ai_code_fixed.py) | исправленная версия `quicksort` (3-way partition + медиана из трёх) |
| [`dz01_verification.py`](dz01_verification.py) | скрипт четырёхшаговой верификации (стартовая заготовка с заполненными TODO) |
| [`report/README.md`](report/README.md) | отчёт: дефекты, замеры, вердикт и повторная верификация |
| [`report/dz01_run.log`](report/dz01_run.log) | протокол запуска верификации |
| [`report/dz01_benchmarks.png`](report/dz01_benchmarks.png) | графики замеров исходной и исправленной версий |

## Воспроизведение

```bash
pip install matplotlib
python dz01_verification.py --variant 17 --out report
```
