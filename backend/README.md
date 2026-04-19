# 俄钓4 助手

## 鱼获提取工具

读取指定目录下所有图片，依次提取鱼获信息最终汇总到指定csv文件

```bash
python scripts/process_fish_images.py data/images -o data/test_output.csv
```

## django后端

首先进入django项目目录

```bash
cd app
```

### 1. 启动django项目

```bash
python manage.py runserver 0.0.0.0:8888
```

### 2. 导入数据

爬取的json数据统一存放于`app/data`目录下，导入数据命令如下：

**导入鱼类数据**

```bash
python manage.py fish_import data/fish_data.json
```

> 如果需要清空现有数据，可以添加`--clear`参数

### 3. 部署时启动

- 生产环境容器化部署
- 容器启动后先更新数据库结构

```bash
# 创建迁移文件（如果尚未创建）
docker-compose exec rf4-backend python manage.py makemigrations

# 应用迁移，创建表结构
docker-compose exec rf4-backend python manage.py migrate

# 创建超级用户(如果还没创建)
docker-compose exec rf4-backend python manage.py createsuperuser
```