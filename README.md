# Лабораторная работа №7. Работа с различными СУБД в Python

**Мовчан Александр Дмитриевич, группа 221341, вариант 2, лабораторная №7.**

Дисциплина: «Методы и технологии программирования», часть 1.
Цель: освоить SQLite, SQLAlchemy ORM и PostgreSQL через psycopg2.

Репозиторий: <https://github.com/Antless21/lab7>.

## Задания варианта 2

По строке варианта 2 на странице 14 методических указаний:
средние задания **2, 4, 7**, повышенные **2, 6**. Условия находятся на странице 13.

| Сложность | № | Условие | Реализация |
|---|---:|---|---|
| Средняя | 2 | Вставить данные в таблицу | `lab7/sqlite_tasks.py`: `insert_student()`, SQL `INSERT` |
| Средняя | 4 | Обновить запись | `lab7/sqlite_tasks.py`: `update_student()`, SQL `UPDATE` |
| Средняя | 7 | Создать несколько таблиц | SQLite: `groups`, `students`, внешний ключ `group_id` |
| Повышенная | 2 | CRUD через ORM | `lab7/orm_tasks.py`: модель `Student`, класс `StudentRepository` |
| Повышенная | 6 | Работа с PostgreSQL через psycopg2 | `lab7/postgres_tasks.py`: подключение к серверу, создание таблицы, CRUD |

Все пять заданий доступны через одну консольную программу. Модули разделены
по технологиям, поэтому каждое задание можно проверить отдельно.

## Установка

Требуется Python **3.10+**. Для повышенного задания №6 дополнительно нужен
сервер PostgreSQL. Его можно запустить через Docker Compose или использовать
уже установленный PostgreSQL. Для SQLite и ORM отдельный сервер не нужен.

```bash
git clone https://github.com/Antless21/lab7.git
cd lab7
python -m venv .venv
```

Активировать окружение в Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

В macOS/Linux:

```bash
source .venv/bin/activate
```

Затем установить зависимости:

```bash
python -m pip install -r requirements.txt
```

Если `python` недоступен, для создания окружения используйте `python3`
(macOS/Linux) или `py` (Windows). Пакет `psycopg2-binary` предоставляет
модуль `psycopg2`, используемый в коде.

## Средние задания №2, №4, №7: SQLite

```bash
python main.py sqlite
```

Программа автоматически создаёт файл `data/sqlite.sqlite3` и две таблицы:

```text
groups
  id       INTEGER PRIMARY KEY
  name     TEXT UNIQUE NOT NULL

students
  id       INTEGER PRIMARY KEY
  name     TEXT NOT NULL
  age      INTEGER NOT NULL, 1–120
  group_id INTEGER NOT NULL REFERENCES groups(id)
```

Внешние ключи включаются командой `PRAGMA foreign_keys = ON`
при каждом подключении. Таблицы связываются отношением «одна группа — много
студентов». Для вывода используется JOIN.

Последовательность демонстрации:

1. Создать таблицы, если их ещё нет.
2. Добавить группу `221341`, если такая группа отсутствует.
3. Вставить студента через параметризованный `INSERT`.
4. Вывести запись с возрастом `20` в поле `inserted`.
5. Обновить возраст на `21` через `UPDATE ... WHERE id = ?`.
6. Вывести обновлённую запись в поле `updated` и общий список `students`.

Возраст в демонстрационных данных условный. Повторный запуск добавляет
новую запись студента; группа остаётся одна. Данные сохраняются в SQLite
после завершения программы. Несуществующая группа и возраст вне диапазона
отклоняются ограничениями базы данных.

## Повышенное задание №2: CRUD через SQLAlchemy ORM

```bash
python main.py orm
```

Используется отдельный файл `data/orm.sqlite3` и таблица `orm_students`.
Модель `Student` объявлена через `DeclarativeBase`, `Mapped` и `mapped_column`.

| Операция | Метод | Механизм ORM |
|---|---|---|
| Create | `create(name, age, group_name)` | `session.add()`, `session.flush()` |
| Read | `read(id)`, `list_all()` | `session.get()`, `select(Student)` |
| Update | `update(id, name, age, group_name)` | Изменение атрибутов объекта |
| Delete | `delete(id)` | `session.delete()` |

Демонстрация выводит `created`, `read`, `updated`, `deleted`, `after_delete`.
После удаления `deleted` равно `true`, `after_delete` равно `null`.
Удаляется только запись, созданная текущей демонстрацией.

Каждая изменяющая операция выполняется внутри `session.begin()`:
при успехе транзакция фиксируется, при исключении откатывается.
Методы чтения и обновления возвращают `None` для отсутствующего ID,
удаление возвращает `False`.

