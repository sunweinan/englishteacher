import { defineStore } from 'pinia';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import type { CourseCard } from '@/types/course';

interface CourseState {
  courses: CourseCard[];
  loading: boolean;
  loaded: boolean;
}

export const useCoursesStore = defineStore('courses', {
  state: (): CourseState => ({
    courses: [],
    loading: false,
    loaded: false
  }),
  getters: {
    courseById: (state) => (id: number) => state.courses.find((course) => course.id === id)
  },
  actions: {
    async fetchCourses(force = false) {
      if (this.loaded && !force) return;
      this.loading = true;
      try {
        const { data } = await http.get<CourseCard[]>(API_ENDPOINTS.courses);
        this.courses = data;
        this.loaded = true;
      } finally {
        this.loading = false;
      }
    }
  }
});
