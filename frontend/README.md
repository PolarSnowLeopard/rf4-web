# RF4 Web Frontend (Vue 3 + Vite)

俄罗斯钓鱼 4 助手的 Web 前端，基于 Vue 3 + Vite + ant-design-vue。

## 开发

```bash
yarn install
yarn dev
```

默认开发服务器对外暴露（`vite --host`）。后端 API 基址在 `src/utils/request.js` 中配置。

## 构建

```bash
yarn build
yarn preview
```

## 目录约定

- `src/api/` 接口定义
- `src/views/` 路由页面
- `src/components/` 公共组件
- `src/layouts/` 布局
- `src/router/` 路由配置
- `src/store/` Pinia store
- `src/utils/` 通用工具（含 axios 封装）

更多说明见仓库根目录 `README.md`。
