import request from '@/utils/request'

const api = {
  getFishManueList: '/api/wiki/fish',
  getFishDetail: (name) => `/api/wiki/fish/${name}`,
  catchFromImage: '/api/wiki/catch_from_image'
}

const getFishManueList = async (params = {}) => {
  const res = await request.get(api.getFishManueList, { params })
  return res
}

const getFishDetail = async (name) => {
  const res = await request.get(api.getFishDetail(name))
  return res
}

const postCatchFromImage = async (file) => {
  const formData = new FormData()
  formData.append('image', file)
  const res = await request.post(api.catchFromImage, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
  return res
}

export {
  getFishManueList,
  getFishDetail,
  postCatchFromImage
}
