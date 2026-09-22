from fastapi import FastAPI, Request, Form, Depends  # type: ignore[reportMissingImports]
from fastapi.responses import HTMLResponse, RedirectResponse  # type: ignore[reportMissingImports]
from fastapi.staticfiles import StaticFiles  # type: ignore[reportMissingImports]
from fastapi.templating import Jinja2Templates  # type: ignore[reportMissingImports]

from sqlalchemy.orm import Session

from database import engine, Base, get_db  # type: ignore[reportMissingImports]
from models import Student, Subject, Mark, User  # type: ignore[reportMissingImports]

from starlette.middleware.sessions import SessionMiddleware  # type: ignore[reportMissingImports]


# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Student Result Management System"
)


app.add_middleware(
    SessionMiddleware,
    secret_key="student-result-secret-key"
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# CREATE DEFAULT ADMIN
# --------------------------------------------------

def create_default_admin():

    db = next(get_db())

    existing_user = db.query(User).filter(
        User.username == "admin"
    ).first()

    if not existing_user:

        admin = User(
            username="admin",
            password="admin123",
            role="admin"
        )

        db.add(admin)
        db.commit()

    db.close()


create_default_admin()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return RedirectResponse("/login")


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
    request=request,
    name="login.html",
    context={}
)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    if user:

        request.session["user"] = user.username
        request.session["role"] = user.role

        return RedirectResponse(
            "/admin",
            status_code=303
        )

    return RedirectResponse(
        "/login?error=Invalid username or password",
        status_code=303
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/login")


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/login")

    student_count = db.query(Student).count()
    subject_count = db.query(Subject).count()
    mark_count = db.query(Mark).count()

    return templates.TemplateResponse(
    request=request,
    name="admin.html",
    context={
        "student_count": student_count,
        "subject_count": subject_count,
        "mark_count": mark_count
    }
)


# --------------------------------------------------
# STUDENTS PAGE
# --------------------------------------------------

@app.get("/students", response_class=HTMLResponse)
def students_page(
    request: Request,
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/login")

    students = db.query(Student).all()

    return templates.TemplateResponse(
        "students.html",
        {
            "request": request,
            "students": students
        }
    )


# --------------------------------------------------
# ADD STUDENT
# --------------------------------------------------

@app.post("/students/add")
def add_student(
    roll_no: str = Form(...),
    name: str = Form(...),
    email: str = Form(""),
    department: str = Form(""),
    year: str = Form(""),
    semester: str = Form(""),
    db: Session = Depends(get_db)
):

    existing = db.query(Student).filter(
        Student.roll_no == roll_no
    ).first()

    if existing:

        return RedirectResponse(
            "/students?error=Roll number already exists",
            status_code=303
        )

    student = Student(
        roll_no=roll_no,
        name=name,
        email=email,
        department=department,
        year=year,
        semester=semester
    )

    db.add(student)
    db.commit()

    return RedirectResponse(
        "/students",
        status_code=303
    )


# --------------------------------------------------
# DELETE STUDENT
# --------------------------------------------------

@app.get("/students/delete/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student:

        db.query(Mark).filter(
            Mark.student_id == student_id
        ).delete()

        db.delete(student)
        db.commit()

    return RedirectResponse(
        "/students",
        status_code=303
    )


# --------------------------------------------------
# SUBJECTS PAGE
# --------------------------------------------------

@app.get("/subjects", response_class=HTMLResponse)
def subjects_page(
    request: Request,
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/login")

    subjects = db.query(Subject).all()

    return templates.TemplateResponse(
        "subjects.html",
        {
            "request": request,
            "subjects": subjects
        }
    )


# --------------------------------------------------
# ADD SUBJECT
# --------------------------------------------------

@app.post("/subjects/add")
def add_subject(
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    credits: int = Form(...),
    semester: str = Form(...),
    db: Session = Depends(get_db)
):

    subject = Subject(
        subject_code=subject_code,
        subject_name=subject_name,
        credits=credits,
        semester=semester
    )

    db.add(subject)
    db.commit()

    return RedirectResponse(
        "/subjects",
        status_code=303
    )


# --------------------------------------------------
# MARKS PAGE
# --------------------------------------------------

@app.get("/marks", response_class=HTMLResponse)
def marks_page(
    request: Request,
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/login")

    students = db.query(Student).all()
    subjects = db.query(Subject).all()

    return templates.TemplateResponse(
        "marks.html",
        {
            "request": request,
            "students": students,
            "subjects": subjects
        }
    )


# --------------------------------------------------
# ADD MARKS
# --------------------------------------------------

@app.post("/marks/add")
def add_marks(
    student_id: int = Form(...),
    subject_id: int = Form(...),
    internal_marks: float = Form(...),
    external_marks: float = Form(...),
    db: Session = Depends(get_db)
):

    if internal_marks < 0 or internal_marks > 30:

        return RedirectResponse(
            "/marks?error=Internal marks must be between 0 and 30",
            status_code=303
        )

    if external_marks < 0 or external_marks > 70:

        return RedirectResponse(
            "/marks?error=External marks must be between 0 and 70",
            status_code=303
        )

    total = internal_marks + external_marks

    if total >= 90:
        grade = "A+"
    elif total >= 80:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 60:
        grade = "C"
    elif total >= 50:
        grade = "D"
    else:
        grade = "F"

    if total >= 40:
        result = "PASS"
    else:
        result = "FAIL"

    mark = Mark(
        student_id=student_id,
        subject_id=subject_id,
        internal_marks=internal_marks,
        external_marks=external_marks,
        total_marks=total,
        grade=grade,
        result=result
    )

    db.add(mark)
    db.commit()

    return RedirectResponse(
        "/marks",
        status_code=303
    )


# --------------------------------------------------
# RESULT PAGE
# --------------------------------------------------

@app.get(
    "/result/{student_id}",
    response_class=HTMLResponse
)
def result_page(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:

        return HTMLResponse(
            "Student not found",
            status_code=404
        )

    marks = db.query(Mark).filter(
        Mark.student_id == student_id
    ).all()

    result_data = []

    total_marks = 0

    for mark in marks:

        subject = db.query(Subject).filter(
            Subject.id == mark.subject_id
        ).first()

        if subject:

            result_data.append(
                {
                    "subject_code": subject.subject_code,
                    "subject_name": subject.subject_name,
                    "internal": mark.internal_marks,
                    "external": mark.external_marks,
                    "total": mark.total_marks,
                    "grade": mark.grade,
                    "result": mark.result
                }
            )

        total_marks += mark.total_marks

    if marks:

        percentage = (
            total_marks /
            (len(marks) * 100)
        ) * 100

    else:

        percentage = 0

    overall_result = "PASS"

    for mark in marks:

        if mark.result == "FAIL":

            overall_result = "FAIL"

            break

    if percentage >= 90:
        cgpa = 9.5
    elif percentage >= 80:
        cgpa = 8.5
    elif percentage >= 70:
        cgpa = 7.5
    elif percentage >= 60:
        cgpa = 6.5
    elif percentage >= 50:
        cgpa = 5.5
    else:
        cgpa = 4.0

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "student": student,
            "marks": result_data,
            "total_marks": total_marks,
            "percentage": round(percentage, 2),
            "cgpa": cgpa,
            "overall_result": overall_result
        }
    )
