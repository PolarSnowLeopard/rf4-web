import request from '@/utils/request'

const api = {
  getAccessoryList: '/api/wiki/accessory',
  getAccessoryTypes: '/api/wiki/accessory/types',
  getAccessoryDetail: (id) => `/api/wiki/accessory/${id}`,
}

const getAccessoryList = async (params = {}) => {
  const res = await request.get(api.getAccessoryList, { params })
  return res
}

const getAccessoryTypes = async () => {
  const res = await request.get(api.getAccessoryTypes)
  return res
}

const getAccessoryDetail = async (id) => {
  const res = await request.get(api.getAccessoryDetail(id))
  return res
}

export { getAccessoryList, getAccessoryTypes, getAccessoryDetail }
