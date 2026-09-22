from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    department = Column(String)
    year = Column(String)
    semester = Column(String)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, unique=True, nullable=False)
    subject_name = Column(String, nullable=False)
    credits = Column(Integer, default=3)
    semester = Column(String)


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    internal_marks = Column(Float, nullable=False)
    external_marks = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    grade = Column(String)
    result = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)