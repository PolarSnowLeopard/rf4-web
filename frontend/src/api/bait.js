import request from '@/utils/request'

const api = {
  getBaitList: '/api/wiki/bait',
  getBaitTypes: '/api/wiki/bait/types',
  getBaitDetail: (id) => `/api/wiki/bait/${id}`,
}

const getBaitList = async (params = {}) => {
  const res = await request.get(api.getBaitList, { params })
  return res
}

const getBaitTypes = async () => {
  const res = await request.get(api.getBaitTypes)
  return res
}

const getBaitDetail = async (id) => {
  const res = await request.get(api.getBaitDetail(id))
  return res
}

export {
  getBaitList,
  getBaitTypes,
  getBaitDetail,
}
