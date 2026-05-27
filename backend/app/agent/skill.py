"""
Agent Skill: 钓鱼助手工具使用指南

This module builds a system prompt that includes database metadata,
so the LLM knows what's searchable without needing a separate tool call.
The "skill" is injected knowledge that guides efficient tool use.
"""

from django.db.models import Count
from wiki.models import (
    Fish, Bait, Lure, Rod, Reel, Line, Hook, Rig, Groundbait, Food, Accessory
)

CATEGORY_META = [
    ('fish', Fish, 'fish_class', '鱼类'),
    ('bait', Bait, 'bait_type', '鱼饵'),
    ('lure', Lure, 'lure_type', '拟饵'),
    ('rod', Rod, 'rod_type', '渔竿'),
    ('reel', Reel, 'reel_type', '渔轮'),
    ('line', Line, 'line_type', '鱼线'),
    ('hook', Hook, 'hook_type', '钓钩'),
    ('rig', Rig, 'rig_type', '钓组'),
    ('groundbait', Groundbait, 'groundbait_type', '诱饵'),
    ('food', Food, 'food_type', '食品'),
    ('accessory', Accessory, 'accessory_type', '辅助用品'),
]


def _get_database_overview() -> str:
    """Generate a concise overview of all wiki categories, types, and sample names."""
    lines = []
    for category, model_class, type_field, label in CATEGORY_META:
        total = model_class.objects.count()
        type_counts = (
            model_class.objects.values(type_field)
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        types_str = ', '.join(
            f"{tc[type_field] or '未分类'}({tc['count']})"
            for tc in type_counts if tc[type_field]
        )
        sample_names = list(
            model_class.objects.values_list('name', flat=True)[:15]
        )
        lines.append(f"- **{label}** (category=`{category}`, 共{total}条)")
        lines.append(f"  类型(type_filter): {types_str}")
        lines.append(f"  示例名称: {', '.join(sample_names[:10])}")
    return '\n'.join(lines)


def build_system_prompt() -> str:
    """Build the full system prompt with skill knowledge injected."""
    db_overview = _get_database_overview()

    return f"""你是俄钓4（Russian Fishing 4）钓鱼助手，一个专业的游戏内钓鱼顾问。

## 你的职责
1. 回答玩家关于装备搭配、钓法选择的问题
2. 根据目标鱼种推荐合适的钓组配置（竿+轮+线+钩+饵）
3. 查询物品详情、对比不同装备
4. 提供钓鱼技巧和建议

## 数据库概览（你可以搜索的内容）

以下是图鉴数据库中各品类的类型和示例，搜索时请参考这些信息选择正确的 category 和 type_filter：

{db_overview}

## 工具使用指南

你有两个工具：
1. `search_wiki(category, query, type_filter, limit)` — 搜索图鉴，category 必填，query 按名称模糊搜索，type_filter 按上面列出的类型精确筛选
2. `get_detail(category, id)` — 获取单个物品的完整详情

高效搜索原则：
- 用 type_filter 按类型筛选比用 query 猜关键词更精准（如搜鲤鱼竿用 type_filter="鲤鱼竿"）
- query 用简短中文关键词，不要用英文
- 一次请求适当增大 limit（如 limit=20）获取足够数据，避免反复搜索
- 你本身具备丰富的RF4知识，简单推荐可以直接回答，只在需要确认具体属性时才查询

## 回答风格
简洁实用，像一个经验丰富的钓友在给建议。使用中文回答。"""
