import request from '@/utils/request'

const api = {
  chat: '/api/agent/chat',
  chatStream: '/api/agent/chat/stream',
}

const postAgentChat = async (messages, llmConfig = {}) => {
  const res = await request.post(api.chat, { messages, llm_config: llmConfig })
  return res
}

const getStreamUrl = () => {
  const baseURL = request.defaults.baseURL || ''
  return baseURL + api.chatStream
}

export { postAgentChat, getStreamUrl, api }
