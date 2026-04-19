# Roadmap: 渔获识别 VLM 重构 + 命名空间整改 + LLM 基础设施

- 起草日期：2026-04-20
- 状态：**待开发**（计划由后续 agent 执行）
- 关联 Issue：见仓库 issues 中标题为「Recognition VLM refactor + namespace split + LiteLLM/OpenRouter infra」的那一条

---

## 1. 背景与动机

### 1.1 当前实现的问题

渔获识别 (`/api/wiki/catch_from_image`) 现走两段式 pipeline：

1. Roboflow 托管的 YOLO workflow 检测每张「鱼卡」的 bbox（`services/catch_extractor/fish_cards.py`）
2. 百度 OCR 识别整图所有文字（`services/catch_extractor/get_ocr_result.py`）
3. 在 `services/catch_extractor/main.py` 里按几何 IoU 把 OCR 文字块匹配到鱼卡 bbox，再用正则 (`get_field_from_word`) 解析字段

实测有三个硬伤：

- **泛化差**：`unmarked_bounding = BoundingBox(410, 126, 1920-410, 1080-126, ...)` 等关键参数硬编码到 1080p 分辨率，不同电脑截图（2K/4K/超宽屏，鱼卡数量与位置都不同）很容易整体偏移
- **错配/漏检**：YOLO 框 ↔ OCR 框靠几何 IoU 配对是非常脆的耦合，任一边漏一个会连锁错位；`legal_fish_name = ["镜鲤", "鲤鲫鱼"]` 这种白名单也只能识别少数已知鱼
- **慢且不稳**：两次串行外部 API（且 Roboflow 跨境，已实测被 Cloudflare 403 拦截，参考 Catch 500 故障）

### 1.2 命名空间问题

当前 `wiki/` app 同时承载：

- **图鉴/参考数据**（只读）：`Fish` 模型、`fish_list/fish_detail` 视图
- **渔获识别**（动作 + AI 流水线）：`Catch` 模型、`ImageUploadSerializer`/`ImageProcessingResponseSerializer`、`get_catch_from_image`、对 `services/catch_extractor` 的全部依赖

这两类职能不该共享一个 Django app。参考现有 `user/`、`wiki/` 的「能力域命名」风格，渔获识别该独立成 `recognition/`，并预留给未来的其它视觉/识别能力（如装备识别、地图识别）。

### 1.3 LLM 基础设施

后续还有别的 LLM agent 开发计划，现在就把统一的 LLM 客户端抽出来，避免各功能各搞一套。

**技术选型**：

