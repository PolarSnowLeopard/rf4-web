import request from '@/utils/request'

const api = {
  getFishManueList: '/api/wiki/fish',
  getFishDetail: (name) => `/api/wiki/fish/${name}`,
}

const getFishManueList = async (params = {}) => {
  const res = await request.get(api.getFishManueList, { params })
  return res
}

const getFishDetail = async (name) => {
  const res = await request.get(api.getFishDetail(name))
  return res
}

export {
  getFishManueList,
  getFishDetail,
}
