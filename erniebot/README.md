# 正山堂茶业消费者行为模拟系统

本系统用于模拟不同类型的茶叶消费者对正山堂推出的红茶新品的消费行为，包括是否进店、是否购买、消费金额等。它使用AI模型生成模拟数据，并提供分析工具。

## 项目结构

```
erniebot/
├── main.py                      # 主程序入口
├── socketplus.py                # Socket通信工具
├── requirements.txt             # 项目依赖
├── modules/                     # 模块化功能
│   ├── __init__.py              # 包标识文件
│   ├── utils.py                 # 工具函数库
│   ├── config.py                # 配置模块
│   ├── data_processor.py        # 数据处理模块（接口层）
│   ├── data_processor/          # 数据处理子模块
│   │   ├── __init__.py          # 子模块初始化文件
│   │   ├── utils.py             # 通用工具函数
│   │   ├── customer.py          # 客户互动相关函数
│   │   ├── stats.py             # 统计数据相关函数
│   │   └── validator.py         # 数据验证与修复函数
│   ├── product_manager.py       # 产品管理模块
│   ├── sales_analytics.py       # 销售分析模块接口
│   ├── socket_manager.py        # Socket通信管理模块
│   ├── simulation_handler.py    # 模拟处理模块
│   ├── message_processor.py     # 消息处理模块
│   ├── cache.py                 # 缓存管理模块
│   ├── client/                  # 客户端相关模块
│   │   ├── __init__.py          # 包标识文件
│   │   ├── api_client.py        # API客户端模块
│   │   ├── api_connector.py     # API连接器
│   │   ├── simulation_handler.py # 模拟处理模块
│   │   ├── message_processor.py # 消息处理模块
│   │   ├── utils.py             # 工具函数库
│   │   └── cache.py             # 缓存管理模块
│   └── sales_analytics/         # 销售分析模块
│       ├── __init__.py          # 包标识文件
│       ├── sales_tracker.py     # 销售追踪模块
│       ├── product_metrics.py   # 产品指标模块
│       ├── product_lifecycle.py # 产品生命周期分析
│       ├── report_generator.py  # 报告生成器
│       ├── consumer_analysis.py # 消费者分析
│       ├── price_analysis.py    # 价格分析
│       ├── product_association.py # 产品关联分析
│       ├── seasonal_analysis.py # 季节性分析
│       └── loyalty_program.py   # 忠诚度计划分析
└── config/                      # 配置文件目录
    ├── constants.yaml           # 常量配置
    ├── product_costs.yaml       # 产品成本配置
    ├── product_pricing.yaml     # 产品定价配置
    ├── comment_templates.yaml   # 评论模板
    ├── seasonal_preferences.yaml # 季节偏好配置
    ├── consumer_types.json      # 消费者类型定义
    ├── consumer_psychological_traits.yaml # 消费者心理特征
    ├── pricing_helper.py        # 定价助手模块
    └── 产品定价管理说明.md      # 产品定价说明文档
```

## 各模块功能介绍

### 核心模块

1. **config.py** - 配置模块
   - 包含系统运行所需的常量和配置
   - 存储产品成本和库存数据
   - 定义消费者类型和有效场所
   - 定义消费者地域分布和心理特征

2. **data_processor.py** - 数据处理模块
   - 模块化重构后的接口层，保持向后兼容性
   - 数据处理功能分为以下子模块：
     - **utils.py**: 通用工具函数（字符串处理、格式转换等）
     - **customer.py**: 客户互动相关函数（生成客户数据、添加消费者特征等）
     - **stats.py**: 统计数据相关函数（日常统计、累计统计计算等）
     - **validator.py**: 数据验证与修复函数（验证数据完整性、生成默认数据等）
   - 验证和修复JSON数据
   - 生成默认的客户互动数据
   - 处理统计数据的计算
   - 添加消费者地域和心理特征

3. **product_manager.py** - 产品管理模块
   - 识别产品生成请求
   - 提取消费者类型
   - 处理品牌信息保存

4. **socket_manager.py** - Socket通信管理模块
   - 处理与客户端的通信
   - 发送模拟数据和结果
   - 接收用户指令

### 客户端模块

1. **api_client.py** - API客户端模块
   - 负责与AI服务的通信
   - 处理对话历史和请求
   - 提取JSON数据和生成茶品信息
   - 支持添加消费者画像信息的提示词

