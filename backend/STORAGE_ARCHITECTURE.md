# 存储架构说明

## 概述

MediaCrawler项目采用**双数据库存储架构**，分别用于API管理和数据存储。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端界面                              │
│                    (React + TypeScript)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API 层                            │
│                   (FastAPI + SQLAlchemy)                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CrawlerService                                      │   │
│  │  ├─ 任务管理 (Task Management)                      │   │
│  │  ├─ 进度跟踪 (Progress Tracking)                    │   │
│  │  └─ WebSocket通知 (Real-time Updates)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                     │
│                         ▼                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  RealCrawlerService (集成层)                        │   │
│  │  ├─ 配置转换                                         │   │
│  │  ├─ 进度回调                                         │   │
│  │  └─ 错误处理                                         │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────┬───────────────────────────┬────────────────────┘
             │                           │
             ▼                           ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│   Backend数据库         │    │      根目录爬虫层             │
│  (media_crawler.db)    │    │  (Playwright + HTTP Client)  │
│                        │    │                              │
│  ┌──────────────────┐ │    │  ┌────────────────────────┐ │
│  │ Task (任务)      │ │    │  │ XiaoHongShuCrawler    │ │
│  │ - id             │ │    │  │ DouYinCrawler         │ │
│  │ - platform       │ │    │  │ BilibiliCrawler       │ │
│  │ - status         │ │    │  │ WeiboCrawler          │ │
│  │ - progress       │ │    │  │ ...                   │ │
│  │ - config         │ │    │  └────────────────────────┘ │
│  └──────────────────┘ │    │                              │
│                        │    └──────────────┬───────────────┘
│  ┌──────────────────┐ │                   │
│  │ Result (结果摘要)│ │                   ▼
│  │ - task_id        │ │    ┌──────────────────────────────┐
│  │ - title          │ │    │      爬虫数据库               │
│  │ - author         │ │    │  (sqlite_tables.db / MySQL)  │
│  │ - url            │ │    │                              │
│  └──────────────────┘ │    │  ┌────────────────────────┐ │
│                        │    │  │ XhsNote (小红书笔记)  │ │
│  ┌──────────────────┐ │    │  │ - note_id             │ │
│  │ Statistics       │ │    │  │ - title               │ │
│  │ (统计信息)       │ │    │  │ - content             │ │
│  └──────────────────┘ │    │  │ - source_keyword      │ │
└────────────────────────┘    │  └────────────────────────┘ │
                              │                              │
                              │  ┌────────────────────────┐ │
                              │  │ XhsNoteComment        │ │
                              │  │ (小红书评论)          │ │
                              │  └────────────────────────┘ │
                              │                              │
                              │  ┌────────────────────────┐ │
                              │  │ BilibiliVideo         │ │
                              │  │ DouyinVideo           │ │
                              │  │ WeiboNote             │ │
                              │  │ ...                   │ │
                              │  └────────────────────────┘ │
                              └──────────────────────────────┘
```

## 两个数据库的作用

### 1. Backend数据库 (media_crawler.db)

**位置**: `backend/media_crawler.db`

**用途**: 
- API任务管理
- 前端快速查询
- 统计分析

**表结构**:
- `tasks` - 任务记录（状态、进度、配置）
- `results` - 结果摘要（标题、作者、URL）
- `statistics` - 统计数据

**特点**:
- 轻量级
- 快速响应
- 面向API设计

### 2. 爬虫数据库 (sqlite_tables.db / MySQL)

**位置**: `database/sqlite_tables.db` 或 MySQL

**用途**:
- 存储完整爬取数据
- 详细内容和元数据
- 原始数据保留

**表结构** (每个平台独立):
- `xhs_note` - 小红书笔记
- `xhs_note_comment` - 小红书评论
- `xhs_creator` - 小红书创作者
- `bilibili_video` - B站视频
- `douyin_video` - 抖音视频
- ...更多平台表

**特点**:
- 数据完整
- 结构详细
- 支持复杂查询

## 数据流程

### 创建任务

```
1. 前端发起请求
   POST /api/v1/crawler/start
   
2. Backend API创建任务
   INSERT INTO tasks (...) VALUES (...)
   
3. 启动爬虫
   RealCrawlerService.run_crawler()
   
4. 返回task_id给前端
```

### 执行爬取

```
1. 爬虫开始运行
   crawler.start()
   
2. 爬取数据并存储
   store.store_content(note)    → 爬虫数据库
   store.store_comment(comment) → 爬虫数据库
   
3. 更新进度
   UPDATE tasks SET progress=X  → Backend数据库
   
4. WebSocket通知
   ws.send(progress_update)     → 前端
```

### 查询结果

```
方案1: 通过Backend API (推荐用于前端)
GET /api/v1/results?task_id=xxx
- 返回结果摘要
- 快速响应
- 分页支持

