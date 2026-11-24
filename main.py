"""Запуск: python main.py sqlite | orm | postgres | all."""

import argparse
import json
import os
import sqlite3
from pathlib import Path

import psycopg2
from sqlalchemy.exc import SQLAlchemyError

from lab7 import orm_tasks, postgres_tasks, sqlite_tasks

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Лабораторная №7, вариант 2")
    parser.add_argument("task", choices=["sqlite", "orm", "postgres", "all"])
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    dsn = os.getenv("POSTGRES_DSN", "")
    if args.task in {"postgres", "all"} and not dsn:
        parser.error("Задайте POSTGRES_DSN для подключения к PostgreSQL (см. README).")

    try:
        if args.task in {"sqlite", "all"}:
            print("SQLite — INSERT, UPDATE, две таблицы:")
            print(
                json.dumps(
                    sqlite_tasks.demo(args.data_dir / "sqlite.sqlite3"),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        if args.task in {"orm", "all"}:
            print("SQLAlchemy ORM — CRUD:")
            print(
                json.dumps(
                    orm_tasks.demo(args.data_dir / "orm.sqlite3"),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        if args.task in {"postgres", "all"}:
            print("PostgreSQL через psycopg2:")
            print(json.dumps(postgres_tasks.demo(dsn), ensure_ascii=False, indent=2))
    except sqlite3.Error as error:
        parser.exit(1, f"Ошибка SQLite: {error}\n")
    except psycopg2.Error:
        parser.exit(
            1, "Ошибка PostgreSQL: проверьте сервер, POSTGRES_DSN и права доступа.\n"
        )
    except SQLAlchemyError:
        parser.exit(1, "Ошибка SQLAlchemy: проверьте данные и доступ к файлу базы.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
