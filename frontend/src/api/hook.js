import request from '@/utils/request'

const api = {
  getHookList: '/api/wiki/hook',
  getHookTypes: '/api/wiki/hook/types',
  getHookDetail: (id) => `/api/wiki/hook/${id}`,
}

const getHookList = async (params = {}) => {
  const res = await request.get(api.getHookList, { params })
  return res
}

const getHookTypes = async () => {
  const res = await request.get(api.getHookTypes)
  return res
}

const getHookDetail = async (id) => {
  const res = await request.get(api.getHookDetail(id))
  return res
}

export {
  getHookList,
  getHookTypes,
  getHookDetail,
}
