<template>
  <div class="detail-container" v-if="detail">
    <div class="detail-header">
      <a-button @click="goBack" class="back-btn">
        <template #icon><arrow-left-outlined /></template>
        返回列表
      </a-button>
      <h1 class="detail-title">{{ detail.name }}</h1>
      <a-tag :color="getTypeColor(detail.lure_type)" class="type-tag">{{ detail.lure_type }}</a-tag>
    </div>

    <div class="detail-content">
      <div class="detail-left">
        <div class="image-wrapper">
          <img :src="detail.img" :alt="detail.name" class="detail-image" />
        </div>
      </div>

      <div class="detail-right">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="名称">{{ detail.name }}</a-descriptions-item>
          <a-descriptions-item label="形式" v-if="detail.lure_type">{{ detail.lure_type }}</a-descriptions-item>
          <a-descriptions-item label="长度" v-if="detail.length">{{ detail.length }}</a-descriptions-item>
          <a-descriptions-item label="大小" v-if="detail.size">{{ detail.size }}</a-descriptions-item>
          <a-descriptions-item label="质量" v-if="detail.weight">{{ detail.weight }}</a-descriptions-item>
          <a-descriptions-item label="鱼钩尺寸" v-if="detail.hook_size">{{ detail.hook_size }}</a-descriptions-item>
          <a-descriptions-item label="解锁技能" v-if="detail.unlock_skill">{{ detail.unlock_skill }}</a-descriptions-item>
          <a-descriptions-item label="钓钩组件" v-if="detail.hook_component">{{ detail.hook_component }}</a-descriptions-item>
        </a-descriptions>

        <div class="description-section" v-if="detail.description">
          <h3>描述</h3>
          <p class="description-text">{{ detail.description }}</p>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="loading">
    <a-spin tip="加载中..." size="large" />
  </div>

  <div v-else class="not-found">
    <a-result status="404" title="未找到该拟饵" sub-title="请检查链接是否正确">
      <template #extra>
        <a-button type="primary" @click="goBack">返回列表</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import { getLureDetail } from '@/api/lure'

const router = useRouter()
const route = useRoute()

const detail = ref(null)
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id
  try {
    const res = await getLureDetail(id)
    if (res && res.data) detail.value = res.data
  } catch (error) {
    console.error('获取拟饵详情失败:', error)
  } finally {
    loading.value = false
  }
})

const goBack = () => { router.push('/manue/lure') }

const getTypeColor = (type) => {
  const colors = {
    '勺子路亚': 'blue', '旋转亮片': 'cyan', '摇滚小胖子': 'green',
    '米诺': 'gold', '铅头钩': 'orange', '复合路亚': 'purple',
    '软饵': 'magenta', '飞蝇': 'lime', '抽停硬饵': 'geekblue',
    '波扒': 'volcano', 'Walker': 'red',
  }
  return colors[type] || 'default'
}
</script>

<style scoped>
.detail-container { padding: 25px; background-color: #f7fafc; min-height: 85vh; }
.detail-header { display: flex; align-items: center; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
.back-btn { margin-right: 10px; }
.detail-title { color: #245f7b; margin: 0; font-size: 1.8rem; }
.type-tag { font-size: 0.9rem; padding: 4px 12px; }
.detail-content { display: flex; gap: 30px; flex-wrap: wrap; }
.detail-left { flex: 0 0 300px; }
.image-wrapper { background: #f0f7ff; border-radius: 12px; padding: 20px; display: flex; align-items: center; justify-content: center; }
.detail-image { max-width: 100%; max-height: 280px; object-fit: contain; }
.detail-right { flex: 1; min-width: 300px; }
.description-section { margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; }
.description-section h3 { color: #245f7b; margin-bottom: 10px; }
.description-text { color: #4a5568; line-height: 1.8; }
.loading { display: flex; justify-content: center; align-items: center; min-height: 400px; }
.not-found { padding: 50px; }
@media (max-width: 768px) { .detail-left { flex: 0 0 100%; } .detail-content { flex-direction: column; } }
</style>
