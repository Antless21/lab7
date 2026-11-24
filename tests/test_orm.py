import pytest
from sqlalchemy.exc import IntegrityError

from lab7.orm_tasks import StudentRepository, demo


@pytest.fixture
def repository(tmp_path):
    repository = StudentRepository(tmp_path / "orm.sqlite3")
    yield repository
    repository.close()


def test_full_crud(repository):
    assert repository.list_all() == []
    created = repository.create("Александр", 20, "221341")
    assert repository.read(created["id"]) == created
    assert repository.list_all() == [created]
    updated = repository.update(created["id"], "Александр Мовчан", 21, "221342")
    assert updated == {
        "id": created["id"],
        "name": "Александр Мовчан",
        "age": 21,
        "group_name": "221342",
    }
    assert repository.read(created["id"]) == updated
    assert repository.delete(created["id"])
    assert repository.read(created["id"]) is None
    assert repository.list_all() == []


def test_missing_id(repository):
    assert repository.read(999) is None
    assert repository.update(999, "Имя", 20, "221341") is None
    assert not repository.delete(999)


@pytest.mark.parametrize("age", [-1, 0, 121])
def test_transaction_rollback(repository, age):
    created = repository.create("Александр", 20, "221341")
    with pytest.raises(IntegrityError):
        repository.update(created["id"], "Новое имя", age, "221342")
    assert repository.read(created["id"]) == created


@pytest.mark.parametrize("field", ["name", "group_name"])
def test_blank_fields(repository, field):
    data = {"name": "Имя", "age": 20, "group_name": "221341", field: " "}
    with pytest.raises(IntegrityError):
        repository.create(**data)
    assert repository.list_all() == []


def test_persistence(tmp_path):
    path = tmp_path / "orm.sqlite3"
    first = StudentRepository(path)
    try:
        created = first.create("Имя", 20, "221341")
    finally:
        first.close()
    second = StudentRepository(path)
    try:
        assert second.read(created["id"]) == created
    finally:
        second.close()


def test_quoted_name(repository):
    name = "O'Brien'); DROP TABLE orm_students;--"
    created = repository.create(name, 20, "221341")
    assert repository.read(created["id"])["name"] == name


def test_demo(tmp_path):
    result = demo(tmp_path / "demo.sqlite3")
    assert result["created"] == result["read"]
    assert result["updated"]["age"] == 21
    assert result["deleted"] is True
    assert result["after_delete"] is None
