import request from '@/utils/request'

const api = {
  catchFromImage: '/api/recognition/catch_from_image'
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
  postCatchFromImage
}