方案2: 直接查询爬虫数据库 (用于数据分析)
SELECT * FROM xhs_note WHERE source_keyword='xxx'
- 返回完整数据
- 支持复杂查询
- 需要数据库访问权限
```

## 数据一致性策略

### 关联方式

两个数据库通过以下方式关联：

1. **source_keyword** - 爬虫数据库中存储的搜索关键词
2. **task_id** - Backend数据库中的任务ID
3. **timestamp** - 时间戳范围匹配

### 查询示例

**场景**: 查询某个任务的所有笔记

```python
# 1. 从Backend获取任务信息
task = db.query(Task).filter(Task.id == task_id).first()
keyword = task.config['keyword']
start_time = task.start_time
end_time = task.end_time

# 2. 从爬虫数据库获取详细数据
notes = crawler_db.query(XhsNote).filter(
    XhsNote.source_keyword == keyword,
    XhsNote.add_ts.between(start_time_ts, end_time_ts)
).all()
```

## 存储位置

### SQLite 模式 (默认)

```
MediaCrawler/
├── backend/
│   └── media_crawler.db          # Backend数据库
└── database/
    └── sqlite_tables.db           # 爬虫数据库
```

### MySQL 模式

```
MySQL服务器:
├── media_crawler (Backend)        # Backend数据库
│   ├── tasks
│   ├── results
│   └── statistics
└── media_crawler_data (爬虫)      # 爬虫数据库
    ├── xhs_note
    ├── xhs_note_comment
    ├── bilibili_video
    └── ...
```

**配置方式**:

Backend (`backend/.env`):
```env
DATABASE_TYPE=mysql
MYSQL_DATABASE=media_crawler
```

爬虫 (`config/db_config.py` 或 `.env`):
```env
MYSQL_DB_NAME=media_crawler_data
```

## 优点和缺点

### 双数据库方案

**优点**:
- ✅ 关注点分离 - API管理与数据存储独立
- ✅ 性能优化 - 前端查询不影响爬虫存储
- ✅ 灵活性高 - 可以独立升级或迁移
- ✅ 兼容性好 - 不影响现有爬虫代码

**缺点**:
- ❌ 数据冗余 - 部分信息重复存储
- ❌ 同步复杂 - 需要确保两边数据一致性
- ❌ 维护成本 - 需要管理两个数据库

### 未来改进方向

可以考虑统一为单一数据库：

```
统一数据库方案
├── core_data (核心数据层)
│   ├── content (内容表 - 原爬虫数据)
│   └── comments (评论表 - 原爬虫数据)
├── api_layer (API视图层)
│   ├── tasks (任务管理)
│   └── task_results (任务结果视图)
└── indexes (索引优化)
```

## 最佳实践

### 1. 前端查询

推荐使用Backend API：
```javascript
// 获取任务列表
GET /api/v1/crawler/tasks

// 获取任务结果
GET /api/v1/results?task_id=xxx&page=1&pageSize=20

// 导出数据
GET /api/v1/results/export?task_id=xxx&format=csv
```

### 2. 数据分析

直接访问爬虫数据库：
```sql
-- 按关键词统计
SELECT source_keyword, COUNT(*) 
FROM xhs_note 
GROUP BY source_keyword;

-- 热门内容
SELECT title, liked_count 
FROM xhs_note 
ORDER BY liked_count DESC 
LIMIT 100;
```

### 3. 数据迁移

从SQLite迁移到MySQL：
```bash
# 1. 导出SQLite数据
sqlite3 sqlite_tables.db .dump > data.sql

# 2. 转换格式（如需要）
sed 's/INTEGER PRIMARY KEY AUTOINCREMENT/INTEGER PRIMARY KEY AUTO_INCREMENT/g' data.sql > data_mysql.sql

# 3. 导入MySQL
mysql -u root -p media_crawler_data < data_mysql.sql
```

## 监控和维护

### 数据库大小监控

```bash
# SQLite
du -h backend/media_crawler.db
du -h database/sqlite_tables.db

# MySQL
SELECT 
  table_schema AS 'Database',
  SUM(data_length + index_length) / 1024 / 1024 AS 'Size (MB)'
FROM information_schema.tables
GROUP BY table_schema;
```

### 数据清理

```python
# 清理旧任务（Backend数据库）
DELETE FROM tasks 
WHERE status = 'completed' 
  AND end_time < DATE_SUB(NOW(), INTERVAL 30 DAY);

# 清理测试数据（爬虫数据库）
DELETE FROM xhs_note 
WHERE source_keyword LIKE 'test%';
```

## 总结

双数据库架构提供了清晰的职责分离和良好的性能，适合当前的项目需求。随着项目发展，可以考虑逐步统一为单一数据库架构，但需要仔细规划迁移策略。
