<template>
  <div class="page">
    <header class="page-head">
      <div>
        <h2>课程列表</h2>
        <p class="muted">数据来源前端课程盒子，默认从数据库加载，可新增/修改/删除并录入学习句子。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="createCourse">新增课程盒子</el-button>
    </header>

    <el-card class="add-bar">
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

    <el-table :data="courses" row-key="id" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="subtitle" label="副标题" min-width="220" />
      <el-table-column prop="createdAt" label="添加时间" min-width="140">
        <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
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
import { reactive, ref } from 'vue';
import { Check, Plus, Upload } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox, type UploadRequestOptions } from 'element-plus';
import { courseCards, type CourseCard, type Lesson } from '@/config/courses';

interface EditableCourse extends CourseCard {
  createdAt: string;
}

const adminPassword = 'admin123';

const toEditable = (items: CourseCard[]): EditableCourse[] =>
  items.map((item, index) => ({
    ...item,
    createdAt: new Date(Date.now() - index * 36_00_000).toISOString()
  }));

const courses = ref<EditableCourse[]>(toEditable(courseCards));
const detailVisible = ref(false);
const activeCourse = ref<EditableCourse | null>(null);
const newLesson = reactive<Lesson>({ zh: '', en: '', phonetic: '', audio: '' });

const newCourse = reactive<Partial<EditableCourse>>({
  title: '',
  subtitle: '',
  tag: '自定义',
  image: '',
  lessons: [],
  createdAt: new Date().toISOString()
});

const formatDate = (val: string) => new Date(val).toLocaleString();

const createCourse = () => {
  newCourse.title = `新课程 ${courses.value.length + 1}`;
  newCourse.subtitle = '请填写副标题';
  newCourse.lessons = [];
  newCourse.image = '';
  newCourse.createdAt = new Date().toISOString();
  ElMessage.info('请在上方补充标题/副标题/图片后点击保存');
};

const saveNewCourse = () => {
  if (!newCourse.title || !newCourse.subtitle) {
    ElMessage.warning('请填写标题和副标题');
    return;
  }
  const maxId = courses.value.reduce((acc, cur) => Math.max(acc, cur.id), 0);
  const payload: EditableCourse = {
    id: maxId + 1,
    title: newCourse.title,
    subtitle: newCourse.subtitle,
    tag: newCourse.tag || '自定义',
    image:
      newCourse.image ||
      'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
    lessons: (newCourse.lessons as Lesson[]) || [],
    createdAt: newCourse.createdAt || new Date().toISOString()
  };
  courses.value.unshift(payload);
  ElMessage.success('新课程已加入列表（待同步数据库）');
  newCourse.title = '';
  newCourse.subtitle = '';
  newCourse.image = '';
};

const openDetail = (course: EditableCourse) => {
  activeCourse.value = JSON.parse(JSON.stringify(course));
  detailVisible.value = true;
};

const saveActiveCourse = () => {
  if (!activeCourse.value) return;
  const index = courses.value.findIndex((c) => c.id === activeCourse.value?.id);
  if (index !== -1) {
    courses.value[index] = JSON.parse(JSON.stringify(activeCourse.value));
    ElMessage.success('课程内容已保存，等待同步到数据库');
  }
  detailVisible.value = false;
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
  ElMessageBox.prompt('请输入当前登录密码以确认删除该课程', '删除课程', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    inputType: 'password',
    inputPlaceholder: '后台登录密码',
    inputValidator: (value) => value === adminPassword || '密码错误，无法删除'
  })
    .then(() => {
      courses.value = courses.value.filter((item) => item.id !== course.id);
      ElMessage.success('课程已删除');
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
  reader.readAsDataURL(options.file);
};

const handleNewUpload = (options: UploadRequestOptions) => {
  const reader = new FileReader();
  reader.onload = () => {
    newCourse.image = String(reader.result || '');
    ElMessage.success('已更新新课程封面');
    options.onSuccess?.({}, options.file);
  };
  reader.onerror = () => options.onError?.(new Error('上传失败'));
  reader.readAsDataURL(options.file);
};
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
