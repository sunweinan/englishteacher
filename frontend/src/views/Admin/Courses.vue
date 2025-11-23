<template>
  <div>
    <h2>课程列表编辑</h2>
    <p class="tip">首页每个课程框的图片、标题、副标题以及对应的学习内容都可以在此维护。</p>
    <el-collapse accordion>
      <el-collapse-item v-for="course in courses" :key="course.id" :name="course.id">
        <template #title>
          <div class="title-row">
            <img :src="course.image" alt="thumb" />
            <div>
              <div class="name">{{ course.title }}</div>
              <div class="sub">{{ course.subtitle }}</div>
            </div>
          </div>
        </template>
        <div class="editor">
          <el-form label-width="110px">
            <el-form-item label="标题">
              <el-input v-model="course.title" />
            </el-form-item>
            <el-form-item label="副标题">
              <el-input v-model="course.subtitle" />
            </el-form-item>
            <el-form-item label="封面图片">
              <el-input v-model="course.image" />
            </el-form-item>
          </el-form>
          <h4>学习内容</h4>
          <el-table :data="course.lessons" size="small">
            <el-table-column prop="zh" label="中文句子" />
            <el-table-column prop="en" label="英文答案" />
            <el-table-column prop="phonetic" label="音标" />
            <el-table-column prop="audio" label="英文语音" />
          </el-table>
          <el-button type="primary" style="margin-top: 10px">保存修改</el-button>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { courseCards as courses } from '@/config/courses';
</script>

<style scoped>
.tip {
  color: #94a3b8;
  margin-bottom: 8px;
}

.title-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.title-row img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 12px;
}

.name {
  font-weight: 700;
}

.sub {
  color: #94a3b8;
}

.editor {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
}
</style>
