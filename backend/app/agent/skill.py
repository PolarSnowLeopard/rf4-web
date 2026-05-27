"""
Agent Skill loader — reads SKILL.md files following the Agent Skills standard,
parses YAML frontmatter, and renders templates with runtime data.

Skills live in agent/skills/<skill-name>/SKILL.md.
Template variables (e.g. {{db_overview}}) are substituted at build time.
"""

import os
import re
from pathlib import Path

from django.db.models import Count
from wiki.models import (
    Fish, Bait, Lure, Rod, Reel, Line, Hook, Rig, Groundbait, Food, Accessory
)

SKILLS_DIR = Path(__file__).parent / 'skills'

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


def _load_skill_md(skill_name: str) -> str:
    """Load a SKILL.md file, strip YAML frontmatter, return body."""
    skill_path = SKILLS_DIR / skill_name / 'SKILL.md'
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")

    content = skill_path.read_text(encoding='utf-8')

    # Strip YAML frontmatter (between --- delimiters)
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end + 3:].lstrip('\n')

    return content


def _render_template(template: str, variables: dict) -> str:
    """Replace {{variable}} placeholders with provided values."""
    def replacer(match):
        key = match.group(1).strip()
        return variables.get(key, match.group(0))

    return re.sub(r'\{\{(\w+)\}\}', replacer, template)


def build_system_prompt() -> str:
    """Build the full system prompt from the fishing-assistant skill."""
    template = _load_skill_md('fishing-assistant')
    variables = {
        'db_overview': _get_database_overview(),
    }
    return _render_template(template, variables)