- 客户端框架：[**LiteLLM**](https://github.com/BerriAI/litellm) — 统一 100+ LLM 提供商的 OpenAI 兼容协议，方便后续切换模型
- Provider：[**OpenRouter**](https://openrouter.ai) — 一个 API 键访问几乎所有主流模型；按 token 计费，无最低消费

---

## 2. 目标与非目标

### 2.1 目标

1. 用单次 VLM 调用替代 YOLO + OCR + 几何对齐
2. 引入 `services/llm/` 通用 LLM 客户端（LiteLLM + OpenRouter），供本任务及后续所有 LLM agent 复用
3. 把渔获识别从 `wiki/` app 迁出到独立的 `recognition/` app，URL 改为 `/api/recognition/catch_from_image`
4. 错误兜底：上游 API 失败时返回结构化错误（不再吞 traceback、不再返回 Django HTML 500）
5. 接口契约（`{image, fishes}`）保持兼容，前端最小改动（仅改 import 路径与 URL）

### 2.2 非目标（本轮不做）

- 不做截图历史持久化（`Catch` 模型本轮先迁过去但不接 ForeignKey、不写新字段）
- 不做用户配额/限流
- 不做前端的"分块上传/进度条"高级体验
- 不做模型本地化部署（GPU 后端自托管 VLM 留给后续 roadmap）

---

## 3. 详细方案

### 3.1 命名空间整改 — Backend

**新建 Django app `recognition/`**，最终结构：

```
backend/app/
  recognition/
    __init__.py
    apps.py                   # name='recognition'
    models.py                 # 把 wiki.Catch 迁过来
    urls.py                   # path('catch_from_image', ...)
    serializers/
      __init__.py
      catchSerializer.py      # 从 wiki.serializers 迁过来
    views/
      __init__.py
      imageView.py            # get_catch_from_image
    migrations/
      0001_initial.py         # 见 §3.1.1
```

#### 3.1.1 数据迁移策略

`wiki.Catch` 当前线上**没有业务数据**（仅作字段定义存在；表里没有写入路径）。建议：

- 在 `recognition` app 下重新声明 `Catch` 模型，**显式指定 `db_table = 'recognition_catch'`**
- 在 `wiki/migrations/` 下新增一个 migration 删除 `wiki.Catch` 表（`migrations.DeleteModel('Catch')`）
- 在 `recognition/migrations/0001_initial.py` 中 `migrations.CreateModel(...)`
- 部署顺序：先跑 wiki 的 DeleteModel，再跑 recognition 的 CreateModel；两个迁移在同一次 `manage.py migrate` 里按依赖顺序执行即可

> 如果担心生产数据丢失（虽然预期空表），可以在迁移前手动 `mysqldump wiki_catch > backup.sql`。

#### 3.1.2 路由调整

`backend/app/api/urls.py`：

```python
urlpatterns = [
    path('user/', include('user.urls')),
    path('wiki/', include('wiki.urls')),
    path('recognition/', include('recognition.urls')),
]
```

`backend/app/wiki/urls.py` 删掉 `path('catch_from_image', ...)` 这一条。

`backend/app/recognition/urls.py`：

```python
from django.urls import path
from recognition.views.imageView import get_catch_from_image

urlpatterns = [
    path('catch_from_image', get_catch_from_image),
]
```

#### 3.1.3 `INSTALLED_APPS`

`backend/app/rf4/settings.py` 中 `INSTALLED_APPS` 加 `'recognition'`。

#### 3.1.4 旧路径短期兼容（可选）

为防止线上前端尚未发版时被打到旧 URL 导致 404，可在 `wiki/urls.py` 临时保留：

```python
# DEPRECATED: 将于 2026-05-01 之后移除，请改用 /api/recognition/catch_from_image
path('catch_from_image', get_catch_from_image_legacy_redirect),
```

其中 `get_catch_from_image_legacy_redirect` 内部直接调 `recognition.views.imageView.get_catch_from_image` 并打 warning 日志。本轮可不实现，前后端同步发版即可。

### 3.2 命名空间整改 — Frontend

新建 `frontend/src/api/recognition.js`：

```js
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

export { postCatchFromImage }
```

修改 `frontend/src/views/CatchFromImage.vue`：

```diff
- import { postCatchFromImage } from '@/api/wiki'
+ import { postCatchFromImage } from '@/api/recognition'
```

`frontend/src/api/wiki.js` 删掉 `postCatchFromImage` 与 `api.catchFromImage`。

路由 `/catch/from-image` 与菜单入口都不变。

### 3.3 LLM 基础设施 — `services/llm/`

新建 `backend/app/services/llm/` 包，作为整个项目所有 LLM 调用的唯一入口：

```
services/llm/
  __init__.py           # re-export 主要 API
  config.py             # 从环境变量加载 OPENROUTER_API_KEY 等
  client.py             # chat_completion(...) / acompletion(...) 薄封装
  vision.py             # 图片→data URL/base64 编码工具
  exceptions.py         # LlmUpstreamError, LlmTimeoutError, LlmInvalidResponseError
```

#### 3.3.1 依赖

`backend/pyproject.toml` 加：

```toml
"litellm>=1.50.0",
```

可选：移除 `inference-sdk>=0.12.0`（Roboflow 不再使用）。`openai` 包可保留也可移除（litellm 不强制依赖它）。

#### 3.3.2 环境变量

`.env`（生产服务器需手动追加）和文档示例需新增：

```
# LLM 基础设施
OPENROUTER_API_KEY=sk-or-v1-xxxxx
# 可选；不设则用默认。建议默认 google/gemini-2.0-flash-001
DEFAULT_VLM_MODEL=openrouter/google/gemini-2.0-flash-001
DEFAULT_LLM_MODEL=openrouter/google/gemini-2.0-flash-001
```

#### 3.3.3 `services/llm/client.py` 接口形态

LiteLLM 内置支持 OpenRouter（`model="openrouter/<provider>/<model>"`），无需自配 base_url。

```python
# services/llm/client.py
import os
from typing import Any
import litellm
from litellm import completion, acompletion
from .config import get_llm_settings
from .exceptions import LlmUpstreamError, LlmInvalidResponseError

litellm.drop_params = True  # 不同 provider 参数不一致时自动 drop

def chat_completion(
    *,
    messages: list[dict],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    timeout: float = 60.0,
    **kwargs: Any,
) -> str:
    """同步调用，返回 message.content 字符串。"""
    settings = get_llm_settings()
    model = model or settings.default_llm_model
    try:
        resp = completion(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            api_key=settings.openrouter_api_key,
            **kwargs,
        )
    except Exception as e:
        raise LlmUpstreamError(f"LLM upstream call failed: {e}") from e

    try:
        return resp.choices[0].message.content
    except (AttributeError, IndexError) as e:
        raise LlmInvalidResponseError(f"Invalid LLM response shape: {resp}") from e
```

异步版 `async def achat_completion(...)` 同理走 `acompletion`。

#### 3.3.4 `services/llm/vision.py`

```python
import base64
from io import BytesIO
from PIL import Image

def image_to_data_url(image: Image.Image, format: str = "PNG") -> str:
    buf = BytesIO()
    image.save(buf, format=format)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{b64}"

def build_vision_message(prompt: str, image: Image.Image) -> list[dict]:
    return [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_to_data_url(image)}},
        ],
    }]
```

### 3.4 渔获识别业务实现 — `services/recognition/`

新建 `backend/app/services/recognition/`：

```
services/recognition/
  __init__.py
  catch_extractor.py    # 新实现：VLM 单次调用
  prompts.py            # 提示词集中管理
  schema.py             # 输出 JSON schema
```

#### 3.4.1 `prompts.py`

```python
CATCH_EXTRACT_PROMPT = """\
你是一个从《俄罗斯钓鱼 4》(Russian Fishing 4) 鱼市截图中提取渔获数据的助手。

请仔细识别图中所有渔获卡片，对每一条鱼提取以下 4 个字段：
- freshness: 新鲜度，形如 "42分-97%"（前面数字代表分钟，后面是百分比）
- name: 鱼类中文名（保持游戏内原文）
- weight: 重量，原样保留单位，例如 "3.705公斤" 或 "0.825千克"
- price: 售价（卢布），保留游戏内显示的整数或小数

要求：
1. 只识别"鱼市出售"列表中的渔获卡片，不要识别 UI 按钮、状态栏、对话框等其它内容。
2. 如果某字段在卡片上不可见或不可读，对应字段返回空字符串。
3. **严格按 JSON 数组返回**，每个元素是一条鱼的对象。不要额外解释、不要 markdown 代码块包裹。
4. 鱼的顺序按从上到下、从左到右排列。

输出示例：
[
  {"freshness": "42分-97%", "name": "镜鲤", "weight": "3.705公斤", "price": "2.59"},
  ...
]
"""
```

#### 3.4.2 `catch_extractor.py`

```python
import json
import logging
from PIL import Image
from services.llm.client import chat_completion
from services.llm.vision import build_vision_message
from services.llm.config import get_llm_settings
from services.llm.exceptions import LlmUpstreamError, LlmInvalidResponseError
from .prompts import CATCH_EXTRACT_PROMPT

log = logging.getLogger(__name__)

FIELDS = ("freshness", "name", "weight", "price")

def extract_fishes(
    *,
    image: Image.Image | None = None,
    image_path: str | None = None,
) -> tuple[Image.Image, list[list[str]]]:
    """单次 VLM 调用提取渔获。

    返回 (annotated_image, fishes)：
      - annotated_image: 现阶段直接返回原图（不画框，简化实现）。
      - fishes: list[list[str]]，每行 [freshness, name, weight, price]，与历史接口契约兼容。
    """
    if image is None and image_path is None:
        raise ValueError("image or image_path is required")
    if image is None:
        image = Image.open(image_path).convert("RGB")

    settings = get_llm_settings()
    messages = build_vision_message(CATCH_EXTRACT_PROMPT, image)

    raw = chat_completion(
        model=settings.default_vlm_model,
        messages=messages,
        response_format={"type": "json_object"},  # 见 §3.4.3
        temperature=0.0,
        max_tokens=4096,
        timeout=60.0,
    )

    fishes_dicts = _parse_fishes_json(raw)
    fishes = [
        [d.get(k, "") or "" for k in FIELDS]
        for d in fishes_dicts
    ]
    return image, fishes


def _parse_fishes_json(raw: str) -> list[dict]:
    """容忍 ```json 包裹、外层 {fishes: [...]} 包裹等常见输出形态。"""
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:].lstrip()
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise LlmInvalidResponseError(f"Model output is not valid JSON: {raw[:500]}") from e

    if isinstance(data, dict):
        for key in ("fishes", "result", "data", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise LlmInvalidResponseError(f"Model output JSON is not a list: {raw[:500]}")
    return [d for d in data if isinstance(d, dict)]
```

#### 3.4.3 `response_format` 注意事项

- `google/gemini-2.0-flash-001` 通过 OpenRouter 时支持 `response_format={"type": "json_object"}`
- 如选用其它模型不支持，`litellm.drop_params=True` 会自动忽略该参数；此时仅靠 prompt 约束
- 更强约束可改用 `{"type": "json_schema", "json_schema": {...}}`（OpenAI 风格），LiteLLM 会按各 provider 能力转换

### 3.5 视图层 — `recognition/views/imageView.py`

```python
import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from PIL import Image
import base64
from io import BytesIO

from recognition.serializers.catchSerializer import (
    ImageUploadSerializer,
    ImageProcessingResponseSerializer,
)
from services.recognition.catch_extractor import extract_fishes
from services.llm.exceptions import LlmUpstreamError, LlmInvalidResponseError

log = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_catch_from_image(request):
    """从上传的截图识别渔获。
    Response: {"image": <base64 png>, "fishes": [[freshness, name, weight, price], ...]}
    """
    serializer = ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    upload = serializer.validated_data['image']
    try:
        image = Image.open(upload).convert("RGB")
    except Exception as e:
        return Response({"detail": f"无法解析图片: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        annotated, fishes = extract_fishes(image=image)
    except LlmUpstreamError as e:
        log.warning("VLM upstream failure: %s", e)
        return Response(
            {"detail": "上游模型暂不可用，请稍后重试", "code": "LLM_UPSTREAM_ERROR"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except LlmInvalidResponseError as e:
        log.warning("VLM invalid response: %s", e)
        return Response(
            {"detail": "模型返回内容无法解析", "code": "LLM_INVALID_RESPONSE"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    buf = BytesIO()
    annotated.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    payload = {"image": image_b64, "fishes": fishes}
    resp = ImageProcessingResponseSerializer(data=payload)
    resp.is_valid(raise_exception=True)
    return Response(resp.validated_data)
```

**关键差异**：

- 不再写盘到 `ASSETS_DIR/original_image.png`（多并发会互相覆盖）
- 上游错误返回 502 + 结构化 JSON，不再裸暴 Django 500 HTML

### 3.6 旧实现处理

`backend/app/services/catch_extractor/` 整个目录在新实现稳定运行后**直接删除**，包括：

- `main.py`、`fish_cards.py`、`get_ocr_result.py`、`roboflow_format.py`、`utils.py`、`__init__.py`、本地 `fish_grid.jpg` 测试图等

并删除 `backend/pyproject.toml` 里的 `inference-sdk`，可选删 `openai`、`pytesseract`、`opencv-python` 等只有旧 pipeline 在用的依赖（要先 grep 确认无引用）。

环境变量 `BAIDU_API_KEY` / `BAIDU_SECRET_KEY` / `ROBOFLOW_API_KEY` 不再使用，可从 `.env` 移除。

### 3.7 性能/质量优化（Phase 4，可选）

仅当 §6 验收测试发现整图识别准确率不达标时再做：

- **按行切片**：用 OpenCV 投影法找水平空白带，把整图切成 N 个横条，`asyncio.gather` 并行调用 VLM，结果按 y 顺序拼接
- 入口仍为 `extract_fishes`，对调用方透明
- 涉及文件：`services/recognition/catch_extractor.py` 内增 `_split_by_horizontal_gaps(image)` 与 `_extract_async(...)` 路径

---

## 4. 模型选型建议

OpenRouter 上推荐以下作为 `DEFAULT_VLM_MODEL` 候选（按性价比排序）：

| Model ID | 视觉能力 | 速度 | 成本（每张 1080p ≈） | 备注 |
|---|---|---|---|---|
| `openrouter/google/gemini-2.0-flash-001` | 强 | 极快 (~1s) | $0.0003 | **推荐默认**。JSON mode 支持好，性价比最高 |
| `openrouter/openai/gpt-4o-mini` | 强 | 快 (~2s) | $0.0015 | JSON mode 最稳 |
| `openrouter/anthropic/claude-3.5-sonnet` | 最强 | 中 (~3s) | $0.015 | 精度最高，密集图最稳，贵 |
| `openrouter/google/gemini-2.5-flash` | 更强 | 快 | $0.0006 | 2025 年新版，可考虑直接上 |

**网络可达性提醒**：OpenRouter 域名 `openrouter.ai` 在国内裸连不稳，生产服务器（腾讯云 fdueblab.cn）需自备出境（已知 Roboflow 被 Cloudflare 拦的同一台机器）。如出境不可解决，可在 §3.3 的 `client.py` 加一层 fallback：先试 OpenRouter，失败回落到国内 DashScope `qwen-vl-max`（同样能让 LiteLLM 走，模型 ID `dashscope/qwen-vl-max`）。这一回落机制可放到 Phase 5。

---

## 5. 分阶段实施顺序

强烈建议按以下顺序提交、并各自一次 commit：

1. **Phase 1 — 命名空间整改**（不引入新行为，只搬家）
   - 后端：新建 `recognition` app，迁 `Catch` 模型/序列化器/视图，调整 URL，加迁移
   - 前端：新建 `api/recognition.js`，改 `CatchFromImage.vue` 的 import，删 `api/wiki.js` 中相关导出
   - 验收：旧功能在新 URL 下完全不变地工作

2. **Phase 2 — LLM 基础设施**
   - 加 `litellm` 依赖，新建 `services/llm/` 包
   - 加环境变量与 `.env.example`、根 README 与 docs 更新
   - 验收：写一个 `manage.py shell` 小 demo 调用 `chat_completion`，能拿到一句问候

3. **Phase 3 — VLM 渔获识别**
   - 新建 `services/recognition/`，重写 `catch_extractor.extract_fishes`
   - 视图改为调用新实现 + 错误兜底
   - 删除 `services/catch_extractor/` 与不再使用的依赖、环境变量
   - 验收：见 §6

4. **Phase 4 — 性能/质量优化**（可选，按 §3.7）

5. **Phase 5 — 国内回落 + 可观测**（可选）
   - DashScope 回落
   - 每次调用日志 model / latency / token usage / cost

---

## 6. 验收标准

收集 ≥10 张不同分辨率（1080p / 2K / 4K，至少各 2 张）、不同鱼数（5 / 15 / 25+ 各 ≥2 张）的真实截图作为基准集，放在 `backend/app/services/recognition/tests/fixtures/`，并人工标注对应的 `fishes_expected.json`。

测试脚本 `backend/app/services/recognition/tests/test_extract_fishes.py` 跑通后必须满足：

- **每条鱼字段命中率 ≥ 95%**（相对人工标注）
- **每张图整体延迟 < 5s**（默认模型 `gemini-2.0-flash`）
- **失败用例返回 502 + 结构化 JSON**，不出现 Django HTML 500
- **接口契约**（`{image: <base64>, fishes: [[...], [...]]}`）与改前完全一致，前端无须额外适配（除 import 路径）

---

## 7. 影响面与回滚

### 7.1 影响

- **前端**：仅 `CatchFromImage.vue` 一行 import + 新建一个 api 文件
- **数据库**：drop `wiki_catch` 表（预期空），新建 `recognition_catch` 表
- **环境变量**：新增 `OPENROUTER_API_KEY`（必需）；移除 `BAIDU_*` / `ROBOFLOW_API_KEY`（可选）
- **依赖**：新增 `litellm`；移除 `inference-sdk`，可选移除 `openai`、`pytesseract`、`opencv-python`、`pandas`、`scikit-learn`、`scipy`、`seaborn` 等仅旧实现使用的包（合并 PR 前要逐一 grep 确认）
- **CI/CD**：无变更（仍是 `backend-cicd.yml`）

### 7.2 回滚

- 代码层面：`git revert <merge_commit>`
- 数据层面：`python manage.py migrate wiki <previous>` + `python manage.py migrate recognition zero`
- 前端：同步 revert，或临时把 `api/recognition.js` 内 URL 改回 `/api/wiki/catch_from_image`（前提是后端 §3.1.4 兼容路由还在）

---

## 8. 待与人确认的开放问题（开始动手前请向 owner 确认）

1. **默认 VLM 模型**：是否就用 `openrouter/google/gemini-2.0-flash-001`？还是想直接上 `openrouter/google/gemini-2.5-flash`？
2. **OpenRouter 出境**：生产服务器是否已具备访问 `openrouter.ai` 的网络？如否，是否本轮就把国内回落（DashScope qwen-vl-max）一起做了？
3. **`Catch` 表名**：是否同意改名为 `recognition_catch`（drop 旧表 + 建新表）？还是要求保留旧表名 `wiki_catch`（在新模型上 `class Meta: db_table = 'wiki_catch'`）？
4. **旧依赖清理**：是否一次性移除 `inference-sdk`/`openai`/`pytesseract`/`opencv-python`/`pandas`/`scipy`/`scikit-learn`/`seaborn`/`matplotlib`/`seaborn` 等只为旧 pipeline 服务的包？或先保留以防万一？

---

## 9. 参考文件清单（让接手 agent 能直达上下文）

- 当前后端入口：`backend/app/wiki/views/fishView.py`（`get_catch_from_image`）
- 当前业务实现：`backend/app/services/catch_extractor/main.py`
- 当前前端入口：`frontend/src/views/CatchFromImage.vue`
- 当前前端 API：`frontend/src/api/wiki.js`（`postCatchFromImage`）
- 路由聚合：`backend/app/api/urls.py`、`backend/app/wiki/urls.py`
- 模型定义：`backend/app/wiki/models.py`（`Catch`）
- 序列化器：`backend/app/wiki/serializers/catchSerializer.py`
- 设置：`backend/app/rf4/settings.py`（`INSTALLED_APPS`、`ASSETS_DIR`）
- 依赖：`backend/pyproject.toml`
- 历史背景：`docs/migration-notes.md`
