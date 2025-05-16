# 正山堂茶业消费者行为分析系统

本项目是一个基于ERNIE Bot的智能消费者行为模拟与分析平台，专为正山堂茶业设计，用于精确模拟和分析茶叶消费者购买行为及偏好。通过人工智能技术，实现从消费者行为模拟到数据可视化分析的全流程解决方案。

## 系统模块

1. **ERNIE Bot模拟引擎 (`erniebot`)**：基于大语言模型生成真实的消费者互动场景和购买决策数据，并实时记录到日志文件中。
2. **Unity WebGL前端 (`My project`)**：采用3D可视化技术，直观展示消费者在店铺中的行为轨迹和互动过程。
3. **数据API服务 (`data_api`)**：提供RESTful接口，用于访问和处理来自模拟日志的结构化数据。
4. **数据分析平台 (`tea-analytics-dashboard`)**：基于Web的交互式分析平台，提供多维度的消费者行为分析和数据可视化。
5. **配置与通信模块 (`config`)**：负责全系统配置管理及各模块间的WebSocket通信实现。

## 系统架构

```
                                  ┌────────────────┐
                                  │ 配置与通信模块 │
                                  │ (config)       │
                                  └───────▲────────┘
                                          │
                               ┌──────────┴──────────┐
                               │                     │
┌─────────────┐      ┌─────────▼────────┐      ┌─────▼──────────┐      ┌────────────────┐
│ Unity前端   │◄────►│ ERNIE Bot后端    │◄────►│ 数据API服务    │◄────►│ 数据分析前端   │
│ (模拟可视化) │      │ (大模型模拟)     │      │ (数据接口)     │      │ (数据可视化)   │
└─────────────┘      └─────────┬────────┘      └─────┬──────────┘      └────────────────┘
                               │                     │
                               └─────────►◄─────────┘
                                     ┌───────▼───────┐
                                     │   数据库      │
                                     │ (存储模拟数据)│
                                     └───────────────┘
```
*说明：箭头表示主要的数据流或控制流方向，配置模块为各组件提供全局支持。*

## 安装与启动指南

### 1. 环境要求

- Python 3.9+ (推荐Python 3.10)
- Node.js 16+ (推荐最新LTS版本)
- Unity Editor (版本对应`My project/ProjectSettings/ProjectVersion.txt`) 

### 2. 组件启动流程

#### 安装依赖 (项目根目录)

```bash
# 安装所有Python依赖
pip install -r requirements.txt
```

#### 启动ERNIE Bot后端

```bash
cd erniebot
python main.py
```

> 服务启动后将创建WebSocket服务器，等待WebGL客户端连接，并处理用户产品设计指令，自动开始消费者行为模拟。模拟数据自动存入数据库，无需手动运行`test_data_save.py`。

#### 启动数据API服务

```bash
cd data_api
python app.py
```

> API服务默认运行在http://localhost:5000，提供多个数据分析接口。

#### 启动数据分析前端

```bash
cd tea-analytics-dashboard
npm install
npm run serve
```

访问`http://localhost:8080`查看数据分析仪表板。

#### 运行Unity WebGL前端

1. 在浏览器中直接访问`http://你的域名/web/` (部署版本)
2. 或通过Unity Editor打开`My project`文件夹，运行主场景进行本地测试

或者直接通过双击erniebot文件下的start_webgl.bat文件一键启动

## API接口文档

系统提供以下RESTful API接口：

| 接口名称 | URL路径 | 说明 |
|---------|---------|------|
| 仪表板指标 | `/api/dashboard/metrics` | 获取核心业务指标概览 |
| 销售趋势 | `/api/dashboard/trend` | 获取时间维度销售数据 |
| 热销产品 | `/api/dashboard/hot-products` | 获取畅销产品排名 |
| 访客趋势 | `/api/dashboard/visitor-trend` | 获取访客流量变化 |
| 访客分析 | `/api/visitor/analysis` | 获取访客属性分析 |
| 访客转化率 | `/api/visitor/conversion` | 获取访客转化漏斗 |
| 消费者行为 | `/api/consumer/behavior` | 获取消费者行为路径 |
| 区域分析 | `/api/consumer/region` | 获取区域消费分布 |
| 心理分析 | `/api/consumer/psychology` | 获取消费心理画像 |
| 系统状态 | `/api/system/status` | 获取系统运行状态 |
| 系统配置 | `/api/system/config` | 获取/更新系统配置 |

## 使用流程

1. **产品设计与模拟**：通过WebGL界面向系统输入产品设计指令（如"设计一款针对年轻人的茶产品"）
2. **消费者行为模拟**：系统自动启动为期30天的消费者行为模拟，生成日志并实时存储到数据库
3. **数据分析与可视化**：访问数据分析平台，查看多维度的数据分析结果和可视化图表
4. **3D行为可视化**：通过Unity WebGL界面，观察模拟消费者在虚拟店铺中的行为轨迹

## 核心功能

1. **智能产品设计**：基于目标消费群体特征，智能生成茶产品方案及营销策略
2. **消费者行为模拟**：精确模拟不同类型消费者在店铺中的购物决策过程
3. **多维数据分析**：从销售、客流、区域、心理等多维度分析消费者行为特征
4. **客户价值分析**：区分新老客户价值，分析留存率和终身价值
5. **区域销售分析**：精准分析不同地域消费者的购买偏好和消费能力
6. **实时3D可视化**：通过WebGL技术直观展示消费者在店铺中的行为路径

## 技术栈

- **AI引擎**: PaddlePaddle ERNIE Bot大语言模型
- **后端技术**: Python, Flask, SQLite, WebSocket
- **前端技术**: Vue.js, Element UI, ECharts, WebGL
- **3D可视化**: Unity, C#, NavMeshAgent
- **数据通信**: WebSocket, RESTful API, JSON