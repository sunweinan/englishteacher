<template>
  <div class="page">
    <header class="page-head">
      <div>
        <h2>课程列表</h2>
        <p class="muted">数据来源前端课程盒子，默认从数据库加载，可新增/修改/删除并录入学习句子。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="createCourse">新增课程盒子</el-button>
    </header>

    <el-card class="add-bar" v-loading="loading">
      <el-input v-model="newCourse.title" placeholder="课程标题" class="field" />
      <el-input v-model="newCourse.subtitle" placeholder="课程副标题" class="field" />
      <el-input v-model="newCourse.tag" placeholder="标签" class="field small" />
      <el-input v-model="newCourse.image" placeholder="封面图片链接（可留空，使用上传）" class="field" />
      <el-upload
        class="upload"
        :http-request="(options) => handleNewUpload(options)"
        :show-file-list="false"
        accept="image/*"
      >
        <el-button :icon="Upload">上传封面</el-button>
      </el-upload>
      <el-button type="primary" plain :icon="Check" @click="saveNewCourse">保存</el-button>
    </el-card>

    <el-table :data="courses" row-key="id" stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="subtitle" label="副标题" min-width="220" />
      <el-table-column label="句子数" width="120">
        <template #default="{ row }">{{ row.lessons.length }}</template>
      </el-table-column>
      <el-table-column label="封面" width="120">
        <template #default="{ row }">
          <el-image :src="row.image" fit="cover" class="thumb" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link @click="openDetail(row)">查看详情</el-button>
          <el-button type="danger" link @click="confirmDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-drawer v-model="detailVisible" size="720px" :title="activeCourse?.title || '课程详情'">
      <div v-if="activeCourse" class="drawer-body">
        <el-form label-width="110px" class="form">
          <el-form-item label="标题">
            <el-input v-model="activeCourse.title" />
          </el-form-item>
          <el-form-item label="副标题">
            <el-input v-model="activeCourse.subtitle" />
          </el-form-item>
          <el-form-item label="封面链接">
            <el-input v-model="activeCourse.image" placeholder="可粘贴 CDN 或 OSS 路径" />
          </el-form-item>
          <el-form-item label="封面上传">
            <el-upload
              :show-file-list="false"
              accept="image/*"
              class="upload"
              :http-request="handleUpload"
            >
              <el-button :icon="Upload">上传本地图片</el-button>
            </el-upload>
            <el-image v-if="activeCourse.image" :src="activeCourse.image" fit="cover" class="thumb" />
          </el-form-item>
        </el-form>

        <section class="lessons">
          <header>
            <h4>学习练习句子</h4>
            <span class="muted">支持录入中文、英文、音标、发音录音</span>
          </header>
          <el-table :data="activeCourse.lessons" size="small" border style="margin-bottom: 12px">
            <el-table-column prop="zh" label="中文" min-width="140">
              <template #default="{ row }">
                <el-input v-model="row.zh" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="en" label="英文" min-width="160">
              <template #default="{ row }">
                <el-input v-model="row.en" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="phonetic" label="音标" min-width="140">
              <template #default="{ row }">
                <el-input v-model="row.phonetic" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="audio" label="发音录音 / 路径" min-width="160">
              <template #default="{ row }">
                <el-input v-model="row.audio" size="small" />
              </template>
            </el-table-column>
          </el-table>

          <div class="add-lesson">
            <el-input v-model="newLesson.zh" placeholder="中文" size="small" />
            <el-input v-model="newLesson.en" placeholder="英文" size="small" />
            <el-input v-model="newLesson.phonetic" placeholder="音标" size="small" />
            <el-input v-model="newLesson.audio" placeholder="发音录音 / 链接" size="small" />
            <el-button type="primary" size="small" :icon="Plus" @click="appendLesson">新增句子</el-button>
          </div>
        </section>

        <div class="footer">
          <el-button type="primary" :icon="Check" @click="saveActiveCourse">保存修改</el-button>
          <el-button @click="detailVisible = false">关闭</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { Check, Plus, Upload } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox, type UploadRequestOptions } from 'element-plus';
import http from '@/utils/http';
import { API_ENDPOINTS } from '@/config/api';
import { useCoursesStore } from '@/store/courses';
import type { CourseCard, Lesson } from '@/types/course';

type EditableCourse = CourseCard;

const coursesStore = useCoursesStore();
const courses = ref<EditableCourse[]>([]);
const detailVisible = ref(false);
const activeCourse = ref<EditableCourse | null>(null);
const newLesson = reactive<Lesson>({ zh: '', en: '', phonetic: '', audio: '' });
const loading = ref(false);

