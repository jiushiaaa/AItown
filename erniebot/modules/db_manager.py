import sqlite3
import os
import json
from datetime import datetime, date

class DBManager:
    """数据库管理类，处理与数据库的所有交互"""
    
    def __init__(self, db_path=None):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 使用与脚本同目录的默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'simulation_data.db')
        
        self.db_path = db_path
        
        # 确保数据库文件所在目录存在
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # 初始化数据库
        self.init_database()
        
        # 确保数据库表结构兼容性
        self.ensure_table_compatibility()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建消费者表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumers (
            customer_id VARCHAR(50) PRIMARY KEY,
            first_visit_date DATE NOT NULL,
            customer_type VARCHAR(50) NOT NULL,
            is_new_customer BOOLEAN DEFAULT 1,
            visit_count INTEGER DEFAULT 1,
            last_visit_date DATE,
            total_amount DECIMAL(10,2) DEFAULT 0
        )
        ''')
        
        # 创建消费者行为表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumer_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id VARCHAR(50),
            timestamp TEXT NOT NULL,
            consumer_type VARCHAR(50) NOT NULL,
            region VARCHAR(50),
            city_type VARCHAR(50),
            visit_store BOOLEAN,
            browse_time INTEGER,
            purchase BOOLEAN,
            product_name VARCHAR(100),
            amount DECIMAL(10,2),
            psychological_trait TEXT,
            day_of_simulation INTEGER,
            is_new_visit BOOLEAN DEFAULT 0
        )
        ''')
        
        # 为 consumer_actions 表添加索引以提高查询效率
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_timestamp ON consumer_actions (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_customer_id ON consumer_actions (customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_purchase ON consumer_actions (purchase)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_region ON consumer_actions (region)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_consumer_type ON consumer_actions (consumer_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consumer_actions_product_name ON consumer_actions (product_name)')
        
        # 创建每日统计数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date DATE PRIMARY KEY,
            order_count INTEGER,
            gmv DECIMAL(12,2),
            user_count INTEGER,
            new_user_count INTEGER DEFAULT 0,
            returning_user_count INTEGER DEFAULT 0,
            avg_order_value DECIMAL(10,2),
            cancelled_order_count INTEGER,
            return_count INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def ensure_table_compatibility(self):
        """确保数据库表结构兼容性，添加缺失列"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查consumer_actions表是否存在customer_id列
            cursor.execute("PRAGMA table_info(consumer_actions)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # 如果没有customer_id列，添加它
            if 'customer_id' not in column_names:
                print("为consumer_actions表添加customer_id列")
                cursor.execute("ALTER TABLE consumer_actions ADD COLUMN customer_id VARCHAR(50)")
            
            # 如果没有is_new_visit列，添加它
            if 'is_new_visit' not in column_names:
                print("为consumer_actions表添加is_new_visit列")
                cursor.execute("ALTER TABLE consumer_actions ADD COLUMN is_new_visit BOOLEAN DEFAULT 0")
            
            # 检查daily_stats表是否存在新的列
            cursor.execute("PRAGMA table_info(daily_stats)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # 如果没有new_user_count列，添加它
            if 'new_user_count' not in column_names:
                print("为daily_stats表添加new_user_count列")
                cursor.execute("ALTER TABLE daily_stats ADD COLUMN new_user_count INTEGER DEFAULT 0")
            
            # 如果没有returning_user_count列，添加它
            if 'returning_user_count' not in column_names:
                print("为daily_stats表添加returning_user_count列")
                cursor.execute("ALTER TABLE daily_stats ADD COLUMN returning_user_count INTEGER DEFAULT 0")
            
            conn.commit()
            print("数据库表结构兼容性检查完成")
        except Exception as e:
            print(f"确保表兼容性时出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_simulation_data(self, simulation_data, day):
        """保存模拟数据到数据库
        
        Args:
            simulation_data: 模拟生成的消费者行为数据
            day: 模拟的天数
        """
        if not simulation_data:
            print(f"警告: 第{day}天的模拟数据为空，跳过保存")
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            print(f"=== 开始保存第{day}天的模拟数据 ===")
            print(f"数据库路径: {self.db_path}")
            
            # 提取当前日期
            current_date = date.today().isoformat()
            print(f"当前日期: {current_date}")
            
            # 统计变量
            order_count = 0
            total_gmv = 0
            unique_users = set()
            cancelled_orders = 0
            return_count = 0
            
            # 获取消费者数据
            consumers = simulation_data.get("consumers", [])
            if not consumers and "customer_interactions" in simulation_data:
                # 尝试从不同的键名获取数据
                consumers = simulation_data.get("customer_interactions", [])
            
            print(f"消费者记录数: {len(consumers)}")
            
            # 记录每条消费者行为
            for i, consumer in enumerate(consumers):
                try:
                    # 确保consumer_id存在
                    customer_id = consumer.get("id", f"auto_id_{i}")
                    
                    consumer_type = consumer.get("consumer_type", consumer.get("type", "未知"))
                    
                    # 更新consumers表
                    try:
                        # 检查用户是否已存在
                        cursor.execute("SELECT * FROM consumers WHERE customer_id = ?", (customer_id,))
                        existing_user = cursor.fetchone()
                        
                        if existing_user:
                            # 更新现有用户
                            cursor.execute("""
                            UPDATE consumers SET 
                            last_visit_date = ?, 
                            visit_count = visit_count + 1,
                            is_new_customer = 0
                            WHERE customer_id = ?
                            """, (current_date, customer_id))
                            is_new_visit = False
                        else:
                            # 创建新用户
                            cursor.execute("""
                            INSERT INTO consumers 
                            (customer_id, first_visit_date, customer_type, is_new_customer, visit_count, last_visit_date)
                            VALUES (?, ?, ?, 1, 1, ?)
                            """, (customer_id, current_date, consumer_type, current_date))
                            is_new_visit = True
                    except Exception as e:
                        print(f"更新customers表时出错: {e}")
                        is_new_visit = False  # 默认为非新访问
                    
                    # 提取地域信息
                    region_data = consumer.get("region", {})
                    region = None
                    city_type = None
                    city = None  # 添加城市变量
                    province = None  # 添加省份变量
                    
                    if isinstance(region_data, dict):
                        region = region_data.get("area", region_data.get("地区", "未知"))
                        city_type = region_data.get("city_type", region_data.get("城市类型", "未知"))
                        city = region_data.get("city", region_data.get("城市", "未知"))  # 获取城市名称
                        
                        # 根据地区和城市映射省份（对应到中国地图）
                        province = self.get_province_by_region_city(region, city)
                    else:
                        region = consumer.get("region", "未知")
                        city_type = consumer.get("city_type", "未知")
                        city = consumer.get("city", "未知")
                        province = self.get_province_by_region_city(region, city)
                    
                    # 将省份信息添加到region字段，格式：原区域名称-省份，例如：华东-上海
                    if province and province != "未知":
                        region = f"{region}-{province}"
                    
                    # 首先优先从behavior字段获取访问和购买信息
                    behavior = consumer.get("behavior", {})
                    if isinstance(behavior, dict):
                        visit_store = behavior.get("entered_store", False)
                        browse_time = behavior.get("browsed_minutes", 0)
                        purchase = behavior.get("made_purchase", False)
                        
                        # 获取购买产品和金额
                        items_purchased = behavior.get("items_purchased", [])
                        product_name = items_purchased[0] if items_purchased and len(items_purchased) > 0 else ""
                        amount = behavior.get("amount_spent", 0.0)
                    else:
                        # 如果没有behavior字段，尝试从顶级字段获取
                        visit_store = consumer.get("visit_store", False)
                        browse_time = consumer.get("browse_time", 0)
                        purchase = consumer.get("purchase", False)
                        product_name = consumer.get("product_name", consumer.get("product", ""))
                        amount = consumer.get("amount", 0.0)
                    
                    # 确保布尔值正确转换
                    visit_store = bool(visit_store)
                    purchase = bool(purchase)
                    
                    # 修复：强制将有金额的记录设为已购买和已访问
                    if amount and float(amount) > 0:
                        purchase = True
                        visit_store = True
                        
                        # 如果产品名为空但有金额，设置一个默认产品
                        if not product_name:
                            product_name = "未指定产品"
                    
                    # 处理心理特征
                    psych_traits = consumer.get("psychological_trait", {})
                    if not psych_traits and "psychological_traits" in consumer:
                        psych_traits = consumer.get("psychological_traits", {})
                    elif not psych_traits and "consumer_traits" in consumer:
                        psych_traits = consumer.get("consumer_traits", {})
                    
                    # 如果是字符串，尝试解析为字典
                    if isinstance(psych_traits, str):
                        try:
                            psych_traits = json.loads(psych_traits)
                        except:
                            psych_traits = {"未解析特征": psych_traits}
                    
                    # 将心理特征转为JSON字符串
                    psych_traits_json = json.dumps(psych_traits, ensure_ascii=False)
                    
                    # 获取timestamp，将day格式用作日期
                    day_num = consumer.get("day", day) or day
                    timestamp = f"Day{day_num}"
                    
                    print(f"处理第{i+1}条消费者记录: 类型={consumer_type}, 区域={region}, 城市类型={city_type}, 访问={visit_store}, 购买={purchase}, 产品={product_name}, 金额={amount}")
                    
                    # 插入消费者行为记录
                    cursor.execute('''
                    INSERT INTO consumer_actions 
                    (customer_id, timestamp, consumer_type, region, city_type, visit_store, 
                    browse_time, purchase, product_name, amount, psychological_trait, day_of_simulation, is_new_visit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        customer_id,
                        timestamp, 
                        consumer_type, 
                        region, 
                        city_type, 
                        1 if visit_store else 0, 
                        browse_time, 
                        1 if purchase else 0, 
                        product_name, 
                        float(amount) if amount is not None else 0.0, 
                        psych_traits_json,
                        day,
                        1 if is_new_visit else 0
                    ))
                    
                    # 更新统计数据
                    if purchase:
                        order_count += 1
                        total_gmv += float(amount) if amount is not None else 0.0
                        unique_users.add(customer_id)
                    
                    if consumer.get("cancelled", False):
                        cancelled_orders += 1
                    
                    if consumer.get("return", False):
                        return_count += 1
                    
                except Exception as e:
                    print(f"处理消费者记录时出错: {e}")
                    continue  # 跳过此条记录，继续处理下一条
            
            # 计算平均订单价值
            avg_order_value = 0
            if order_count > 0:
                avg_order_value = total_gmv / order_count
            
            # 保存每日统计数据
            print(f"统计结果: 订单数={order_count}, 总GMV={total_gmv}, 用户数={len(unique_users)}, 平均订单价值={avg_order_value}")
            
            # 计算新用户和回访用户数量
            try:
                cursor.execute("SELECT COUNT(*) FROM consumers WHERE is_new_customer = 1")
                new_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM consumers WHERE is_new_customer = 0")
                returning_users = cursor.fetchone()[0]
            except Exception as e:
                print(f"获取新用户和回访用户数量时出错: {e}")
                new_users = 0
                returning_users = 0
            
            # 插入或更新日常统计
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, order_count, gmv, user_count, new_user_count, returning_user_count, avg_order_value, cancelled_order_count, return_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    current_date, 
                    order_count, 
                    total_gmv, 
                    len(unique_users),
                    new_users,
                    returning_users,
                    avg_order_value, 
                    cancelled_orders, 
                    return_count
                ))
            except Exception as e:
                print(f"保存每日统计数据时出错: {e}")
            
            # 提交所有更改
            conn.commit()
            print("数据已提交到数据库")
            print(f"=== 成功保存第{day}天的模拟数据，共{len(consumers)}条消费者记录 ===")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"保存数据时出错: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_province_by_region_city(self, region, city):
        """
        根据地区和城市名称返回对应的省份名称
        
        Args:
            region: 地区名称，如：华东、华南、华北等
            city: 城市名称，如：上海、广州、北京等
            
        Returns:
            province: 省份名称，用于中国地图显示
        """
        # 城市到省份的映射
        city_to_province = {
            # 直辖市
            "北京": "北京市",
            "上海": "上海市",
            "天津": "天津市",
            "重庆": "重庆市",
            
            # 华东地区
            "杭州": "浙江省",
            "宁波": "浙江省",
            "温州": "浙江省",
            "南京": "江苏省",
            "苏州": "江苏省",
            "无锡": "江苏省",
            "常州": "江苏省",
            "济南": "山东省",
            "青岛": "山东省",
            "烟台": "山东省",
            "合肥": "安徽省",
            "福州": "福建省",
            "厦门": "福建省",
            "泉州": "福建省",
            
            # 华南地区
            "广州": "广东省",
            "深圳": "广东省",
            "东莞": "广东省",
            "佛山": "广东省",
            "珠海": "广东省",
            "南宁": "广西壮族自治区",
            "桂林": "广西壮族自治区",
            "海口": "海南省",
            "三亚": "海南省",
            
            # 华中地区
            "武汉": "湖北省",
            "长沙": "湖南省",
            "郑州": "河南省",
            "南昌": "江西省",
            
            # 华北地区
            "石家庄": "河北省",
            "太原": "山西省",
            "呼和浩特": "内蒙古自治区",
            
            # 西南地区
            "成都": "四川省",
            "绵阳": "四川省",
            "贵阳": "贵州省",
            "昆明": "云南省",
            "拉萨": "西藏自治区",
            
            # 西北地区
            "西安": "陕西省",
            "兰州": "甘肃省",
            "西宁": "青海省",
            "银川": "宁夏回族自治区",
            "乌鲁木齐": "新疆维吾尔自治区",
            
            # 东北地区
            "哈尔滨": "黑龙江省",
            "长春": "吉林省",
            "沈阳": "辽宁省",
            "大连": "辽宁省"
        }
        
        # 地区到默认省份的映射（当城市未知或不在映射表中时使用）
        region_to_default_province = {
            "华东": "上海市",
            "华南": "广东省",
            "华北": "北京市",
            "华中": "湖北省",
            "西南": "四川省", 
            "西北": "陕西省",
            "东北": "辽宁省",
            "港澳台": "香港特别行政区"
        }
        
        # 首先尝试通过城市名称获取省份
        if city and city != "未知" and city in city_to_province:
            return city_to_province[city]
        
        # 如果城市未知或不在映射表中，使用地区的默认省份
        if region and region != "未知" and region in region_to_default_province:
            return region_to_default_province[region]
        
        # 如果都没有匹配，返回未知
        return "未知"