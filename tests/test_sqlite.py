import sqlite3

import pytest

from lab7 import sqlite_tasks as db


@pytest.fixture
def path(tmp_path):
    path = tmp_path / "data" / "students.sqlite3"
    db.initialize(path)
    return path


def test_two_tables_and_foreign_key(path):
    with db.connect(path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        assert {row[0] for row in tables} == {"groups", "students"}
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_student(path, "Студент", 20, 999)


def test_insert_update_and_persistence(path):
    group_id = db.add_group(path, "221341")
    assert db.add_group(path, "221341") == group_id
    student_id = db.insert_student(path, "Александр", 20, group_id)
    assert db.list_students(path) == [
        {"id": student_id, "name": "Александр", "age": 20, "group_name": "221341"}
    ]
    assert db.update_student(path, student_id, 21)
    db.initialize(path)
    assert db.list_students(path)[0]["age"] == 21
    assert not db.update_student(path, 999, 22)


@pytest.mark.parametrize("age", [-1, 0, 121])
def test_invalid_age_rolls_back(path, age):
    group_id = db.add_group(path, "221341")
    student_id = db.insert_student(path, "Студент", 20, group_id)
    with pytest.raises(sqlite3.IntegrityError):
        db.update_student(path, student_id, age)
    assert db.list_students(path)[0]["age"] == 20


def test_sql_parameters(path):
    name = "O'Brien'); DROP TABLE students;--"
    group_id = db.add_group(path, "221341")
    db.insert_student(path, name, 20, group_id)
    assert db.list_students(path)[0]["name"] == name


def test_blank_values_rejected(path):
    with pytest.raises(sqlite3.IntegrityError):
        db.add_group(path, " ")
    group_id = db.add_group(path, "221341")
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_student(path, " ", 20, group_id)


def test_demo(path):
    result = db.demo(path)
    assert result["inserted"]["age"] == 20
    assert result["updated"]["age"] == 21
    assert result["students"][0]["group_name"] == "221341"
