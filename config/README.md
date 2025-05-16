# 正山堂茶业 - 配置管理系统

本目录包含正山堂茶业各项目共享的配置管理文件，用于简化多服务间的配置协调。

## 配置文件说明

- `config.yaml` - 主配置文件，包含所有服务的基础配置
- `.env.example` - 环境变量示例文件
- `unity_config.json` - Unity前端配置
- `dashboard_config.json` - 分析面板前端配置
- `websocket_server.py` - WebSocket服务器实现
- `websocket_client.py` - WebSocket客户端实现

## 配置加载优先级

配置系统遵循以下优先级规则：

1. **环境变量** - 最高优先级，覆盖其他所有配置
2. **本地配置文件** - 每个服务自己的配置文件
3. **共享配置文件** - 本目录中的配置文件
4. **默认配置** - 代码中的硬编码默认值

## 使用方法

### Python项目 (erniebot和data_api)

```python
# 直接使用环境变量加载配置
import os
import dotenv

# 加载环境变量
dotenv.load_dotenv('.env')

# 获取配置项
host = os.environ.get("ERNIEBOT_HOST", "127.0.0.1") 
port = int(os.environ.get("ERNIEBOT_PORT", "12339"))
debug = os.environ.get("DEBUG", "false").lower() == "true"
```

### Unity项目 (My project)

Unity项目通过ConfigManager单例访问配置：

```csharp
// 获取配置
ServerConfig serverConfig = ConfigManager.Instance.GetServerConfig();
string host = serverConfig.ip;
int port = serverConfig.port;
```

### Vue项目 (tea-analytics-dashboard)

Vue项目通过config模块使用配置：

```javascript
// 初始化配置
import { initConfig, getApiConfig } from './config';

async function setup() {
  await initConfig();
  const apiConfig = getApiConfig();
  console.log('API基础URL:', apiConfig.baseUrl);
}
```

## 环境变量配置

可以通过环境变量覆盖配置，主要环境变量包括：

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| ERNIEBOT_HOST | erniebot服务主机 | 127.0.0.1 |
| ERNIEBOT_PORT | erniebot服务端口 | 12339 |
| DATA_API_HOST | data_api服务主机 | 127.0.0.1 |
| DATA_API_PORT | data_api服务端口 | 5000 |
| DB_PATH | 数据库文件路径 | simulation_data.db |
| AI_API_KEY | AI API密钥 | (空) |
| DEBUG | 调试模式 | false |
| LOG_LEVEL | 日志级别 | info |

## 添加新配置

直接在相应服务的配置模块中添加新的环境变量支持，并更新环境变量示例文件`.env.example`

## 多环境支持

通过环境变量可以轻松支持多环境：

- 开发环境: `.env.development`
- 测试环境: `.env.test`
- 生产环境: `.env.production`

## 故障排查

配置加载失败时，系统会回退到默认配置。可查看日志了解具体错误信息。 