import request from '@/utils/request'

const api = {
  getReelList: '/api/wiki/reel',
  getReelTypes: '/api/wiki/reel/types',
  getReelDetail: (id) => `/api/wiki/reel/${id}`,
}

const getReelList = async (params = {}) => {
  const res = await request.get(api.getReelList, { params })
  return res
}

const getReelTypes = async () => {
  const res = await request.get(api.getReelTypes)
  return res
}

const getReelDetail = async (id) => {
  const res = await request.get(api.getReelDetail(id))
  return res
}

export {
  getReelList,
  getReelTypes,
  getReelDetail,
}
