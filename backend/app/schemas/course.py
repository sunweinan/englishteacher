from pydantic import BaseModel, ConfigDict


class LessonBase(BaseModel):
  zh: str
  en: str
  phonetic: str | None = None
  audio: str | None = None

  model_config = ConfigDict(from_attributes=True)


class LessonOut(LessonBase):
  id: int


class CourseBase(BaseModel):
  title: str
  subtitle: str | None = ''
  tag: str | None = ''
  image: str | None = ''

  model_config = ConfigDict(from_attributes=True)


class CourseCreate(CourseBase):
  lessons: list[LessonBase] = []


class CourseOut(CourseBase):
  id: int
  lessons: list[LessonOut] = []
