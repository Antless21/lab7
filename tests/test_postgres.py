import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2 import sql

from lab7.postgres_tasks import PostgresRepository

pytestmark = pytest.mark.postgres


@pytest.fixture
def repository():
    dsn = os.getenv("POSTGRES_DSN")
    if not dsn:
        pytest.skip("Нужен POSTGRES_DSN с доступом к настоящему PostgreSQL")
    repository = PostgresRepository(dsn, schema=f"lab7_test_{uuid4().hex}")
    repository.initialize()
    try:
        yield repository
    finally:
        with repository.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(
                    sql.Identifier(repository.schema)
                )
            )


def test_real_postgres_crud(repository):
    assert repository.list_all() == []
    created = repository.create("Александр", 20, "221341")
    assert repository.read(created["id"]) == created
    assert repository.list_all() == [created]
    assert repository.update(created["id"], 21)["age"] == 21
    assert repository.read(created["id"])["age"] == 21
    assert repository.delete(created["id"])
    assert repository.read(created["id"]) is None
    assert repository.list_all() == []


def test_missing_id(repository):
    assert repository.read(999) is None
    assert repository.update(999, 21) is None
    assert not repository.delete(999)


@pytest.mark.parametrize("age", [-1, 0, 121])
def test_rollback(repository, age):
    created = repository.create("Имя", 20, "221341")
    with pytest.raises(psycopg2.IntegrityError):
        repository.update(created["id"], age)
    assert repository.read(created["id"])["age"] == 20
    assert repository.update(created["id"], 21)["age"] == 21


def test_sql_parameters(repository):
    name = "O'Brien'); DROP TABLE students;--"
    created = repository.create(name, 20, "221341")
    assert repository.read(created["id"])["name"] == name
    assert len(repository.list_all()) == 1


def test_reinitialize_preserves_data(repository):
    created = repository.create("Имя", 20, "221341")
    repository.initialize()
    reopened = PostgresRepository(repository.dsn, repository.schema)
    assert reopened.read(created["id"]) == created
