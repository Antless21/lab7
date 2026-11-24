"""Средние задания №2, №4, №7: INSERT, UPDATE и две связанные таблицы."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connect(path: str | Path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK (length(trim(name)) > 0),
            age INTEGER NOT NULL CHECK (age BETWEEN 1 AND 120),
            group_id INTEGER NOT NULL REFERENCES groups(id)
        )""")


def add_group(path: str | Path, name: str) -> int:
    with connect(path) as db:
        db.execute(
            "INSERT INTO groups (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
            (name,),
        )
        return db.execute("SELECT id FROM groups WHERE name = ?", (name,)).fetchone()[0]


def insert_student(path: str | Path, name: str, age: int, group_id: int) -> int:
    with connect(path) as db:
        cursor = db.execute(
            "INSERT INTO students (name, age, group_id) VALUES (?, ?, ?)",
            (name, age, group_id),
        )
        return cursor.lastrowid


def update_student(path: str | Path, student_id: int, age: int) -> bool:
    with connect(path) as db:
        cursor = db.execute(
            "UPDATE students SET age = ? WHERE id = ?", (age, student_id)
        )
        return cursor.rowcount == 1


def list_students(path: str | Path) -> list[dict]:
    with connect(path) as db:
        rows = db.execute("""SELECT s.id, s.name, s.age, g.name AS group_name
            FROM students AS s JOIN groups AS g ON s.group_id = g.id
            ORDER BY s.id""")
        return [dict(row) for row in rows]


def demo(path: str | Path) -> dict:
    initialize(path)
    group_id = add_group(path, "221341")
    student_id = insert_student(path, "Мовчан Александр Дмитриевич", 20, group_id)
    before = next(row for row in list_students(path) if row["id"] == student_id)
    update_student(path, student_id, 21)
    after = next(row for row in list_students(path) if row["id"] == student_id)
    return {"inserted": before, "updated": after, "students": list_students(path)}
