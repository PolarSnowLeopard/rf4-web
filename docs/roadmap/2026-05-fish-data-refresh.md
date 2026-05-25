# Roadmap: 鱼类图鉴数据刷新 + 数据基础设施

- 起草日期：2026-05-25
- 状态：**待开发**

---

## 1. 背景与动机

当前数据库中 226 条鱼类数据来自 3 年前爬取的 Gamekee RF4 中文 wiki（`gamekee.com/rf4`），存在三个问题：

1. **数据不全**：游戏持续更新，新增了大量鱼种、水域
2. **字段缺失**：部分鱼种缺少描述、稀有度、重量等信息
3. **图片失效**：直接引用了 Gamekee CDN 的外链（`cdnimg-v2.gamekee.com`），现在已无法访问

## 2. 数据源

### 2.1 Gamekee RF4 Wiki（主要来源）

- URL: `https://www.gamekee.com/rf4`
- 内容：中文、覆盖鱼种/装备/饵料/地图等
- 技术特点：**SPA 架构**，页面内容由 JS 渲染，直接 HTTP GET 返回空壳
- 已知 API 端点前缀：`https://www.gamekee.com/v1/` （需要抓包确认具体接口）
- game_id: `50209`

### 2.2 历史爬虫参考

- 仓库：`PolarSnowLeopard/rf4_wiki_scrapy`（Scrapy 框架）
- 当时爬取的分类：鱼种、食品、鱼线、钓钩、拟饵、鱼饵、诱饵、辅助用品

## 3. 技术方案

### 3.1 数据获取（两种路线选其一）

**路线 A：API 直抓（推荐）**

Gamekee 前端是 SPA，必然有后端 JSON API。通过浏览器 DevTools Network 面板抓取：
1. 打开 `gamekee.com/rf4` 的鱼类图鉴列表页
2. 在 Network 中筛选 XHR/Fetch 请求
3. 找到返回鱼类列表数据的 API 端点（可能类似 `/v1/wiki/entry` 或 `/v1/content/...`）
4. 记录请求的 Headers（特别是 token/cookie）和参数格式
5. 用 Python requests/httpx 批量请求所有鱼种页面

优点：快速、稳定、拿到的就是结构化 JSON
缺点：可能有 token 过期问题、需要手动抓包确认

**路线 B：Playwright 渲染抓取**

用 Playwright 打开每个鱼种页面，等待 JS 渲染完成后提取 DOM 内容：
1. 启动无头浏览器
2. 逐页打开鱼种 URL（已知 source_url 模式：`gamekee.com/rf4/600277.html`）
3. 等待内容加载完毕
4. 提取页面 HTML 内容

优点：不依赖 API 逆向
缺点：慢、资源消耗大、可能被反爬

### 3.2 数据提取

无论用哪种路线，拿到原始数据后用 **LLM 提取结构化字段**：

```python
# 目标字段（扩展现有 Fish 模型）
{
    "name": "鱼名（中文）",
    "description": "简介",
    "img_url": "原始图片URL（后续下载到对象存储）",
    "fish_class": "稀有度（常见/稀有/稀有鱼种/传说）",
    "rare_weight": "上星重量",
    "super_rare_weight": "蓝冠重量",
    "habitats": ["栖息水域列表"],
    "baits": ["推荐饵料列表"],
    "min_weight": "最小重量",
    "max_weight": "最大重量",
}
```

可复用已有的 `services/llm/client.py` 基础设施。

### 3.3 图片处理

1. 从 Gamekee 下载原始鱼种图片
2. 上传到对象存储（腾讯云 COS 或阿里云 OSS）
3. 数据库 `img` 字段替换为对象存储 URL

### 3.4 数据导入

扩展现有 `manage.py fish_import` 命令，支持：
- 增量更新（按 name 匹配）
- 字段补全（只更新空字段）
- 全量覆盖模式（`--force`）

## 4. 实施步骤

1. **抓包确认 Gamekee API** — 用户在浏览器中操作，提供 API 端点和参数格式
2. **编写爬虫脚本** — `backend/scripts/scraper/` 目录下，独立于 Django app
3. **LLM 字段提取** — 对非结构化内容用 LLM 提取补全
4. **图片下载 + 上传对象存储** — 批量处理
5. **数据导入** — 更新 `fish_import` 命令
6. **前端适配** — 如有新字段则更新详情页展示

## 5. 需要用户操作的部分

- [ ] 浏览器打开 Gamekee RF4 wiki 鱼类页面，在 DevTools Network 中找到数据 API
- [ ] 提供对象存储的 bucket 信息和访问凭证
- [ ] 确认是否需要扩展 Fish 模型字段

---

# 附：未来功能 — 钓点信息聚合

## 数据源

- **微信小程序「俄钓宝典」**：用户每日上传钓点/点位信息
- **目标公众号**：待确认具体公众号名称

## 初步思路

1. 对小程序进行抓包（Charles/mitmproxy），分析其后端 API
2. 对公众号文章内容进行爬取 + LLM 提取结构化钓点数据
3. 新建 Django app（如 `spots/`）存储水域、钓点、鱼种、时间、装备等
4. 前端新增钓点浏览/搜索功能

## 注意事项

- 小程序登录态依赖微信 session，需要定期刷新
- 需评估数据使用的合规性（是否为用户公开分享的信息）
- 此功能优先级低于鱼类数据刷新，后续再启动
