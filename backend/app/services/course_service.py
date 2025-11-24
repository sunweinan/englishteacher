from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.admin import Course, CourseLesson
from app.schemas.course import CourseCreate


def list_courses(db: Session):
  return db.query(Course).options(selectinload(Course.lessons)).order_by(Course.id.asc()).all()


def get_course(db: Session, course_id: int) -> Course:
  course = (
    db.query(Course)
    .options(selectinload(Course.lessons))
    .filter(Course.id == course_id)
    .first()
  )
  if not course:
    raise HTTPException(status_code=404, detail='Course not found')
  return course


def create_course(db: Session, payload: CourseCreate) -> Course:
  course = Course(
    title=payload.title,
    subtitle=payload.subtitle or '',
    tag=payload.tag or '',
    image=payload.image or '',
    lessons=[
      CourseLesson(
        zh=lesson.zh,
        en=lesson.en,
        phonetic=lesson.phonetic or '',
        audio=lesson.audio or ''
      )
      for lesson in payload.lessons
    ]
  )
  db.add(course)
  db.commit()
  db.refresh(course)
  return course


def update_course(db: Session, course_id: int, payload: CourseCreate) -> Course:
  course = get_course(db, course_id)
  course.title = payload.title
  course.subtitle = payload.subtitle or ''
  course.tag = payload.tag or ''
  course.image = payload.image or ''
  course.lessons = [
    CourseLesson(
      zh=lesson.zh,
      en=lesson.en,
      phonetic=lesson.phonetic or '',
      audio=lesson.audio or ''
    )
    for lesson in payload.lessons
  ]
  db.commit()
  db.refresh(course)
  return course


def delete_course(db: Session, course_id: int) -> None:
  course = get_course(db, course_id)
  db.delete(course)
  db.commit()
