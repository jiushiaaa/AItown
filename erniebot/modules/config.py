#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
erniebot配置模块 - 集成中央配置管理
"""

import os
import sys
from pathlib import Path

# 添加父目录到系统路径，以便导入config模块
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 尝试从公共模块导入配置管理器
try:
    from common.config_loader import config
except ImportError:
    print("错误：无法找到配置加载器。请确保 common.config_loader 可用。")

# 定义本地配置变量，用于向后兼容
HOST = "127.0.0.1"
PORT = 12339
DEBUG = False

# AI模型配置
MODEL_API_KEY = ""
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.7

# 数据库配置
DB_PATH = "simulation_data.db"

# 产品成本数据
PRODUCT_COSTS = {}

def load_configuration():
    """加载配置，优先使用中央配置系统"""
    global HOST, PORT, DEBUG, MODEL_API_KEY, MODEL_NAME, TEMPERATURE, DB_PATH
    
    if config is not None:
        # 从中央配置系统加载
        erniebot_config = config.get_service_config("erniebot")
        
        # 服务基本配置
        HOST = erniebot_config.get("host", HOST)
        PORT = erniebot_config.get("port", PORT)
        DEBUG = erniebot_config.get("debug", DEBUG)
        
        # 模型配置
        model_config = erniebot_config.get("model", {})
        MODEL_API_KEY = model_config.get("api_key", MODEL_API_KEY)
        MODEL_NAME = model_config.get("model_name", MODEL_NAME)
        TEMPERATURE = model_config.get("temperature", TEMPERATURE)
        
        # 数据库配置
        db_config = erniebot_config.get("database", {})
        DB_PATH = db_config.get("path", DB_PATH)
        
        print(f"已从中央配置加载设置，服务运行在 {HOST}:{PORT}")
    else:
        # 回退到环境变量
        HOST = os.environ.get("ERNIEBOT_HOST", HOST)
        PORT = int(os.environ.get("ERNIEBOT_PORT", PORT))
        MODEL_API_KEY = os.environ.get("AI_API_KEY", MODEL_API_KEY)
        MODEL_NAME = os.environ.get("AI_MODEL_NAME", MODEL_NAME)
        DB_PATH = os.environ.get("DB_PATH", DB_PATH)
        
        print(f"使用本地配置，服务运行在 {HOST}:{PORT}")

# 在模块导入时加载配置
load_configuration()

# 产品成本配置加载在这里保持不变，可以在后续更新中集成到中央配置

#coding=utf-8
"""
配置模块 - 存储正山堂茶业模拟系统的常量和配置数据
"""

import os
import json
import yaml
from datetime import datetime

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")

def load_yaml_config(filename):
    """加载YAML配置文件"""
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        print(f"警告: 配置文件 {filepath} 不存在!")
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_json_config(filename):
    """加载JSON配置文件"""
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        print(f"警告: 配置文件 {filepath} 不存在!")
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载各类配置
constants_config = load_yaml_config("constants.yaml")
product_costs_config = load_yaml_config("product_costs.yaml")
product_pricing_config = load_yaml_config("product_pricing.yaml")  # 加载产品定价配置
consumer_psychological_traits_config = load_yaml_config("consumer_psychological_traits.yaml")
seasonal_preferences_config = load_yaml_config("seasonal_preferences.yaml")
comment_templates_config = load_yaml_config("comment_templates.yaml") 
consumer_types_config = load_json_config("consumer_types.json")

# AI API配置
API_KEY = constants_config.get('api', {}).get('key', "f0b94d12aa98c64426df53f87551a702fd2032c6")
BASE_URL = constants_config.get('api', {}).get('base_url', "https://aistudio.baidu.com/llm/lmapi/v3")
MODEL_NAME = constants_config.get('api', {}).get('model_name', "ernie-4.0-turbo-128k")
REQUEST_TIMEOUT = constants_config.get('api', {}).get('timeout', 30)  # 请求超时时间，单位秒
REQUEST_INTERVAL = constants_config.get('api', {}).get('interval', 3)  # 请求间隔时间，单位秒，避免访问过于频繁
MAX_RETRIES = constants_config.get('api', {}).get('max_retries', 3)  # 最大重试次数
RETRY_INTERVAL = constants_config.get('api', {}).get('retry_interval', 5)  # 重试间隔时间，单位秒，出错后应等待更久

# 新增高级API配置
CONNECT_TIMEOUT = constants_config.get('api', {}).get('connect_timeout', 15)  # 连接超时时间
READ_TIMEOUT = constants_config.get('api', {}).get('read_timeout', 90)  # 读取超时时间
WRITE_TIMEOUT = constants_config.get('api', {}).get('write_timeout', 30)  # 写入超时时间
MAX_RETRY_INTERVAL = constants_config.get('api', {}).get('max_retry_interval', 60)  # 最大重试间隔
RETRY_CODES = constants_config.get('api', {}).get('retry_codes', [408, 429, 500, 502, 503, 504])  # 重试状态码
CACHE_ENABLED = constants_config.get('api', {}).get('cache_enabled', True)  # 是否启用缓存
CACHE_TIME = constants_config.get('api', {}).get('cache_time', 3600)  # 缓存有效期

# 系统提示词
SYSTEM_PROMPT = """你是一个专为正山堂茶业打造的消费者行为模拟系统，需要模拟不同类型的茶叶消费者对正山堂推出的红茶新品的消费行为，包括是否进店、是否购买、消费金额等。\
        正山堂茶业背景：创立于福建武夷山，传承400余年红茶文化，是世界红茶始祖正山小种的发源地，也是高端红茶金骏眉的创始企业。2005年，江元勋先生率领团队创新研发出金骏眉，填补高端红茶市场空白。正山堂获得多项国际有机认证，参与制定国家红茶标准，专注于生态、高品质的红茶生产。\
        请基于以下几类典型正山堂消费者人物画像及其在市场中的实际占比，模拟他们的真实消费行为：\
        一、消费者类型及市场占比：\
           - 传统茶文化爱好者（25%）：年龄40-65岁，注重茶叶品质和传统工艺，消费能力高，偏好正统红茶，重视茶的文化内涵与品质溯源，平均消费200-800元\
           - 品质生活追求者（30%）：年龄30-45岁，追求高品质生活，愿意为正宗好茶付费，注重品牌调性和产品故事，消费能力高，平均消费150-500元\
           - 商务人士（20%）：年龄35-55岁，注重茶叶的商务送礼价值，关注品牌知名度和包装档次，消费能力高，倾向于购买礼盒装，平均消费300-1500元\
           - 健康生活主义者（15%）：年龄28-50岁，关注茶叶有机认证和健康功效，注重无污染和生态种植，消费能力中高，偏好有机认证产品，平均消费100-300元\
           - 年轻新贵（10%）：年龄25-35岁，新兴茶文化爱好者，通过社交媒体了解高端茶品，追求时尚与品位，愿意尝试新品，平均消费80-250元\
        请让20位模拟消费者的分布比例大致符合上述市场占比。具体人员分配为：\
           - 传统茶文化爱好者（25%）：刘一、陈二、刘一一、陈二二、李四四（5人）\
           - 品质生活追求者（30%）：张三、李四、王五、张三三、李四四、王五五（6人）\
           - 商务人士（20%）：赵六、孙七、赵六六、孙七七（4人）\
           - 健康生活主义者（15%）：周八、吴九、周八八（3人）\
           - 年轻新贵（10%）：郑十、吴九九、郑十十（2人）\
        二、每次交互时，消费者将在以下8个不同的场景中进行消费行为，各场景代表不同的消费行为特点：\
           - 茶艺体验区：模拟消费者参与茶艺表演和品鉴活动，重点关注茶的冲泡工艺和口感体验\
           - 产品展示区：模拟消费者浏览不同品类的正山堂红茶产品，了解产品特点和价格\
           - 文化传承区：模拟消费者了解正山堂400年红茶历史和文化底蕴，增强品牌认同\
           - 个人定制区：模拟消费者咨询并选择个人喜好的红茶品类、口味和包装\
           - 礼品专区：模拟消费者选购礼盒装及商务送礼产品，关注包装和品牌形象\
           - 有机认证区：模拟消费者了解正山堂的各项国际有机认证和生态种植理念\
           - 品牌故事区：模拟消费者了解金骏眉创始故事和正山堂品牌理念，增强情感连接\
           - 会员服务区：模拟消费者办理会员、积分兑换和售后咨询等活动\
        三、每位消费者需要有姓名、年龄、职业、消费习惯、消费能力等基本信息，姓名仅使用上述二十个固定名字\
        四、模拟消费行为需要涵盖：是否进店、浏览时间、是否购买、购买产品（如金骏眉、正山小种、骏眉红茶等正山堂产品）、消费金额、消费满意度、是否会再次光临、是否会推荐给他人等\
        五、每位消费者会有独立的行为模式和消费习惯，包括对价格的敏感度、口味偏好、服务要求等\
        六、每位消费者要有独立的访问历史记录，用于判断是首次访问还是回头客\
        七、每次交互时，你需要按以下JSON格式回复，使用```json```标记：\
        {\
            'store_name':'正山堂茶业体验店', // string，当前模拟的店铺名称\
            'day': n, // int，当前模拟的天数，从1开始，最多模拟30天\
            'business_hour': '营业时间段', // string，如'9:00-21:00'\
            'daily_stats': { // 当天的营业数据统计\
                'customer_flow': n, // int，当天客流量（进店人数）\
                'new_customers': n, // int，新客户数量（首次访问）\
                'returning_customers': n, // int，回头客数量\
                'conversion_rate': '消费转化率', // string，例如'75%'，表示进店后实际购买的比例\
                'total_sales': n, // int，当天销售总额（元）\
                'avg_expense': n, // int，人均消费（元）\
                'peak_hours': '高峰时段', // string，如'14:00-16:00'\
                'best_sellers': ['产品1', '产品2'], // array，当天最畅销的2-3款产品\
            },\
            'cumulative_stats': { // 累计营业数据统计（从第1天到当前）\
                'total_customers': n, // int，累计客流量\
                'unique_customers': n, // int，不同顾客总数\
                'loyal_customers': n, // int，多次光临的顾客数（2次及以上）\
                'total_revenue': n, // int，累计销售总额（元）\
                'customer_retention': '顾客留存率', // string，如'45%'，表示回头客占比\
                'avg_visits_per_customer': n, // float，平均每位顾客的访问次数\
            },\
            'customer_interactions':[\
                {\
                    'name':'姓名', // string，消费者姓名(使用上述二十个固定名字)\
                    'type':'消费者类型', // string，消费者类型(上述五种类型之一)\
                    'age': n, // int，消费者年龄\
                    'location':'场所', // string，消费者所在场景(必须是上述8个场所之一)\
                    'visit_count': n, // int，该消费者的访问次数（含当次，首次访问为1）\
                    'behavior': { // 消费行为详情\
                        'entered_store': true/false, // boolean，是否进入商店\
                        'browsed_minutes': n, // int，浏览/停留时间（分钟）\
                        'made_purchase': true/false, // boolean，是否购买\
                        'items_purchased': ['正山小种', '金骏眉'], // array，购买的产品（如未购买则为空数组）\
                        'amount_spent': n, // int，消费金额（元，未购买则为0）\
                        'satisfaction': n, // int，满意度评分（1-5分，未购买可为null）\
                        'will_return': true/false, // boolean，是否愿意再次光临\
                        'will_recommend': true/false, // boolean，是否愿意推荐给他人\
                    },\
                    'comments':'评价', // string，该消费者的具体评价或反馈\
                    'emoji':'表情 表情' // 两个emoji表情，分别代表消费体验和情绪\
                },\
                ...\
            ]\
        }\
        请确保每个日期的消费者分布在不同的场所中，并根据场所的特性设计符合场景的消费者行为。当我说'继续'，请模拟下一天的消费者行为。\
        模拟过程中要合理展现不同日期（工作日/周末）、不同时段、不同天气等因素对客流量和消费行为的影响。\
        每一天至少要展现7-10位不同消费者的行为，其中既有新客户也有回头客，比例要合理。\
        请注意：顾客数据要有连续性，即回头客的数据要与之前的访问保持一致性，并记录其历史访问次数。"""

# 产品成本和库存数据
PRODUCT_COSTS = product_costs_config

# 消费者类型和名称映射
CONSUMER_TYPES_MAPPING = consumer_types_config

# 消费者地域分布
CONSUMER_REGIONS = constants_config.get('consumer_regions', {})

# 消费者地域类型
CONSUMER_REGION_TYPES = constants_config.get('consumer_region_types', {})

# 消费者地域分布
CONSUMER_REGION_DISTRIBUTION = constants_config.get('consumer_region_distribution', {})

# 消费者心理特征配置
CONSUMER_PSYCHOLOGICAL_TRAITS = consumer_psychological_traits_config

# 有效的场所名称
VALID_LOCATIONS = constants_config.get('locations', ["茶艺体验区", "产品展示区", "文化传承区", "个人定制区", "礼品专区", "有机认证区", "品牌故事区", "会员服务区"])

# 表情符号列表
EMOJIS = constants_config.get('emojis', ["👍✨", "😊🍵", "🤔💭", "😄🫖", "🧐📊", "🌿👌", "❤️🍃", "💯🏆"])

# 文件路径相关
def get_file_path(filename):
    """获取绝对文件路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)

