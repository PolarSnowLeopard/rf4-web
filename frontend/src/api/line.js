import request from '@/utils/request'

const api = {
  getLineList: '/api/wiki/line',
  getLineTypes: '/api/wiki/line/types',
  getLineDetail: (id) => `/api/wiki/line/${id}`,
}

const getLineList = async (params = {}) => {
  const res = await request.get(api.getLineList, { params })
  return res
}

const getLineTypes = async () => {
  const res = await request.get(api.getLineTypes)
  return res
}

const getLineDetail = async (id) => {
  const res = await request.get(api.getLineDetail(id))
  return res
}

export {
  getLineList,
  getLineTypes,
  getLineDetail,
}
