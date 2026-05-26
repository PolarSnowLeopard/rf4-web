import request from '@/utils/request'

const api = {
  getLureList: '/api/wiki/lure',
  getLureTypes: '/api/wiki/lure/types',
  getLureDetail: (id) => `/api/wiki/lure/${id}`,
}

const getLureList = async (params = {}) => {
  const res = await request.get(api.getLureList, { params })
  return res
}

const getLureTypes = async () => {
  const res = await request.get(api.getLureTypes)
  return res
}

const getLureDetail = async (id) => {
  const res = await request.get(api.getLureDetail(id))
  return res
}

export {
  getLureList,
  getLureTypes,
  getLureDetail,
}
