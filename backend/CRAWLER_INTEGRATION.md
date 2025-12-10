# 爬虫集成说明文档

## 概述

本文档说明了backend项目如何集成根目录下的爬虫算法，实现前端发起任务后真正执行爬取功能。

## 架构说明

### 双存储系统

项目采用双数据库存储系统：

1. **Backend API 数据库**
   - 位置：`backend/media_crawler.db` (SQLite) 或 MySQL
   - 用途：存储任务（Task）、结果摘要（Result）、统计信息（Statistics）
   - 模型：`backend/app/models/`
   - 目的：为前端提供快速的任务管理和结果查询

2. **爬虫数据库**
   - 位置：`database/sqlite_tables.db` (SQLite) 或 MySQL
   - 用途：存储详细的爬取数据（笔记、评论、用户信息等）
   - 模型：`database/models.py`
   - 目的：存储完整的原始爬取数据

### 数据流程

```
前端 → Backend API → RealCrawlerService → 根目录爬虫 → 爬虫数据库
              ↓
         Backend数据库
              ↓
         前端（任务状态/摘要）
```

## 核心组件

### 1. RealCrawlerService

**文件**: `backend/app/services/real_crawler_service.py`

**功能**:
- 封装根目录爬虫的调用
- 配置转换（前端配置 → 爬虫配置）
- 进度跟踪和回调
- 支持7个平台

**关键方法**:
```python
async def run_crawler(
    platform: str,          # 平台名称: xhs, douyin, kuaishou, etc.
    crawler_type: str,      # 类型: search, detail, creator
    config_dict: dict,      # 配置: keyword, pages, sort, etc.
    progress_callback: callable  # 进度回调
) -> dict
```

### 2. CrawlerService (已更新)

**文件**: `backend/app/services/crawler_service.py`

**更新内容**:
- 集成了RealCrawlerService
- 自动检测真实爬虫可用性
- 失败时降级到模拟爬虫
- 保持WebSocket进度通知

### 3. 配置转换

前端配置示例：
```json
{
  "keyword": "编程",
  "pages": 10,
  "sort": "latest"
}
```

转换为爬虫配置：
```python
config.PLATFORM = "xhs"
config.CRAWLER_TYPE = "search"
config.KEYWORDS = "编程"
config.CRAWLER_MAX_NOTES_COUNT = 10
config.HEADLESS = True
config.SAVE_DATA_OPTION = "db"
```

## 数据存储说明

### 存储位置

1. **SQLite模式** (默认)
   - Backend数据: `backend/media_crawler.db`
   - 爬虫数据: `database/sqlite_tables.db`

2. **MySQL模式**
   - Backend数据: 配置在 `backend/.env` 中
   - 爬虫数据: 配置在根目录 `.env` 或 `config/db_config.py` 中

### 数据一致性

- 两个数据库系统**独立运行**，不会冲突
- Backend数据库存储任务元数据和简要结果
- 爬虫数据库存储完整的爬取数据
- 可以通过task_id关联两边的数据

### 查询完整数据

如需查询完整的爬取数据，可以：

1. 从Backend API获取task_id和基本信息
2. 直接查询爬虫数据库获取详细数据

示例：
```python
# Backend API - 获取任务信息
GET /api/v1/crawler/task/{task_id}

# 直接查询爬虫数据库
SELECT * FROM xhs_note WHERE source_keyword = '编程'
```

## 支持的平台

| 平台代码 | 平台名称 | 爬虫类 |
|---------|---------|--------|
| xhs | 小红书 | XiaoHongShuCrawler |
| douyin | 抖音 | DouYinCrawler |
| kuaishou | 快手 | KuaishouCrawler |
| bilibili | B站 | BilibiliCrawler |
| weibo | 微博 | WeiboCrawler |
| tieba | 百度贴吧 | TieBaCrawler |
| zhihu | 知乎 | ZhihuCrawler |

