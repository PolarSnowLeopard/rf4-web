# RF4-Fish-Helper（桌面版） — DEPRECATED

> 状态：已废弃，**不再维护**。归档于 `2026-04-20`，原仓库 `PolarSnowLeopard/rf4_helper_app`。
>
> 桌面版的核心功能（截图渔获识别）已迁移到本仓库的 Web 前端：
> - 路由：`/catch/from-image`（页面 `frontend/src/views/CatchFromImage.vue`）
> - 调用后端接口：`POST /api/wiki/catch_from_image`
>
> 本目录仅作为历史代码的只读参考，**不要再向其中提交新功能**。

---

## 历史说明

俄罗斯钓鱼 4 助手 — 桌面客户端（PyQt5 + uv + PyInstaller 打包）。

### 配置环境

```bash
uv venv
uv sync
uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 打包为 exe

```bash
pyinstaller RF4-helper.spec
```
