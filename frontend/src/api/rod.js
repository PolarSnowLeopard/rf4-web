import request from '@/utils/request'

const api = {
  getRodList: '/api/wiki/rod',
  getRodTypes: '/api/wiki/rod/types',
  getRodDetail: (id) => `/api/wiki/rod/${id}`,
}

const getRodList = async (params = {}) => {
  const res = await request.get(api.getRodList, { params })
  return res
}

const getRodTypes = async () => {
  const res = await request.get(api.getRodTypes)
  return res
}

const getRodDetail = async (id) => {
  const res = await request.get(api.getRodDetail(id))
  return res
}

export {
  getRodList,
  getRodTypes,
  getRodDetail,
}
