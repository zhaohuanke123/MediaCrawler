# MediaCrawler Frontend

MediaCrawler 的 React 前端界面，提供友好的 UI 交互和数据可视化功能。

## 技术栈

- **React 18+** - 使用函数组件和 Hooks
- **TypeScript 5+** - 完整类型安全
- **Vite** - 快速构建工具
- **React Router v6** - 路由管理
- **Zustand** - 轻量级状态管理
- **Ant Design** - UI 组件库
- **ECharts** - 数据可视化
- **Axios** - HTTP 请求

## 项目结构

```
frontend/
├── public/              # 静态资源
│   ├── index.html      # HTML 模板
│   └── logo.svg        # 应用图标
├── src/
│   ├── components/     # 可复用组件
│   │   ├── Common/     # 通用组件
│   │   ├── Layout/     # 布局组件
│   │   ├── Form/       # 表单组件
│   │   ├── Display/    # 展示组件
│   │   └── Charts/     # 图表组件
│   ├── pages/          # 页面组件
│   │   ├── Dashboard.tsx    # 仪表盘
│   │   ├── Crawler.tsx      # 爬虫管理
│   │   ├── Results.tsx      # 结果展示
│   │   ├── Statistics.tsx   # 统计分析
│   │   ├── TaskList.tsx     # 任务列表
│   │   └── Settings.tsx     # 系统设置
│   ├── hooks/          # 自定义 Hooks
│   ├── services/       # API 服务
│   ├── store/          # 状态管理
│   ├── types/          # TypeScript 类型定义
│   ├── utils/          # 工具函数
│   ├── styles/         # 全局样式
│   ├── App.tsx         # 主应用组件
│   └── main.tsx        # 应用入口
├── package.json        # 依赖配置
├── tsconfig.json       # TypeScript 配置
├── vite.config.ts      # Vite 配置
└── README.md           # 项目文档
```

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 预览生产版本

```bash
npm run preview
```

## 功能模块

### 1. 仪表盘 (Dashboard)
- 任务统计概览
- 最近任务列表
- 快速操作入口

### 2. 爬虫管理 (Crawler)
- 平台选择（小红书、抖音、快手、B站、微博、贴吧、知乎）
- 爬取类型配置
- 关键词搜索
- 爬取参数设置

### 3. 结果展示 (Results)
- 数据表格展示
- 搜索和筛选
- 批量操作
- 数据导出

### 4. 统计分析 (Statistics)
- 平台数据分布图
- 时间趋势图
- 数据可视化

### 5. 任务列表 (TaskList)
- 任务状态管理
- 任务进度显示
- 任务控制（暂停、继续、取消）

### 6. 系统设置 (Settings)
- API 配置
- 代理设置
- 爬虫参数调整

## API 集成

前端通过 `/api/v1` 前缀与后端 API 通信。Vite 开发服务器已配置代理：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 环境变量

创建 `.env` 文件配置环境变量：

```env
VITE_API_BASE_URL=/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

## 代码规范

项目使用 ESLint 和 Prettier 进行代码规范检查：

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 浏览器支持

- Chrome/Edge >= 90
- Firefox >= 88
- Safari >= 14

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目遵循 NON-COMMERCIAL LEARNING LICENSE 1.1 许可证，仅供学习和研究使用。

## 相关链接

- [React 官方文档](https://react.dev)
- [Ant Design 文档](https://ant.design)
- [Vite 文档](https://vitejs.dev)
- [TypeScript 文档](https://www.typescriptlang.org)