# 产品定义
def get_product_info():
    """获取产品信息，包括价格范围和分类"""
    result = {}
    
    # 从配置文件加载产品价格信息
    for product_name, product_data in product_pricing_config.items():
        # 确保产品数据包含必要的字段
        if 'price_range' in product_data and 'category' in product_data:
            price_range = tuple(product_data['price_range'])
            category = product_data['category']
            
            # 添加到结果字典中
            result[product_name] = {
                "price_range": price_range,
                "category": category
            }
            
            # 可选：添加描述字段
            if 'description' in product_data:
                result[product_name]["description"] = product_data['description']
    
    return result

# 有效的用户名列表
def get_valid_names():
    """获取所有有效的用户名列表"""
    names = []
    for type_names in CONSUMER_TYPES_MAPPING.values():
        names.extend(type_names)
    return names

# 消费者类型的年龄范围
AGE_RANGES = constants_config.get('age_ranges', {
    "传统茶文化爱好者": (40, 65),
    "品质生活追求者": (30, 45),
    "商务人士": (35, 55),
    "健康生活主义者": (28, 50),
    "年轻新贵": (18, 35)
})

# 评论模板
POSITIVE_COMMENTS = comment_templates_config.get('positive_comments', [])
NEUTRAL_COMMENTS = comment_templates_config.get('neutral_comments', [])
BROWSING_COMMENTS = comment_templates_config.get('browsing_comments', [])
ENVIRONMENT_COMMENTS = comment_templates_config.get('environment_comments', [])
SERVICE_COMMENTS = comment_templates_config.get('service_comments', [])
PROMOTION_COMMENTS = comment_templates_config.get('promotion_comments', [])
NEGATIVE_COMMENTS = comment_templates_config.get('negative_comments', [])
YOUNG_CONSUMER_COMMENTS = comment_templates_config.get('young_consumer_comments', [])

# 季节信息
SEASONS = seasonal_preferences_config.get('seasons', {})

# 季节性产品偏好
SEASONAL_PREFERENCES = seasonal_preferences_config.get('seasonal_preferences', {})

# 消费者群体季节性偏好
CONSUMER_SEASONAL_PREFERENCES = seasonal_preferences_config.get('consumer_seasonal_preferences', {})

# 模拟参数
BATCH_SIZE = constants_config.get('simulation', {}).get('batch_size', 3)  # 每批模拟的消费者数量
BATCH_COUNT = constants_config.get('simulation', {}).get('batch_count', 3)  # 分批数量
SIMPLIFIED_PROMPT = constants_config.get('simulation', {}).get('simplified_prompt', True)  # 使用简化提示词