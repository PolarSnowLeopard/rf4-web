<template>
  <div class="container">
    <div class="header">
      <h1 class="title">鱼类图鉴</h1>
      <div class="search-bar">
        <a-input-search
          placeholder="搜索鱼种名称"
          v-model:value="searchText"
          style="width: 250px"
          @search="handleSearch"
          allow-clear
        />
        <a-select 
          placeholder="按类别筛选" 
          style="width: 150px; margin-left: 10px;"
          v-model:value="selectedClass"
          @change="handleClassFilter"
          allow-clear
        >
          <a-select-option v-for="cls in fishClasses" :key="cls" :value="cls">
            {{ cls }}
          </a-select-option>
        </a-select>
      </div>
    </div>

    <div v-if="!loading || page > 1">
      <div class="fish-count">{{ fishCount }}</div>
      
      <div class="fish-card-container">
        <a-card 
          v-for="fish in manueList" 
          :key="fish.id" 
          class="fish-card" 
          :hoverable="true"
          @click="goToDetail(fish.name)"
        >
          <template #cover>
            <div class="img-container">
              <img :src="fish.img" :alt="fish.name" class="fish-image" />
            </div>
          </template>
          <template #title>
            <div class="fish-title">{{ fish.name }}</div>
          </template>
          <template #extra>
            <a-tag :color="getClassColor(fish.fish_class)">{{ fish.fish_class }}</a-tag>
          </template>
          <div class="fish-info">
            <div class="info-row">
              <span class="info-label">稀有重量：</span>
              <span class="info-value">{{ fish.rare_weight }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">超稀有重量：</span>
              <span class="info-value">{{ fish.super_rare_weight }}</span>
            </div>
          </div>
        </a-card>
      </div>
      
      <div v-if="manueList.length === 0 && !loading" class="empty-result">
        <a-empty description="未找到符合条件的鱼类" />
      </div>
      
      <div class="pagination-container">
        <a-pagination
          v-model:current="page"
          :total="total"
          :pageSize="pageSize"
          show-quick-jumper
          @change="handlePageChange"
        />
      </div>
    </div>
    
    <div v-if="loading && page === 1" class="loading">
      <a-spin tip="加载中..." size="large">
        <div class="loading-content">正在获取鱼类数据...</div>
      </a-spin>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getFishManueList } from '@/api/wiki'

const router = useRouter()
const route = useRoute()

// 分页相关状态
const page = ref(1)
const pageSize = ref(21) // 修改为与后端一致的页面大小
const total = ref(0)
const manueList = ref([])
const loading = ref(true)
const searchText = ref('')
const selectedClass = ref(null)
const fishClasses = ref([])

// 从URL参数恢复状态
onMounted(() => {
  if (route.query.page) {
    page.value = parseInt(route.query.page) || 1
  }
  if (route.query.search) {
    searchText.value = route.query.search
  }
  if (route.query.class) {
    selectedClass.value = route.query.class
  }
  
  fetchFishManueList()
})

// 监听筛选条件变化，重置页码并重新加载
watch([searchText, selectedClass], () => {
  if (page.value !== 1) {
    page.value = 1
  } else {
    fetchFishManueList()
  }
})

// 监听页码变化，更新URL并重新加载
watch(page, (newPage) => {
  updateUrlParams()
  fetchFishManueList()
})

// 更新URL参数，不触发路由变化
const updateUrlParams = () => {
  const query = { ...route.query }
  
  // 更新查询参数
  if (page.value > 1) {
    query.page = page.value.toString()
  } else {
    delete query.page
  }
  
  if (searchText.value) {
    query.search = searchText.value
  } else {
    delete query.search
  }
  
  if (selectedClass.value) {
    query.class = selectedClass.value
  } else {
    delete query.class
  }
  
  // 替换当前URL，不触发导航
  router.replace({ query })
}

const fetchFishManueList = async () => {
  try {
    loading.value = true
    
    // 构建请求参数
    const params = {
      page: page.value,
      page_size: pageSize.value // 确保参数名与后端一致
    }
    
    // 添加搜索和筛选条件
    if (searchText.value) {
      params.search = searchText.value
    }
    
    if (selectedClass.value) {
      params.fish_class = selectedClass.value
    }
    
    const res = await getFishManueList(params)
    
    // 处理响应数据
    if (res && res.data) {
      // 处理 Django REST framework 分页格式的响应
      if (res.data.results) {
        manueList.value = res.data.results
        total.value = res.data.count || 0
        
        // 收集鱼类类别（如果未收集过）
        if (fishClasses.value.length === 0) {
          const uniqueClasses = new Set(res.data.results.map(fish => fish.fish_class))
          fishClasses.value = Array.from(uniqueClasses).filter(Boolean)
        }
      } else {
        // 兼容处理，如果直接返回数组
        manueList.value = Array.isArray(res.data) ? res.data : []
        total.value = manueList.value.length
      }
    } else {
      manueList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取鱼类图鉴失败:', error)
    manueList.value = [] // 确保即使出错也设置为空数组
  } finally {
    loading.value = false
  }
}

// 计算鱼类总数显示文本
const fishCount = computed(() => {
  if (searchText.value || selectedClass.value) {
    return `筛选结果: ${total.value} 种鱼类`
  }
  return `共 ${total.value} 种鱼类`
})

// 处理搜索
const handleSearch = () => {
  page.value = 1 // 重置为第一页
  fetchFishManueList()
  updateUrlParams()
}

// 处理类别筛选
const handleClassFilter = () => {
  page.value = 1 // 重置为第一页
  fetchFishManueList()
  updateUrlParams()
}

// 处理页码变化
const handlePageChange = (newPage) => {
  page.value = newPage
  // watch会处理剩下的逻辑
}

// 根据鱼类获取标签颜色
const getClassColor = (fishClass) => {
  const colors = {
    '淡水鱼': 'blue',
    '海水鱼': 'cyan',
    '湖泊鱼': 'green',
    '河流鱼': 'gold',
    '掠食鱼': 'orange',
    '稀有鱼': 'purple',
    '常见': 'geekblue',
    '稀有': 'purple',
    '罕见': 'magenta',
    '稀有鱼种': 'purple',
    '罕见鱼种': 'magenta'
  }
  
  return colors[fishClass] || 'default'
}

// 添加跳转详情页方法，保存当前状态
const goToDetail = (fishName) => {
  // 先更新当前URL参数，确保状态保存
  updateUrlParams()
  // 然后跳转到详情页
  router.push(`/manue/fish/${encodeURIComponent(fishName)}`)
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
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.title {
  color: #245f7b;
  margin: 0;
  font-size: 1.8rem;
}

.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.fish-count {
  color: #5a6c7d;
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.fish-card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  min-height: 400px; /* 防止内容变化时布局跳动 */
}

.fish-card {
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  cursor: pointer;
}

.fish-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.img-container {
  height: 180px;
  overflow: hidden;
  background-color: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fish-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s;
}

.fish-card:hover .fish-image {
  transform: scale(1.05);
}

.fish-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #245f7b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fish-info {
  padding: 10px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.info-label {
  color: #5a6c7d;
  font-size: 0.9rem;
}

.info-value {
  font-weight: 500;
  color: #333;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.loading-content {
  margin-top: 15px;
  color: #5a6c7d;
}

.empty-result {
  margin-top: 50px;
  text-align: center;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-bar {
    width: 100%;
  }
  
  .fish-card-container {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  
  .fish-card-container {
    grid-template-columns: 1fr;
  }
}
</style>