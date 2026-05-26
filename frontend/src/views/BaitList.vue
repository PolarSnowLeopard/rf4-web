<template>
  <div class="container">
    <div class="header">
      <h1 class="title">鱼饵图鉴</h1>
      <div class="search-bar">
        <a-input-search
          placeholder="搜索鱼饵名称"
          v-model:value="searchText"
          style="width: 250px"
          @search="handleSearch"
          allow-clear
        />
        <a-select
          placeholder="按类型筛选"
          style="width: 180px; margin-left: 10px;"
          v-model:value="selectedType"
          @change="handleTypeFilter"
          allow-clear
        >
          <a-select-option v-for="t in baitTypes" :key="t" :value="t">
            {{ t }}
          </a-select-option>
        </a-select>
      </div>
    </div>

    <div v-if="!loading || page > 1">
      <div class="item-count">{{ itemCount }}</div>

      <div class="card-container">
        <a-card
          v-for="bait in list"
          :key="bait.id"
          class="item-card"
          :hoverable="true"
          @click="goToDetail(bait.id)"
        >
          <template #cover>
            <div class="img-container">
              <img :src="bait.img" :alt="bait.name" class="item-image" />
            </div>
          </template>
          <template #title>
            <div class="item-title">{{ bait.name }}</div>
          </template>
          <template #extra>
            <a-tag :color="getTypeColor(bait.bait_type)">{{ bait.bait_type }}</a-tag>
          </template>
          <div class="item-info">
            <div class="info-row" v-if="bait.buoyancy">
              <span class="info-label">浮力：</span>
              <span class="info-value">{{ bait.buoyancy }}</span>
            </div>
            <div class="info-row" v-if="bait.weight">
              <span class="info-label">质量：</span>
              <span class="info-value">{{ bait.weight }}</span>
            </div>
          </div>
        </a-card>
      </div>

      <div v-if="list.length === 0 && !loading" class="empty-result">
        <a-empty description="未找到符合条件的鱼饵" />
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
        <div class="loading-content">正在获取鱼饵数据...</div>
      </a-spin>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getBaitList, getBaitTypes } from '@/api/bait'

const router = useRouter()
const route = useRoute()

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const list = ref([])
const loading = ref(true)
const searchText = ref('')
const selectedType = ref(null)
const baitTypes = ref([])

const CARD_MIN_WIDTH = 200
const CARD_GAP = 20
const CONTAINER_PADDING = 50
const TARGET_ROWS = 4

const calcPageSize = () => {
  const containerWidth = window.innerWidth - CONTAINER_PADDING
  const cols = Math.floor((containerWidth + CARD_GAP) / (CARD_MIN_WIDTH + CARD_GAP))
  return Math.max(cols, 1) * TARGET_ROWS
}

let resizeTimer = null
const onResize = () => {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const newSize = calcPageSize()
    if (newSize !== pageSize.value) {
      pageSize.value = newSize
      fetchList()
    }
  }, 300)
}

onMounted(async () => {
  pageSize.value = calcPageSize()
  window.addEventListener('resize', onResize)

  if (route.query.page) {
    page.value = parseInt(route.query.page) || 1
  }
  if (route.query.search) {
    searchText.value = route.query.search
  }
  if (route.query.type) {
    selectedType.value = route.query.type
  }

  try {
    const typesRes = await getBaitTypes()
    if (typesRes && typesRes.data) {
      baitTypes.value = typesRes.data
    }
  } catch (e) {
    console.error('获取鱼饵类型失败:', e)
  }

  fetchList()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})

watch([searchText, selectedType], () => {
  if (page.value !== 1) {
    page.value = 1
  } else {
    fetchList()
  }
})

watch(page, () => {
  updateUrlParams()
  fetchList()
})

const updateUrlParams = () => {
  const query = { ...route.query }

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

  if (selectedType.value) {
    query.type = selectedType.value
  } else {
    delete query.type
  }

  router.replace({ query })
}

const fetchList = async () => {
  try {
    loading.value = true

    const params = {
      page: page.value,
      page_size: pageSize.value
    }

    if (searchText.value) {
      params.search = searchText.value
    }

    if (selectedType.value) {
      params.bait_type = selectedType.value
    }

    const res = await getBaitList(params)

    if (res && res.data) {
      if (res.data.results) {
        list.value = res.data.results
        total.value = res.data.count || 0
      } else {
        list.value = Array.isArray(res.data) ? res.data : []
        total.value = list.value.length
      }
    } else {
      list.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取鱼饵数据失败:', error)
    list.value = []
  } finally {
    loading.value = false
  }
}

const itemCount = computed(() => {
  if (searchText.value || selectedType.value) {
    return `筛选结果: ${total.value} 种鱼饵`
  }
  return `共 ${total.value} 种鱼饵`
})

const handleSearch = () => {
  page.value = 1
  fetchList()
  updateUrlParams()
}

const handleTypeFilter = () => {
  page.value = 1
  fetchList()
  updateUrlParams()
}

const handlePageChange = (newPage) => {
  page.value = newPage
}

const getTypeColor = (type) => {
  const colors = {
    '蠕虫': 'green',
    '幼虫': 'lime',
    '昆虫': 'gold',
    '坚果': 'orange',
    '谷物': 'volcano',
    '面团': 'geekblue',
    '颗粒': 'blue',
    '下沉香煮成饵': 'purple',
    'Pop-up香煮成饵': 'magenta',
    '人造玉米': 'cyan',
    '活饵鱼': 'red',
    '切饵': 'volcano',
    '海洋鱼饵': 'blue',
  }
  return colors[type] || 'default'
}

const goToDetail = (id) => {
  updateUrlParams()
  router.push(`/manue/bait/${id}`)
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

.item-count {
  color: #5a6c7d;
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.item-card {
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  cursor: pointer;
}

.item-card:hover {
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

.item-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s;
}

.item-card:hover .item-image {
  transform: scale(1.05);
}

.item-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #245f7b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-info {
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

  .card-container {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }

  .card-container {
    grid-template-columns: 1fr;
  }
}
</style>
