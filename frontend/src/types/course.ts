export interface Lesson {
  id?: number;
  zh: string;
  en: string;
  phonetic?: string;
  audio?: string;
}

export interface CourseCard {
  id: number;
  title: string;
  subtitle: string;
  image: string;
  tag: string;
  lessons: Lesson[];
}
