import request from '@/utils/request'

const api = {
  getRigList: '/api/wiki/rig',
  getRigTypes: '/api/wiki/rig/types',
  getRigDetail: (id) => `/api/wiki/rig/${id}`,
}

const getRigList = async (params = {}) => {
  const res = await request.get(api.getRigList, { params })
  return res
}

const getRigTypes = async () => {
  const res = await request.get(api.getRigTypes)
  return res
}

const getRigDetail = async (id) => {
  const res = await request.get(api.getRigDetail(id))
  return res
}

export {
  getRigList,
  getRigTypes,
  getRigDetail,
}
