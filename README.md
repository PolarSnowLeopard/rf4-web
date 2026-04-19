# rf4-web

俄罗斯钓鱼 4（Russian Fishing 4）助手 Web 端单仓库（monorepo）。

由以下三个仓库合并而来（旧仓已 archive，仅作只读参考）：

- 后端：`PolarSnowLeopard/rf4`
- 前端：`PolarSnowLeopard/rf4-frontend`
- 桌面（已废弃）：`PolarSnowLeopard/rf4_helper_app`

详情见 [`docs/migration-notes.md`](./docs/migration-notes.md)。

---

## 目录结构

```
rf4-web/
  backend/             # Django + DRF 后端，含 Dockerfile
    app/               # Django 项目（manage.py、rf4 settings、wiki / user 应用）
  frontend/            # Vue 3 + Vite + ant-design-vue 前端
  legacy/
    desktop/           # 旧 PyQt5 桌面客户端（DEPRECATED，不再维护）
  docker-compose.yml   # 后端线上部署 compose（拉取或本地构建均可）
  docs/                # 项目相关文档
```

## 主要功能

- 鱼类图鉴：列表 / 详情 / 搜索筛选（`/manue/fish`）
- 渔获识别：上传游戏截图，调用后端 OCR + 目标检测识别新鲜度 / 鱼类 / 重量 / 售价（`/catch/from-image`，原桌面版功能已迁移至此）
- 用户登录（JWT）

## 开发

### 后端

```bash
cd backend
uv venv && uv sync
cd app
python manage.py migrate
python manage.py runserver 0.0.0.0:8888
```

或直接构建并运行 Docker 镜像（默认监听 9999）：

```bash
docker build -t polarsnowleopard/rf4-backend:latest backend
docker run --rm -p 9999:9999 --env-file .env polarsnowleopard/rf4-backend:latest
```

后端鱼类数据导入：

```bash
cd backend/app
python manage.py fish_import data/fish_data.json
# 清空再导入：加 --clear
```

### 前端

```bash
cd frontend
yarn install
yarn dev          # 开发服务器（vite --host）
yarn build        # 生产构建到 dist/
```

后端 API 基址在 `frontend/src/utils/request.js` 的 `baseURL`，默认指向线上后端。本地开发若指向其它地址，请相应修改。

## 部署

线上当前部署模式：

- 后端：在生产服务器上以 Docker 运行（`docker compose -f docker-compose.yml up -d`，镜像通过 GitHub Actions 推送到 Docker Hub 后由生产机 pull）。
- 前端：直接 `yarn dev` 运行（暂未引入静态构建 + nginx 的部署方式）。

如需本地一站式起后端：

```bash
docker compose up -d
```

`docker-compose.yml` 同时配置了 `image:` 与 `build:`，无需本地构建时直接 pull 远程镜像；本地需要带改动构建时执行 `docker compose build`。

## CI/CD

- 后端：`.github/workflows/backend-cicd.yml`
  - 触发：`push` 到 `main`
  - 步骤：构建并推送 `polarsnowleopard/rf4-backend:latest` → SSH 到生产机 pull 并重启 compose
  - 所需 Secrets：`DOCKER_HUB_USERNAME` / `DOCKER_HUB_TOKEN` / `PRODUCTION_HOST` / `PRODUCTION_USERNAME` / `PRODUCTION_SSH_KEY`
- 前端：暂未配置 GitHub Actions（开发模式 `yarn dev`）。

## 关联仓库

- 数据来源（独立项目，未并入本仓）：[`PolarSnowLeopard/rf4_wiki_scrapy`](https://github.com/PolarSnowLeopard/rf4_wiki_scrapy) — 基于 Scrapy 的 wiki 爬虫，可为本后端的鱼类数据库提供原始数据。
