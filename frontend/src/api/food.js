import request from '@/utils/request'

const api = {
  getFoodList: '/api/wiki/food',
  getFoodTypes: '/api/wiki/food/types',
  getFoodDetail: (id) => `/api/wiki/food/${id}`,
}

const getFoodList = async (params = {}) => {
  const res = await request.get(api.getFoodList, { params })
  return res
}

const getFoodTypes = async () => {
  const res = await request.get(api.getFoodTypes)
  return res
}

const getFoodDetail = async (id) => {
  const res = await request.get(api.getFoodDetail(id))
  return res
}

export { getFoodList, getFoodTypes, getFoodDetail }
