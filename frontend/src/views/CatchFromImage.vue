<template>
  <div class="container">
    <div class="header">
      <h1 class="title">渔获识别</h1>
      <a-upload
        :before-upload="beforeUpload"
        :show-upload-list="false"
        accept="image/png,image/jpeg,image/jpg,image/bmp"
      >
        <a-button type="primary" :loading="loading">
          <upload-outlined />
          上传游戏截图
        </a-button>
      </a-upload>
    </div>

    <a-row :gutter="16" class="content">
      <a-col :xs="24" :md="12">
        <a-card title="截图" class="image-card">
          <div class="image-wrapper">
            <a-spin :spinning="loading" tip="正在识别...">
              <img
                v-if="displayImage"
                :src="displayImage"
                alt="catch screenshot"
                class="screenshot"
              />
              <a-empty v-else description="请上传游戏截图（识别完成后此处显示标注结果）" />
            </a-spin>
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :md="12">
        <a-card title="渔获分析结果" class="result-card">
          <a-table
            :columns="columns"
            :data-source="tableData"
            :pagination="false"
            :locale="{ emptyText: '尚无识别结果' }"
            row-key="key"
            size="middle"
            bordered
          />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { postCatchFromImage } from '@/api/recognition'

const loading = ref(false)
const displayImage = ref('')
const tableData = ref([])

const columns = [
  { title: '新鲜度', dataIndex: 'freshness', key: 'freshness', width: 140 },
  { title: '鱼类名称', dataIndex: 'name', key: 'name' },
  { title: '重量', dataIndex: 'weight', key: 'weight', width: 140 },
  { title: '售价', dataIndex: 'price', key: 'price', width: 120 }
]

const localPreview = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })

const beforeUpload = async (file) => {
  try {
    loading.value = true
    tableData.value = []
    displayImage.value = await localPreview(file)

    const res = await postCatchFromImage(file)
    const data = res?.data ?? {}

    if (data.image) {
      displayImage.value = `data:image/png;base64,${data.image}`
    }

    if (Array.isArray(data.fishes)) {
      tableData.value = data.fishes.map((row, idx) => ({
        key: idx,
        freshness: row?.[0] ?? '',
        name: row?.[1] ?? '',
        weight: row?.[2] ?? '',
        price: row?.[3] ?? ''
      }))
    }

    message.success(`识别完成，共 ${tableData.value.length} 条`)
  } catch (err) {
    console.error('识别失败:', err)
    message.error('识别失败，请稍后重试')
  } finally {
    loading.value = false
  }
  return false
}
</script>

<style scoped>
.container {
  padding: 25px;
  background-color: #f7fafc;
  min-height: 85vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.title {
  color: #245f7b;
  margin: 0;
  font-size: 1.8rem;
}

.content {
  margin-top: 8px;
}

.image-card,
.result-card {
  height: 100%;
}

.image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360px;
  background-color: #f0f7ff;
  border-radius: 6px;
  overflow: hidden;
}

.screenshot {
  max-width: 100%;
  max-height: 540px;
  object-fit: contain;
}
</style>
