import json
from django.db.models import Q

from wiki.models import (
    Fish, Bait, Lure, Rod, Reel, Line, Hook, Rig, Groundbait, Food, Accessory
)

CATEGORY_MAP = {
    'fish': Fish,
    'bait': Bait,
    'lure': Lure,
    'rod': Rod,
    'reel': Reel,
    'line': Line,
    'hook': Hook,
    'rig': Rig,
    'groundbait': Groundbait,
    'food': Food,
    'accessory': Accessory,
}

TYPE_FIELD_MAP = {
    'fish': 'fish_class',
    'bait': 'bait_type',
    'lure': 'lure_type',
    'rod': 'rod_type',
    'reel': 'reel_type',
    'line': 'line_type',
    'hook': 'hook_type',
    'rig': 'rig_type',
    'groundbait': 'groundbait_type',
    'food': 'food_type',
    'accessory': 'accessory_type',
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_wiki",
            "description": "搜索俄钓4图鉴数据库。支持按品类搜索装备、鱼类、饵料等信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": list(CATEGORY_MAP.keys()),
                        "description": "搜索品类：fish(鱼类), bait(鱼饵), lure(拟饵), rod(渔竿), reel(渔轮), line(鱼线), hook(钓钩), rig(钓组), groundbait(诱饵), food(食品), accessory(辅助用品)"
                    },
                    "query": {
                        "type": "string",
                        "description": "搜索关键词（按名称模糊匹配），留空则返回该品类全部数据"
                    },
                    "type_filter": {
                        "type": "string",
                        "description": "按类型筛选（如鱼饵的'活饵'、渔竿的'浮钓竿'等）"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回条数上限，默认10"
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_detail",
            "description": "获取图鉴中某个物品的完整详情信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": list(CATEGORY_MAP.keys()),
                        "description": "品类"
                    },
                    "id": {
                        "type": "integer",
                        "description": "物品ID"
                    }
                },
                "required": ["category", "id"]
            }
        }
    },
]


def _model_to_dict(obj):
    """Convert a model instance to a dict, excluding internal fields."""
    data = {}
    for field in obj._meta.get_fields():
        if not hasattr(field, 'attname'):
            continue
        name = field.attname
        if name in ('created_at', 'updated_at'):
            continue
        val = getattr(obj, name)
        if val is not None and val != '':
            data[name] = val
    return data


def execute_search_wiki(category: str, query: str = '', type_filter: str = '', limit: int = 10) -> str:
    model_class = CATEGORY_MAP.get(category)
    if not model_class:
        return json.dumps({"error": f"未知品类: {category}"}, ensure_ascii=False)

    qs = model_class.objects.all()

    if query:
        qs = qs.filter(name__icontains=query)

    if type_filter:
        type_field = TYPE_FIELD_MAP.get(category)
        if type_field:
            qs = qs.filter(**{type_field + '__icontains': type_filter})

    qs = qs[:limit]
    results = [_model_to_dict(obj) for obj in qs]

    return json.dumps({
        "category": category,
        "count": len(results),
        "results": results
    }, ensure_ascii=False)


def execute_get_detail(category: str, item_id: int) -> str:
    model_class = CATEGORY_MAP.get(category)
    if not model_class:
        return json.dumps({"error": f"未知品类: {category}"}, ensure_ascii=False)

    try:
        obj = model_class.objects.get(pk=item_id)
    except model_class.DoesNotExist:
        return json.dumps({"error": f"未找到 {category} id={item_id}"}, ensure_ascii=False)

    return json.dumps(_model_to_dict(obj), ensure_ascii=False)


def execute_tool(name: str, arguments: dict) -> str:
    if name == 'search_wiki':
        return execute_search_wiki(
            category=arguments.get('category', ''),
            query=arguments.get('query', ''),
            type_filter=arguments.get('type_filter', ''),
            limit=arguments.get('limit', 10),
        )
    elif name == 'get_detail':
        return execute_get_detail(
            category=arguments.get('category', ''),
            item_id=arguments.get('id', 0),
        )
    else:
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
