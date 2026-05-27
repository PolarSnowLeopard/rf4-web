import json
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

import litellm
from services.llm.config import get_llm_settings
from agent.tools import TOOL_DEFINITIONS, execute_tool
from agent.skill import build_system_prompt

litellm.drop_params = True

MAX_TOOL_ROUNDS = 40


@api_view(['POST'])
def agent_chat(request):
    """Non-streaming agent chat endpoint."""
    messages = request.data.get('messages', [])
    llm_config = request.data.get('llm_config', {})

    if not messages:
        return Response({'error': 'messages is required'}, status=400)

    settings = get_llm_settings()
    model = llm_config.get('model') or settings.default_llm_model
    api_key = llm_config.get('api_key') or settings.openrouter_api_key
    api_base = llm_config.get('base_url') or settings.openrouter_base_url

    system_prompt = build_system_prompt()
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            resp = litellm.completion(
                model=model,
                messages=full_messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.7,
                timeout=60.0,
                api_key=api_key,
                api_base=api_base,
            )
        except Exception as e:
            return Response({'error': f'LLM调用失败: {str(e)}'}, status=502)

        choice = resp.choices[0]
        msg = choice.message

        if msg.tool_calls:
            full_messages.append(msg.model_dump())
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}
                result = execute_tool(fn_name, fn_args)
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            return Response({
                'content': msg.content,
                'role': 'assistant',
            })

    return Response({'content': '抱歉，处理过程过于复杂，请尝试简化你的问题。', 'role': 'assistant'})


@api_view(['POST'])
def agent_chat_stream(request):
    """Streaming agent chat endpoint using SSE."""
    messages = request.data.get('messages', [])
    llm_config = request.data.get('llm_config', {})

    if not messages:
        return Response({'error': 'messages is required'}, status=400)

    settings = get_llm_settings()
    model = llm_config.get('model') or settings.default_llm_model
    api_key = llm_config.get('api_key') or settings.openrouter_api_key
    api_base = llm_config.get('base_url') or settings.openrouter_base_url

    def event_stream():
        system_prompt = build_system_prompt()
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        for _ in range(MAX_TOOL_ROUNDS):
            try:
                resp = litellm.completion(
                    model=model,
                    messages=full_messages,
                    tools=TOOL_DEFINITIONS,
                    temperature=0.7,
                    timeout=60.0,
                    api_key=api_key,
                    api_base=api_base,
                    stream=True,
                )
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'LLM调用失败: {str(e)}'}, ensure_ascii=False)}\n\n"
                return

            collected_content = ""
            tool_calls_data = {}

            for chunk in resp:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                if delta.content:
                    collected_content += delta.content
                    yield f"data: {json.dumps({'type': 'content', 'content': delta.content}, ensure_ascii=False)}\n\n"

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_data:
                            tool_calls_data[idx] = {
                                "id": "",
                                "function": {"name": "", "arguments": ""},
                                "type": "function",
                            }
                        if tc.id:
                            tool_calls_data[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_data[idx]["function"]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_data[idx]["function"]["arguments"] += tc.function.arguments

            if not tool_calls_data:
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                return

            assistant_msg = {"role": "assistant", "content": collected_content or None, "tool_calls": list(tool_calls_data.values())}
            full_messages.append(assistant_msg)

            for idx in sorted(tool_calls_data.keys()):
                tc = tool_calls_data[idx]
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    fn_args = {}

                yield f"data: {json.dumps({'type': 'tool_call', 'name': fn_name, 'arguments': fn_args}, ensure_ascii=False)}\n\n"

                result = execute_tool(fn_name, fn_args)

                yield f"data: {json.dumps({'type': 'tool_result', 'name': fn_name, 'result': json.loads(result)}, ensure_ascii=False)}\n\n"

                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        yield f"data: {json.dumps({'type': 'content', 'content': '抱歉，处理过程过于复杂，请尝试简化你的问题。'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
