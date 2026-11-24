"""Повышенное №2: Create, Read, Update, Delete через SQLAlchemy ORM."""

from pathlib import Path

from sqlalchemy import CheckConstraint, String, create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "orm_students"
    __table_args__ = (
        CheckConstraint("age BETWEEN 1 AND 120"),
        CheckConstraint("length(trim(name)) > 0"),
        CheckConstraint("length(trim(group_name)) > 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int]
    group_name: Mapped[str] = mapped_column(String(30))


def as_dict(student: Student) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "age": student.age,
        "group_name": student.group_name,
    }


class StudentRepository:
    def __init__(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(URL.create("sqlite", database=str(path)))
        Base.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def create(self, name: str, age: int, group_name: str) -> dict:
        with Session(self.engine) as session, session.begin():
            student = Student(name=name, age=age, group_name=group_name)
            session.add(student)
            session.flush()
            return as_dict(student)

    def read(self, student_id: int) -> dict | None:
        with Session(self.engine) as session:
            student = session.get(Student, student_id)
            return as_dict(student) if student is not None else None

    def list_all(self) -> list[dict]:
        with Session(self.engine) as session:
            return [
                as_dict(student)
                for student in session.scalars(select(Student).order_by(Student.id))
            ]

    def update(
        self, student_id: int, name: str, age: int, group_name: str
    ) -> dict | None:
        with Session(self.engine) as session, session.begin():
            student = session.get(Student, student_id)
            if student is None:
                return None
            student.name, student.age, student.group_name = name, age, group_name
            session.flush()
            return as_dict(student)

    def delete(self, student_id: int) -> bool:
        with Session(self.engine) as session, session.begin():
            student = session.get(Student, student_id)
            if student is None:
                return False
            session.delete(student)
            return True


def demo(path: str | Path) -> dict:
    repository = StudentRepository(path)
    try:
        created = repository.create("Мовчан Александр Дмитриевич", 20, "221341")
        read = repository.read(created["id"])
        updated = repository.update(created["id"], created["name"], 21, "221341")
        deleted = repository.delete(created["id"])
        return {
            "created": created,
            "read": read,
            "updated": updated,
            "deleted": deleted,
            "after_delete": repository.read(created["id"]),
        }
    finally:
        repository.close()