const newCourse = reactive<Partial<EditableCourse>>({
  title: '',
  subtitle: '',
  tag: '自定义',
  image: '',
  lessons: []
});

const syncCourses = () => {
  courses.value = coursesStore.courses.map((course) => ({
    ...course,
    lessons: course.lessons.map((lesson) => ({ ...lesson }))
  }));
};

const loadCourses = async () => {
  loading.value = true;
  try {
    await coursesStore.fetchCourses(true);
    syncCourses();
  } finally {
    loading.value = false;
  }
};

const resetNewCourse = () => {
  newCourse.title = '';
  newCourse.subtitle = '';
  newCourse.tag = '自定义';
  newCourse.image = '';
  newCourse.lessons = [];
};

const createCourse = () => {
  newCourse.title = newCourse.title || `新课程 ${courses.value.length + 1}`;
  newCourse.subtitle = newCourse.subtitle || '请填写副标题';
  ElMessage.info('请在上方补充标题/副标题/图片后点击保存');
};

const saveNewCourse = async () => {
  if (!newCourse.title || !newCourse.subtitle) {
    ElMessage.warning('请填写标题和副标题');
    return;
  }
  loading.value = true;
  try {
    await http.post(API_ENDPOINTS.adminCourses, {
      title: newCourse.title,
      subtitle: newCourse.subtitle,
      tag: newCourse.tag || '自定义',
      image: newCourse.image || '',
      lessons: (newCourse.lessons as Lesson[]) || []
    });
    ElMessage.success('新课程已加入数据库');
    resetNewCourse();
    await loadCourses();
  } finally {
    loading.value = false;
  }
};

const openDetail = (course: EditableCourse) => {
  activeCourse.value = JSON.parse(JSON.stringify(course));
  detailVisible.value = true;
};

const saveActiveCourse = async () => {
  if (!activeCourse.value) return;
  loading.value = true;
  try {
    await http.put(API_ENDPOINTS.adminCourseDetail(activeCourse.value.id), {
      title: activeCourse.value.title,
      subtitle: activeCourse.value.subtitle,
      tag: activeCourse.value.tag,
      image: activeCourse.value.image,
      lessons: activeCourse.value.lessons.map((lesson) => ({
        zh: lesson.zh,
        en: lesson.en,
        phonetic: lesson.phonetic,
        audio: lesson.audio
      }))
    });
    ElMessage.success('课程内容已保存到数据库');
    detailVisible.value = false;
    await loadCourses();
  } finally {
    loading.value = false;
  }
};

const appendLesson = () => {
  if (!activeCourse.value) return;
  if (!newLesson.zh || !newLesson.en) {
    ElMessage.warning('请填写中文和英文内容');
    return;
  }
  activeCourse.value.lessons.push({ ...newLesson });
  newLesson.zh = '';
  newLesson.en = '';
  newLesson.phonetic = '';
  newLesson.audio = '';
  ElMessage.success('句子已添加');
};

const confirmDelete = (course: EditableCourse) => {
  ElMessageBox.confirm('确定删除该课程吗？', '删除课程', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(async () => {
      loading.value = true;
      try {
        await http.delete(API_ENDPOINTS.adminCourseDetail(course.id));
        ElMessage.success('课程已删除');
        await loadCourses();
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {});
};

const handleUpload = (options: UploadRequestOptions) => {
  const reader = new FileReader();
  reader.onload = () => {
    if (activeCourse.value) {
      activeCourse.value.image = String(reader.result);
      ElMessage.success('封面上传成功');
    }
    options.onSuccess?.({}, options.file);
  };
  reader.onerror = () => {
    options.onError?.(new Error('上传失败'));
  };
  reader.readAsDataURL(options.file as File);
};

const handleNewUpload = (options: UploadRequestOptions) => {
  const reader = new FileReader();
  reader.onload = () => {
    newCourse.image = String(reader.result);
    ElMessage.success('封面上传成功');
    options.onSuccess?.({}, options.file);
  };
  reader.onerror = () => options.onError?.(new Error('上传失败'));
  reader.readAsDataURL(options.file as File);
};

onMounted(loadCourses);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.muted {
  color: #94a3b8;
  margin: 2px 0 0;
}

.add-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.field {
  width: 260px;
}

.field.small {
  width: 140px;
}

.upload {
  margin-right: 6px;
}

.thumb {
  width: 72px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e5e7eb;
}

.drawer-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lessons header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.add-lesson {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr)) 140px;
  gap: 8px;
  align-items: center;
}

.footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>
