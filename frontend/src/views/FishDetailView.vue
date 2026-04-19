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
              <div class="info-item">
                <span class="info-label">类别：</span>
                <a-tag :color="getClassColor(fishDetail.fish_class)">{{ fishDetail.fish_class }}</a-tag>
              </div>
              
              <div class="info-item">
                <span class="info-label">稀有重量：</span>
                <span class="info-value rare-weight">{{ fishDetail.rare_weight }}</span>
              </div>
              
              <div class="info-item">
                <span class="info-label">超稀有重量：</span>
                <span class="info-value super-rare-weight">{{ fishDetail.super_rare_weight }}</span>
              </div>
              
              <div class="info-item last-update">
                <span class="info-label">更新时间：</span>
                <span class="info-value">{{ formatDate(fishDetail.updated_at) }}</span>
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
        
        <div class="related-info-card">
          <h2 class="section-title">相关信息</h2>
          <div class="info-message">
            <InfoCircleOutlined /> 更多相关信息正在开发中，敬请期待！
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
import { ArrowLeftOutlined, InfoCircleOutlined } from '@ant-design/icons-vue'

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
    '淡水鱼': 'blue',
    '海水鱼': 'cyan',
    '湖泊鱼': 'green',
    '河流鱼': 'gold',
    '掠食鱼': 'orange',
    '稀有鱼': 'purple',
    '常见': 'geekblue'
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

.fish-description-card, .related-info-card {
  background-color: #fff;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
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

.info-message {
  color: #5a6c7d;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background-color: #f0f7ff;
  border-radius: 5px;
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