2. **api_connector.py** - API连接器
   - 管理与外部API的连接
   - 处理API认证和错误

3. **simulation_handler.py** - 模拟处理模块
   - 管理消费者行为的模拟过程
   - 处理模拟数据的生成和分析

4. **message_processor.py** - 消息处理模块
   - 解析用户输入和系统消息
   - 提取关键指令和参数

### 销售分析模块

1. **sales_tracker.py** - 销售追踪模块
   - 记录销售数据
   - 追踪销售趋势和模式

2. **product_metrics.py** - 产品指标模块
   - 计算产品销售指标
   - 分析产品表现

3. **report_generator.py** - 报告生成器
   - 生成详细的模拟总结报告
   - 提供销售和消费者行为洞察

4. **consumer_analysis.py** - 消费者分析
   - 分析消费者地域分布与销售表现关系
   - 分析消费者心理特征与购买行为关系

5. **price_analysis.py** - 价格分析
   - 分析价格对销售的影响
   - 提供价格优化建议

6. **product_lifecycle.py** - 产品生命周期分析
   - 跟踪产品在不同生命周期阶段的表现
   - 预测产品未来表现

7. **seasonal_analysis.py** - 季节性分析
   - 分析季节因素对销售的影响
   - 提供季节性营销建议

8. **loyalty_program.py** - 忠诚度计划分析
   - 分析消费者忠诚度
   - 提供忠诚度计划优化建议

9. **product_association.py** - 产品关联分析
   - 分析不同产品之间的关联性
   - 提供捆绑销售建议

## 使用方法

### 安装依赖

```
pip install -r requirements.txt
```

### 运行程序

```
python main.py
```

## 功能说明

1. **产品生成**
   - 通过输入"生成产品"等指令，可以创建一个符合正山堂品牌调性的创新红茶产品
   - 可以针对特定消费群体生成产品，如"为商务人士生成产品"

2. **消费者行为模拟**
   - 模拟不同类型消费者在不同场所的行为
   - 记录是否进店、浏览时间、购买产品、消费金额等信息
   - 包含消费者地域信息和消费心理特征

3. **数据分析**
   - 计算每日和累计的销售数据
   - 分析产品销售表现和爆款潜力
   - 生成详细的模拟总结报告
   - 分析消费者地域分布与销售表现关系
   - 分析消费者心理特征与购买行为关系

## 消费者画像功能

系统实现了消费者画像功能，对消费者类型进行了细化：

1. **地域分布**
   - 按地区划分：华东、华南、华北、华中、西南、西北、东北
   - 按城市类型划分：一线城市、新一线城市、二线城市、三四线城市、县城、农村
   - 可分析不同地域消费者的购买行为和偏好

2. **消费心理特征**
   - 价格敏感度：表示消费者对价格变化的敏感程度（高/中高/中/中低/低）
   - 品牌忠诚度：表示消费者对品牌的忠诚程度（高/中高/中/中低/低）
   - 决策速度：表示消费者做出购买决策的快慢（快/中/慢）
   - 购买动机：描述消费者购买产品的主要原因
   - 信息获取渠道：消费者了解产品信息的主要途径
   - 购买影响因素：影响消费者购买决策的关键因素

3. **分析功能**
   - 地域分析：包括各地区销售总额、客流量、平均客单价、最佳城市等
   - 消费心理分析：分析价格敏感度和品牌忠诚度与购买行为的关系
   - 洞察生成：自动生成消费者心理特征对销售的影响洞察

## 配置管理

系统使用YAML和JSON配置文件管理各种设置：

1. **constants.yaml** - 基本常量配置
2. **product_costs.yaml** - 产品成本配置
3. **product_pricing.yaml** - 产品定价策略
4. **comment_templates.yaml** - 消费者评论模板
5. **seasonal_preferences.yaml** - 季节性消费偏好
6. **consumer_types.json** - 消费者类型定义
7. **consumer_psychological_traits.yaml** - 消费者心理特征定义

## 开发者说明

- 添加新功能时，建议在适当的模块中进行扩展
- 可以通过修改config目录下的配置文件来调整产品信息和消费者画像
- 消费者画像可通过修改consumer_psychological_traits.yaml进行调整
- 产品定价策略可参考"产品定价管理说明.md"进行设置 