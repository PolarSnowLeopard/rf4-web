<template>
  <div class="fish-detail-container">
    <div class="detail-header">
      <a-button class="back-button" @click="goBack">
        <ArrowLeftOutlined /> 返回列表
      </a-button>
      
      <h1 class="fish-name">{{ loading ? '加载中...' : fishDetail.name }}</h1>
    </div>
    
    <a-spin :spinning="loading" tip="正在加载鱼类详情...">
      <div v-if="fishDetail" class="detail-content">
        <div class="detail-card">
          <div class="fish-image-container">
            <img :src="fishDetail.img" :alt="fishDetail.name" class="fish-image" />
          </div>

          <div class="fish-info-container">
            <div class="fish-basic-info">
              <div class="info-item" v-if="fishDetail.name_en">
                <span class="info-label">英文名：</span>
                <span class="info-value">{{ fishDetail.name_en }}</span>
              </div>

              <div class="info-item">
                <span class="info-label">稀有度：</span>
                <a-tag :color="getClassColor(fishDetail.fish_class)">{{ fishDetail.fish_class || '未知' }}</a-tag>
              </div>

              <div class="info-item" v-if="fishDetail.rare_weight">
                <span class="info-label">上星重量：</span>
                <span class="info-value rare-weight">{{ fishDetail.rare_weight }}</span>
              </div>

              <div class="info-item" v-if="fishDetail.super_rare_weight">
                <span class="info-label">蓝冠重量：</span>
                <span class="info-value super-rare-weight">{{ fishDetail.super_rare_weight }}</span>
              </div>

              <div class="info-item" v-if="fishDetail.fishing_method">
                <span class="info-label">钓法：</span>
                <span class="info-value">{{ fishDetail.fishing_method }}</span>
              </div>

              <div class="info-item" v-if="fishDetail.habitats && fishDetail.habitats.length">
                <span class="info-label">栖息水域：</span>
                <span class="info-value">
                  <a-tag v-for="h in fishDetail.habitats" :key="h" color="blue">{{ h }}</a-tag>
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="fish-description-card">
          <h2 class="section-title">鱼类描述</h2>
          <div class="description-content">
            <p>{{ fishDetail.description }}</p>
          </div>
        </div>

        <div class="fish-baits-card" v-if="fishDetail.baits && fishDetail.baits.length">
          <h2 class="section-title">推荐饵料</h2>
          <div class="baits-list">
            <a-tag v-for="bait in fishDetail.baits" :key="bait" color="green" class="bait-tag">{{ bait }}</a-tag>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="error-message">
        <a-result status="error" :title="error" sub-title="请返回列表重试或联系管理员">
          <template #extra>
            <a-button type="primary" @click="goBack">返回列表</a-button>
          </template>
        </a-result>
      </div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFishDetail } from '@/api/wiki'
import { ArrowLeftOutlined } from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const fishDetail = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  await fetchFishDetail()
})

const fetchFishDetail = async () => {
  const fishName = route.params.name
  
  if (!fishName) {
    error.value = '鱼类名称未指定'
    loading.value = false
    return
  }
  
  try {
    loading.value = true
    error.value = null
    
    const res = await getFishDetail(fishName)
    
    if (res && res.data) {
      fishDetail.value = res.data
    } else if (res) {
      fishDetail.value = res
    } else {
      error.value = '获取鱼类详情失败'
    }
  } catch (err) {
    console.error('获取鱼类详情出错:', err)
    error.value = '获取鱼类详情时发生错误'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/manue/fish')
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getClassColor = (fishClass) => {
  const colors = {
    '常见': 'geekblue',
    '稀有': 'purple',
    '罕见': 'magenta',
    '稀有鱼种': 'purple',
    '罕见鱼种': 'magenta',
    '传说': 'gold',
    '独特': 'red',
  }
  return colors[fishClass] || 'default'
}
</script>

<style scoped>
.fish-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 25px;
  background-color: #f7fafc;
  min-height: 100vh;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.back-button {
  margin-right: 20px;
}

.fish-name {
  margin: 0;
  color: #245f7b;
  font-size: 2rem;
  flex-grow: 1;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.detail-card {
  display: flex;
  flex-direction: row;
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.fish-image-container {
  flex: 0 0 300px;
  background-color: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.fish-image {
  width: 100%;
  height: 300px;
  object-fit: contain;
}

.fish-info-container {
  flex-grow: 1;
  padding: 25px;
  display: flex;
  flex-direction: column;
}

.fish-basic-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  width: 100px;
  color: #5a6c7d;
  font-size: 1rem;
}

.info-value {
  font-size: 1.1rem;
  color: #2c4152;
  font-weight: 500;
}

.rare-weight, .super-rare-weight {
  color: #1890ff;
  font-weight: 600;
}

.super-rare-weight {
  color: #722ed1;
}

.last-update {
  margin-top: 20px;
  font-size: 0.9rem;
  color: #8c8c8c;
}

.fish-description-card, .fish-baits-card {
  background-color: #fff;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.baits-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.bait-tag {
  font-size: 0.9rem;
  padding: 4px 10px;
}

.section-title {
  color: #245f7b;
  font-size: 1.3rem;
  border-bottom: 1px solid #eef2f6;
  padding-bottom: 10px;
  margin-top: 0;
  margin-bottom: 15px;
}

.description-content {
  color: #4a4a4a;
  line-height: 1.7;
  white-space: pre-line;
}


.error-message {
  margin-top: 30px;
}

@media (max-width: 768px) {
  .detail-card {
    flex-direction: column;
  }
  
  .fish-image-container {
    flex: none;
    height: 250px;
  }
  
  .fish-image {
    height: 100%;
  }
  
  .fish-info-container {
    padding: 20px;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .back-button {
    margin-right: 0;
  }
}

@media (max-width: 480px) {
  .fish-detail-container {
    padding: 15px;
  }
  
  .fish-name {
    font-size: 1.6rem;
  }
  
  .info-label {
    width: 90px;
  }
}
</style> 