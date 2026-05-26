import request from '@/utils/request'

const api = {
  getGroundbaitList: '/api/wiki/groundbait',
  getGroundbaitTypes: '/api/wiki/groundbait/types',
  getGroundbaitDetail: (id) => `/api/wiki/groundbait/${id}`,
}

const getGroundbaitList = async (params = {}) => {
  const res = await request.get(api.getGroundbaitList, { params })
  return res
}

const getGroundbaitTypes = async () => {
  const res = await request.get(api.getGroundbaitTypes)
  return res
}

const getGroundbaitDetail = async (id) => {
  const res = await request.get(api.getGroundbaitDetail(id))
  return res
}

export {
  getGroundbaitList,
  getGroundbaitTypes,
  getGroundbaitDetail,
}
