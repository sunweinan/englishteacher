from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.course import CourseCreate, CourseOut
from app.services import course_service

router = APIRouter()


@router.get('/', response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
  return course_service.list_courses(db)


@router.get('/{course_id}', response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
  return course_service.get_course(db, course_id)


