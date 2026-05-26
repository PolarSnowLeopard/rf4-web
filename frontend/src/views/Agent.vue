<template>
  <div class="agent-container">
    <div class="chat-panel">
      <div class="chat-header">
        <h2>钓鱼助手</h2>
        <a-button type="text" @click="showSettings = true"><setting-outlined /> 设置</a-button>
      </div>

      <div class="chat-messages" ref="messagesRef">
        <div v-if="chatMessages.length === 0" class="welcome">
          <div class="welcome-icon">🎣</div>
          <h3>你好，我是俄钓4钓鱼助手</h3>
          <p>我可以帮你查询装备图鉴、推荐钓组搭配、对比不同装备。试试问我：</p>
          <div class="suggestions">
            <a-tag v-for="s in suggestions" :key="s" class="suggestion-tag" @click="sendSuggestion(s)">{{ s }}</a-tag>
          </div>
        </div>

        <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['message', msg.role]">
          <div class="message-bubble">
            <div v-if="msg.role === 'assistant'" class="message-content" v-html="renderMarkdown(msg.content)"></div>
            <div v-else class="message-content">{{ msg.content }}</div>
            <div v-if="msg.toolCalls && msg.toolCalls.length" class="tool-calls">
              <a-collapse size="small" ghost>
                <a-collapse-panel header="查询过程" :key="idx">
                  <div v-for="(tc, ti) in msg.toolCalls" :key="ti" class="tool-call-item">
                    <div class="tool-name">{{ formatToolCall(tc) }}</div>
                    <div v-if="tc.result" class="tool-result">{{ formatToolResult(tc.result) }}</div>
                  </div>
                </a-collapse-panel>
              </a-collapse>
            </div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-bubble">
            <div v-if="currentToolCalls.length" class="thinking">
              <a-spin size="small" /> 正在查询: {{ currentToolCalls[currentToolCalls.length - 1].name }}...
            </div>
            <div v-else class="thinking">
              <a-spin size="small" /> {{ streamContent ? '' : '思考中...' }}
            </div>
            <div v-if="streamContent" class="message-content" v-html="renderMarkdown(streamContent)"></div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <a-textarea v-model:value="inputText" :auto-size="{ minRows: 1, maxRows: 4 }" placeholder="输入你的问题..." @pressEnter="handleEnter" :disabled="loading" />
        <a-button type="primary" :loading="loading" @click="sendMessage" :disabled="!inputText.trim()">
          <template #icon><send-outlined /></template>
        </a-button>
      </div>
    </div>

    <a-modal v-model:open="showSettings" title="LLM 设置" @ok="saveSettings" width="500px">
      <a-form layout="vertical">
        <a-form-item label="API Key">
          <a-input-password v-model:value="settingsForm.apiKey" placeholder="留空使用默认" />
        </a-form-item>
        <a-form-item label="Base URL">
          <a-input v-model:value="settingsForm.baseUrl" placeholder="留空使用默认 (OpenRouter)" />
        </a-form-item>
        <a-form-item label="模型">
          <a-input v-model:value="settingsForm.model" placeholder="留空使用默认 (gemini-3.5-flash)" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="resetSettings">重置为默认</a-button>
        <a-button type="primary" @click="saveSettings">保存</a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { SettingOutlined, SendOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { marked } from 'marked'
import { getStreamUrl } from '@/api/agent'

const messagesRef = ref(null)
const inputText = ref('')
const loading = ref(false)
const showSettings = ref(false)
const chatMessages = ref([])
const streamContent = ref('')
const currentToolCalls = ref([])

const suggestions = [
  '推荐一套钓鲤鱼的装备',
  '有哪些浮钓竿？',
  '活饵有哪些选择？',
  '帮我对比不同类型的渔轮',
]

const settingsForm = ref({
  apiKey: '',
  baseUrl: '',
  model: '',
})

onMounted(() => {
  const saved = localStorage.getItem('agent_llm_config')
  if (saved) {
    try { Object.assign(settingsForm.value, JSON.parse(saved)) } catch (e) { /* ignore */ }
  }
})

const saveSettings = () => {
  localStorage.setItem('agent_llm_config', JSON.stringify(settingsForm.value))
  showSettings.value = false
  message.success('设置已保存')
}

const resetSettings = () => {
  settingsForm.value = { apiKey: '', baseUrl: '', model: '' }
  localStorage.removeItem('agent_llm_config')
  message.success('已重置为默认设置')
}

const getLlmConfig = () => {
  const config = {}
  if (settingsForm.value.apiKey) config.api_key = settingsForm.value.apiKey
  if (settingsForm.value.baseUrl) config.base_url = settingsForm.value.baseUrl
  if (settingsForm.value.model) config.model = settingsForm.value.model
  return config
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text, { breaks: true })
}