## Повышенное задание №6: PostgreSQL через psycopg2

### Запуск PostgreSQL через Docker Compose

При установленном и запущенном Docker выполнить из папки проекта:

```bash
docker compose up -d --wait
```

Будет запущен PostgreSQL 17: база `lab7`, пользователь `lab7`, учебный пароль
`lab7_local`, адрес `127.0.0.1:5433`. Файл `compose.yaml` содержит эту
локальную учебную конфигурацию. База хранится в Docker volume `lab7_data`.

Указать подключение в Windows PowerShell:

```powershell
$env:POSTGRES_DSN = "postgresql://lab7:lab7_local@127.0.0.1:5433/lab7"
python main.py postgres
```

В macOS/Linux:

```bash
export POSTGRES_DSN='postgresql://lab7:lab7_local@127.0.0.1:5433/lab7'
python main.py postgres
```

Если PostgreSQL уже установлен, создать в нём отдельную учебную базу
и задать `POSTGRES_DSN` со своими адресом, портом, пользователем и паролем.
Пользователю нужны права подключения и создания схемы в выбранной базе.

### Что выполняет программа

1. Подключается к настоящему серверу через `psycopg2.connect()`.
2. Создаёт схему `lab7` и таблицу `lab7.students`, если они отсутствуют.
3. Вставляет студента через `INSERT ... VALUES (%s, %s, %s) RETURNING *`.
4. Читает запись, обновляет возраст с 20 на 21, удаляет эту запись.
5. Показывает результат каждой операции в JSON.

Операции выполняются через курсоры psycopg2, параметры передаются отдельно
от SQL. Для имён схем и таблиц применяется `psycopg2.sql.Identifier`.
Соединения закрываются, изменения фиксируются транзакцией; при ошибке
выполняется rollback. Остальные записи базы демонстрация не удаляет.

Без `POSTGRES_DSN` команда сообщает о необходимой настройке и завершается
с кодом 2. При ошибке подключения возвращается код 1.

### Все задания одним запуском

После настройки `POSTGRES_DSN`:

```bash
python main.py all
```

Путь для файлов SQLite можно изменить:

```bash
python main.py sqlite --data-dir ./my_data
python main.py orm --data-dir ./my_data
```

Справка: `python main.py --help`.

После работы остановить Docker-сервис:

```bash
docker compose down
```

## Автоматические проверки

Локально проверено на Python 3.10.9 и PostgreSQL 17.10: **29 тестов пройдено
без пропусков**, Ruff — без ошибок. Команда `python main.py all` выполнена
с подключением к настоящему PostgreSQL.

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest -q
```

При заданном `POSTGRES_DSN` выполняются также интеграционные тесты
настоящего PostgreSQL. Они создают отдельную схему со случайным именем
и удаляют её после теста. Данные демонстрационной схемы `lab7` не затрагиваются.
Без `POSTGRES_DSN` только PostgreSQL-тесты будут пропущены.

Проверяются: создание нескольких таблиц, внешний ключ, вставка и обновление,
сохранение данных между подключениями, полный CRUD ORM, откат ошибочных
изменений, строки с кавычками и SQL-подобным текстом, PostgreSQL и команды CLI.

GitHub Actions запускает проверки на Python 3.10 и 3.13, поднимает PostgreSQL 17
как сервис, выполняет все тесты и команду `python main.py all`.

## Структура

```text
main.py                  — консольный запуск примеров
lab7/sqlite_tasks.py     — три средних задания
lab7/orm_tasks.py        — CRUD через SQLAlchemy ORM
lab7/postgres_tasks.py   — PostgreSQL через psycopg2
tests/                   — проверки трёх модулей и CLI
compose.yaml             — локальный сервер PostgreSQL
.github/workflows/       — проверки на GitHub
requirements.txt         — зависимости программы
requirements-dev.txt     — зависимости для проверок
```

Файлы баз, виртуальное окружение и кеши исключены через `.gitignore`.

## Сдача

После изменения исходников:

```bash
git add .
git commit -m "fix: update lab 7"
git push --all && git push --tags
```

Для лабораторной №7 дополнительные ветки и теги методичкой не требуются.
Когда @NoMercy_Review_bot заработает, проверить дедлайн командой `/help`
и отправить отдельным сообщением ссылку <https://github.com/Antless21/lab7>.
По условиям сдачи — до трёх попыток, новая попытка только после «не принята»;
принятую работу пересдать нельзя.

## Источники

- Методические указания, часть 1, лабораторные работы 1–8: страницы 13–14.
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [psycopg2: Basic module usage](https://www.psycopg.org/docs/usage.html)
- [GitHub Actions: PostgreSQL service](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)
