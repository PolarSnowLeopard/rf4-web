# 迁移说明

本仓库 `rf4-web` 由三个旧仓合并而来。迁移日期：**2026-04-20**。

## 旧仓最终 commit

| 旧仓 | 角色 | 最终 commit | 提交时间 (UTC) | 在新仓的位置 |
|------|------|-------------|---------------|--------------|
| [`PolarSnowLeopard/rf4`](https://github.com/PolarSnowLeopard/rf4) | Django 后端 | `d996df748a1f71b5ee6772be57e967911d9553a7` | 2025-05-20 14:05 | `backend/` |
| [`PolarSnowLeopard/rf4-frontend`](https://github.com/PolarSnowLeopard/rf4-frontend) | Vue 3 前端 | `6a346759c9a244ce079ac8ced1b90af8e1c3b1f4` | 2025-05-20 14:09 | `frontend/` |
| [`PolarSnowLeopard/rf4_helper_app`](https://github.com/PolarSnowLeopard/rf4_helper_app) | PyQt5 桌面客户端 | `22206db8822c36965542a26ab8593c7f3fe3ae79` | 2025-05-15 11:29 | `legacy/desktop/`（DEPRECATED） |

> 历史不保留：本仓库以一次性复制方式作为初始提交，旧仓 archive 为只读，需要历史时直接到旧仓查看上述 commit。

## 主要变更

### 1. 后端

- 整体从旧 `rf4/` 仓根下移到本仓 `backend/`。
- 旧 `rf4/.github/workflows/cicd.yml` 重命名为 `backend-cicd.yml` 并迁到本仓根 `.github/workflows/`，`docker build` 上下文由 `.` 改为 `backend`。
- 旧 `rf4/docker-compose.yml` 提到本仓根，并增加 `build.context: ./backend` 段（保留 `image:`，本地不构建时仍可直接 pull）。
- 业务代码（Django apps、序列化器、管理命令等）**未改动**。

### 2. 前端

- 整体从旧 `rf4-frontend/` 复制到本仓 `frontend/`。
- 新增渔获识别页面（替代桌面版同功能）：
  - 路由：`/catch/from-image`（`frontend/src/router/index.js`）
  - 页面：`frontend/src/views/CatchFromImage.vue`
  - 接口封装：`frontend/src/api/wiki.js` 新增 `postCatchFromImage(file)`，对应后端 `POST /api/wiki/catch_from_image`
  - 顶部菜单：`frontend/src/components/GlobalHeader.vue` 新增 `渔获识别` 入口
- 其它代码未改动；`baseURL`、登录、Pinia store 一切照旧。

### 3. 桌面端

- 旧 `rf4_helper_app/` 复制到 `legacy/desktop/` 仅作历史参考，README 顶部已标注 DEPRECATED。
- 桌面唯一被使用的能力（截图渔获识别）已通过上文的 Web 页面替代。
- 未迁移的内容：
  - PyQt5 UI 组件（`src/ui/main_window.py`）
  - PyInstaller 打包脚本（`RF4-helper.spec`、`setup.py`）
  - 桌面专属配置加载（`src/utils/config_loader.py`）
  - 早期未启用的本地推理实现（`src/core/image_processor.py`）

## 与未并入的爬虫仓的字段映射提醒

[`PolarSnowLeopard/rf4_wiki_scrapy`](https://github.com/PolarSnowLeopard/rf4_wiki_scrapy)（独立爬虫工程，未并入本仓）抓取后字段为 `cls`，而 Django 模型 `wiki.Fish` 字段为 `fish_class`。如以后通过 JSON 经 `python manage.py fish_import` 导入，需要在导出时把 `cls` 重命名为 `fish_class`。

## 旧仓 archive 后的 README 跳转

迁移完成后，三个旧仓 README 顶部均追加了「已迁移到 `PolarSnowLeopard/rf4-web`」的提示与链接，便于来自搜索引擎的访客直达本仓。