const formatToolCall = (tc) => {
  if (tc.name === 'search_wiki') {
    const cat = tc.arguments?.category || ''
    const q = tc.arguments?.query || ''
    return `搜索${cat}${q ? ': ' + q : ''}`
  }
  if (tc.name === 'get_detail') {
    return `查看${tc.arguments?.category || ''}详情 #${tc.arguments?.id || ''}`
  }
  return tc.name
}

const formatToolResult = (result) => {
  if (result.error) return `错误: ${result.error}`
  if (result.count !== undefined) return `找到 ${result.count} 条结果`
  if (result.name) return result.name
  return JSON.stringify(result).slice(0, 100)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const handleEnter = (e) => {
  if (e.shiftKey) return
  e.preventDefault()
  sendMessage()
}

const sendSuggestion = (text) => {
  inputText.value = text
  sendMessage()
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  chatMessages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  streamContent.value = ''
  currentToolCalls.value = []
  scrollToBottom()

  const messages = chatMessages.value.map(m => ({ role: m.role, content: m.content }))
  const llmConfig = getLlmConfig()

  try {
    const baseURL = 'http://fdueblab.cn:9999'
    const url = baseURL + '/api/agent/chat/stream'

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, llm_config: llmConfig }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let toolCallsForMessage = []

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const jsonStr = line.slice(6)
        let event
        try { event = JSON.parse(jsonStr) } catch (e) { continue }

        if (event.type === 'content') {
          streamContent.value += event.content
          scrollToBottom()
        } else if (event.type === 'tool_call') {
          currentToolCalls.value.push({ name: event.name, arguments: event.arguments })
          scrollToBottom()
        } else if (event.type === 'tool_result') {
          const last = currentToolCalls.value[currentToolCalls.value.length - 1]
          if (last) last.result = event.result
          toolCallsForMessage.push({ ...last })
          scrollToBottom()
        } else if (event.type === 'done') {
          break
        } else if (event.type === 'error') {
          message.error(event.content)
          break
        }
      }
    }

    chatMessages.value.push({
      role: 'assistant',
      content: streamContent.value,
      toolCalls: toolCallsForMessage.length ? toolCallsForMessage : undefined,
    })
  } catch (e) {
    message.error('请求失败: ' + e.message)
    chatMessages.value.push({ role: 'assistant', content: '抱歉，请求出错了，请检查网络连接或 LLM 设置。' })
  } finally {
    loading.value = false
    streamContent.value = ''
    currentToolCalls.value = []
    scrollToBottom()
  }
}
</script>

<style scoped>
.agent-container {
  height: calc(100vh - 64px);
  display: flex;
  justify-content: center;
  background: #f0f2f5;
}

.chat-panel {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  background: white;
  border-left: 1px solid #e8e8e8;
  border-right: 1px solid #e8e8e8;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #245f7b;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome h3 {
  color: #245f7b;
  margin-bottom: 8px;
}

.suggestions {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.suggestion-tag {
  cursor: pointer;
  padding: 6px 12px;
  font-size: 0.9rem;
  border-radius: 16px;
}

.suggestion-tag:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.message {
  display: flex;
  margin-bottom: 16px;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.message.user .message-bubble {
  background: #1890ff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: #f6f8fa;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-content :deep(p) {
  margin: 0 0 8px 0;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(ul), .message-content :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

.message-content :deep(pre) {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.thinking {
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.tool-calls {
  margin-top: 8px;
  font-size: 0.85rem;
}

.tool-call-item {
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tool-call-item:last-child {
  border-bottom: none;
}

.tool-name {
  color: #1890ff;
  font-weight: 500;
}

.tool-result {
  color: #666;
  margin-top: 2px;
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  align-items: flex-end;
}

.chat-input :deep(.ant-input) {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .chat-panel {
    border: none;
  }
  .message-bubble {
    max-width: 90%;
  }
}
</style>
