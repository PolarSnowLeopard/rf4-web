from django.urls import path
from agent.views import agent_chat, agent_chat_stream

urlpatterns = [
    path('chat', agent_chat),
    path('chat/stream', agent_chat_stream),
]
