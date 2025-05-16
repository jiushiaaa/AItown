#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
erniebot配置集成模块 - 集成所有配置
"""

import os
import sys
from pathlib import Path
import dotenv

# 加载.env文件
dotenv.load_dotenv()

# 以下是默认值，可通过环境变量覆盖
# Socket服务配置
HOST = os.environ.get("ERNIEBOT_HOST", "127.0.0.1")
PORT = int(os.environ.get("ERNIEBOT_PORT", "12339"))
DEBUG = os.environ.get("ERNIEBOT_DEBUG", "False").lower() == "true"

# 模型API配置
MODEL_API_KEY = os.environ.get("AI_API_KEY", "f0b94d12aa98c64426df53f87551a702fd2032c6")
MODEL_NAME = os.environ.get("AI_MODEL_NAME", "ernie-4.0-turbo-128k")
TEMPERATURE = float(os.environ.get("AI_TEMPERATURE", "0.7"))
BASE_URL = os.environ.get("AI_BASE_URL", "https://aistudio.baidu.com/llm/lmapi/v3")

# API重试与超时配置 - 增加重试次数和超时时间
REQUEST_TIMEOUT = int(os.environ.get("API_REQUEST_TIMEOUT", "60"))  # 从30秒增加到60秒
REQUEST_INTERVAL = float(os.environ.get("API_REQUEST_INTERVAL", "3.0"))
MAX_RETRIES = int(os.environ.get("API_MAX_RETRIES", "8"))  # 从5次增加到8次
RETRY_INTERVAL = float(os.environ.get("API_RETRY_INTERVAL", "8.0"))  # 从5秒增加到8秒
CONNECT_TIMEOUT = int(os.environ.get("API_CONNECT_TIMEOUT", "20"))  # 从15秒增加到20秒
READ_TIMEOUT = int(os.environ.get("API_READ_TIMEOUT", "120"))  # 从90秒增加到120秒
WRITE_TIMEOUT = int(os.environ.get("API_WRITE_TIMEOUT", "30"))
MAX_RETRY_INTERVAL = int(os.environ.get("API_MAX_RETRY_INTERVAL", "120"))  # 从60秒增加到120秒
RETRY_CODES = [408, 429, 500, 502, 503, 504]

# 缓存配置
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "True").lower() == "true"
CACHE_TIME = int(os.environ.get("CACHE_TIME", "3600"))

# 数据库配置
DB_PATH = os.environ.get("DB_PATH", "simulation_data.db")

# 模拟参数
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "3"))
BATCH_COUNT = int(os.environ.get("BATCH_COUNT", "3"))
SIMPLIFIED_PROMPT = os.environ.get("SIMPLIFIED_PROMPT", "True").lower() == "true"

# 系统提示词 - 来自模块中
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

# 调试API连接配置
print(f"配置加载完成: API_KEY={MODEL_API_KEY[:5]}***, BASE_URL={BASE_URL}, MODEL={MODEL_NAME}")

def configure_app(app):
    """配置Flask应用 (如果erniebot需要Flask的话)"""
    if not app:
        return None
        
    return {
        "host": HOST,
        "port": PORT,
        "debug": DEBUG
    }

# 打印配置信息
print(f"ErnieBot 配置加载完成. 服务运行在 {HOST}:{PORT}")
print(f"数据库路径: {DB_PATH}")
if not MODEL_API_KEY:
    print("警告: 未配置 AI_API_KEY. 请在 .env 文件或环境变量中设置.")