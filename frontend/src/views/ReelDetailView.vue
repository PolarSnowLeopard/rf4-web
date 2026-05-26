<template>
  <div class="detail-container" v-if="detail">
    <div class="detail-header">
      <a-button @click="goBack" class="back-btn"><template #icon><arrow-left-outlined /></template>返回列表</a-button>
      <h1 class="detail-title">{{ detail.name }}</h1>
      <a-tag :color="getTypeColor(detail.reel_type)" class="type-tag">{{ detail.reel_type }}</a-tag>
    </div>
    <div class="detail-content">
      <div class="detail-left">
        <div class="image-wrapper"><img :src="detail.img" :alt="detail.name" class="detail-image" /></div>
      </div>
      <div class="detail-right">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="名称">{{ detail.name }}</a-descriptions-item>
          <a-descriptions-item label="类型" v-if="detail.reel_type">{{ detail.reel_type }}</a-descriptions-item>
          <a-descriptions-item label="形式" v-if="detail.form">{{ detail.form }}</a-descriptions-item>
          <a-descriptions-item label="大小" v-if="detail.size">{{ detail.size }}</a-descriptions-item>
          <a-descriptions-item label="防海水" v-if="detail.saltwater && detail.saltwater !== '-'">{{ detail.saltwater }}</a-descriptions-item>
          <a-descriptions-item label="传动比" v-if="detail.gear_ratio">{{ detail.gear_ratio }}</a-descriptions-item>
          <a-descriptions-item label="摩擦制动力" v-if="detail.friction_brake">{{ detail.friction_brake }}</a-descriptions-item>
          <a-descriptions-item label="回线速度" v-if="detail.line_retrieve_speed">{{ detail.line_retrieve_speed }}</a-descriptions-item>
          <a-descriptions-item label="锁轮拉力" v-if="detail.max_drag">{{ detail.max_drag }}</a-descriptions-item>
          <a-descriptions-item label="测试/适配重" v-if="detail.cast_weight">{{ detail.cast_weight }}</a-descriptions-item>
          <a-descriptions-item label="线轴容量" v-if="detail.line_capacity">{{ detail.line_capacity }}</a-descriptions-item>
          <a-descriptions-item label="等级要求" v-if="detail.level_req">{{ detail.level_req }}</a-descriptions-item>
          <a-descriptions-item label="银币" v-if="detail.price_silver">{{ detail.price_silver }}</a-descriptions-item>
          <a-descriptions-item label="金币" v-if="detail.price_gold">{{ detail.price_gold }}</a-descriptions-item>
          <a-descriptions-item label="评级" v-if="detail.rating">{{ detail.rating }}</a-descriptions-item>
        </a-descriptions>
        <div class="description-section" v-if="detail.description">
          <h3>描述</h3>
          <p class="description-text">{{ detail.description }}</p>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="loading"><a-spin tip="加载中..." size="large" /></div>
  <div v-else class="not-found"><a-result status="404" title="未找到该渔轮" sub-title="请检查链接是否正确"><template #extra><a-button type="primary" @click="goBack">返回列表</a-button></template></a-result></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'
import { getReelDetail } from '@/api/reel'

const router = useRouter()
const route = useRoute()
const detail = ref(null)
const loading = ref(true)

onMounted(async () => {
  try { const res = await getReelDetail(route.params.id); if (res && res.data) detail.value = res.data }
  catch (error) { console.error('获取渔轮详情失败:', error) }
  finally { loading.value = false }
})

const goBack = () => { router.push('/manue/reel') }
const getTypeColor = (type) => {
  const colors = { '水滴轮': 'blue', '动力鼓轮': 'red', '纺车式': 'green', '鼓轮': 'orange', '新年系列 纺车式': 'purple', '新年系列 鼓轮': 'gold', '新年系列 动力鼓轮': 'magenta' }
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