## 爬虫类型

- **search**: 关键词搜索爬取
- **detail**: 指定ID详情爬取
- **creator**: 创作者主页爬取

## 配置要求

### 必需的配置

在启动backend服务前，确保：

1. **根目录配置** (`config/base_config.py`)
   - 可以保持默认值，会被RealCrawlerService动态覆盖

2. **Backend配置** (`backend/.env`)
   ```env
   DATABASE_TYPE=sqlite
   SQLITE_DATABASE=media_crawler.db
   ```

3. **爬虫数据库** (自动创建)
   - SQLite: 会自动在 `database/` 目录创建
   - MySQL: 需要预先创建数据库

### 可选配置

- **IP代理**: `config.ENABLE_IP_PROXY = True`
- **登录方式**: `config.LOGIN_TYPE = "qrcode"` (需要手动扫码)
- **CDP模式**: `config.ENABLE_CDP_MODE = True` (使用真实浏览器)

## 运行说明

### 启动Backend服务

```bash
cd backend
python main.py
```

或使用uvicorn:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端发起任务

```javascript
// POST /api/v1/crawler/start
{
  "platform": "xhs",
  "type": "search",
  "config": {
    "keyword": "编程",
    "pages": 10,
    "sort": "latest"
  }
}
```

### 监控任务进度

通过WebSocket连接：
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/task/{task_id}')
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('Progress:', data.data.progress)
}
```

## 降级机制

如果真实爬虫不可用（例如：依赖未安装、配置错误），系统会自动降级到模拟爬虫：

```python
if REAL_CRAWLER_AVAILABLE:
    # 使用真实爬虫
    await RealCrawlerService.run_crawler(...)
else:
    # 使用模拟爬虫（仅用于测试）
    # 生成模拟数据
```

## 故障排查

### 真实爬虫不可用

检查日志：
```
[WARNING] Real crawler not available: ...
[INFO] 使用模拟爬虫执行任务
```

可能原因：
1. 依赖未安装（playwright, etc.）
2. 根目录模块导入失败
3. 配置错误

解决方法：
```bash
# 安装依赖
uv sync
uv run playwright install

# 检查导入
python -c "from base.base_crawler import AbstractCrawler; print('OK')"
```

### 数据未保存

检查：
1. 爬虫数据库路径是否正确
2. 数据库文件是否有写权限
3. 配置 `config.SAVE_DATA_OPTION` 是否设置为 "db"

查看数据：
```bash
# SQLite
sqlite3 database/sqlite_tables.db "SELECT COUNT(*) FROM xhs_note"

# 或使用SQL客户端查看MySQL
```

### 进度不更新

检查：
1. WebSocket连接是否正常
2. 后端日志中是否有进度更新
3. 任务是否被暂停

## 性能考虑

### 并发控制

- Backend API 限制：3个并发任务（可在 `backend/app/config.py` 修改）
- 爬虫限制：1个并发（在 `config/base_config.py` 中 `MAX_CONCURRENCY_NUM`）

### 资源占用

- 每个爬虫任务会启动浏览器实例
- 无头模式（HEADLESS=True）减少资源占用
- CDP模式会使用现有浏览器，资源占用更小

## 未来改进

- [ ] 统一双数据库为单一数据源
- [ ] 实时进度更新（目前是模拟的）
- [ ] 支持任务恢复和断点续传
- [ ] 更细粒度的配置控制
- [ ] 数据同步工具（爬虫DB → Backend DB）

## 相关文件

- `backend/app/services/real_crawler_service.py` - 爬虫集成服务
- `backend/app/services/crawler_service.py` - 任务管理服务
- `config/base_config.py` - 爬虫全局配置
- `database/models.py` - 爬虫数据模型
- `backend/app/models/` - Backend数据模型

## 支持

如有问题，请检查：
1. 日志文件
2. 数据库内容
3. 配置文件

或参考主项目README和文档。
