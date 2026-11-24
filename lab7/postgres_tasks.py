"""Повышенное №6: настоящий PostgreSQL через драйвер psycopg2."""

from contextlib import contextmanager

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class PostgresRepository:
    def __init__(self, dsn: str, schema: str = "lab7"):
        self.dsn = dsn
        self.schema = schema
        self.table = sql.Identifier(schema, "students")

    @contextmanager
    def connect(self):
        connection = psycopg2.connect(self.dsn, connect_timeout=5)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(self.schema)
                )
            )
            cursor.execute(
                sql.SQL("""CREATE TABLE IF NOT EXISTS {} (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                    age INTEGER NOT NULL CHECK (age BETWEEN 1 AND 120),
                    group_name TEXT NOT NULL CHECK (length(trim(group_name)) > 0)
                )""").format(self.table)
            )

    def create(self, name: str, age: int, group_name: str) -> dict:
        with self.connect() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    sql.SQL("""INSERT INTO {} (name, age, group_name)
                        VALUES (%s, %s, %s) RETURNING *""").format(self.table),
                    (name, age, group_name),
                )
                return dict(cursor.fetchone())

    def read(self, student_id: int) -> dict | None:
        with self.connect() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    sql.SQL("SELECT * FROM {} WHERE id = %s").format(self.table),
                    (student_id,),
                )
                row = cursor.fetchone()
                return dict(row) if row is not None else None

    def list_all(self) -> list[dict]:
        with self.connect() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    sql.SQL("SELECT * FROM {} ORDER BY id").format(self.table)
                )
                return [dict(row) for row in cursor.fetchall()]

    def update(self, student_id: int, age: int) -> dict | None:
        with self.connect() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    sql.SQL("UPDATE {} SET age = %s WHERE id = %s RETURNING *").format(
                        self.table
                    ),
                    (age, student_id),
                )
                row = cursor.fetchone()
                return dict(row) if row is not None else None

    def delete(self, student_id: int) -> bool:
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DELETE FROM {} WHERE id = %s").format(self.table),
                (student_id,),
            )
            return cursor.rowcount == 1


def demo(dsn: str) -> dict:
    repository = PostgresRepository(dsn)
    repository.initialize()
    created = repository.create("Мовчан Александр Дмитриевич", 20, "221341")
    try:
        read = repository.read(created["id"])
        updated = repository.update(created["id"], 21)
        deleted = repository.delete(created["id"])
        return {
            "created": created,
            "read": read,
            "updated": updated,
            "deleted": deleted,
            "after_delete": repository.read(created["id"]),
        }
    finally:
        # Удаляется только запись текущего запуска демонстрации.
        repository.delete(created["id"])
