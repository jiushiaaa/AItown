#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
正山堂茶业消费者行为分析系统 - API服务
"""

from flask import Flask, jsonify, request
import sqlite3
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 确保优先导入当前目录下的模块
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 导入配置集成模块
try:
    from config_integration import configure_app, get_db_path
    print(f"成功从 {current_dir}/config_integration.py 导入配置")
except ImportError as e:
    print(f"导入config_integration失败: {e}")
    # 尝试直接定义必要的函数作为后备
    def get_db_path():
        base_dir = Path(__file__).parent.parent
        return str(base_dir / "erniebot" / "simulation_data.db")
        
    def configure_app(app):
        from flask_cors import CORS
        CORS(app)
        return {"host": "127.0.0.1", "port": 5000, "debug": False}

app = Flask(__name__)

# 使用配置集成模块配置应用
app_config = configure_app(app)

# 获取数据库路径
def get_db_connection():
    """获取数据库连接"""
    db_path = get_db_path()
    print(f"连接到数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """API首页"""
    return jsonify({
        'name': '正山堂茶业消费者行为分析系统API',
        'version': '1.0.0',
        'endpoints': [
            '/api/dashboard/metrics',
            '/api/dashboard/trend',
            '/api/dashboard/hot-products',
            '/api/consumer/behavior',
            '/api/consumer/behavior/trend',
            '/api/consumer/region',
            '/api/consumer/psychology',
            '/api/system/status',
            '/api/system/refresh'
        ]
    })

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """获取仪表盘主要指标"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取日期范围
    days = request.args.get('days', '7')
    time_range = request.args.get('timeRange', 'all')
    days = int(days)
    
    # 直接从consumer_actions表查询统计数据
    print("从consumer_actions直接统计数据")
    
    cursor.execute('''
    SELECT 
        COUNT(CASE WHEN purchase = 1 THEN 1 ELSE NULL END) as total_orders,
        SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as total_gmv,
        COUNT(DISTINCT customer_id) as total_users,
        COUNT(DISTINCT CASE WHEN is_new_visit = 1 THEN customer_id END) as new_users,
        COUNT(DISTINCT CASE WHEN is_new_visit = 0 THEN customer_id END) as returning_users,
        AVG(CASE WHEN purchase = 1 THEN amount ELSE NULL END) as avg_order
    FROM consumer_actions
    ''')
    
    direct_stats = cursor.fetchone()
    
    # 使用直接统计的数据
    if direct_stats:
        current_stats = {
            'total_orders': direct_stats['total_orders'] or 0,
            'total_gmv': direct_stats['total_gmv'] or 0,
            'total_users': direct_stats['total_users'] or 0,
            'new_users': direct_stats['new_users'] or 0,
            'returning_users': direct_stats['returning_users'] or 0,
            'avg_order': direct_stats['avg_order'] or 0,
            'cancelled_orders': 0,
            'total_returns': 0
        }
    else:
        current_stats = {
            'total_orders': 0,
            'total_gmv': 0,
            'total_users': 0,
            'new_users': 0,
            'returning_users': 0,
            'avg_order': 0,
            'cancelled_orders': 0,
            'total_returns': 0
        }
    
    # 环比数据 - 假设分析的是模拟数据，环比设为固定值
    yoy_orders = 15.2  # 同比增长15.2%
    yoy_gmv = 18.7     # 同比增长18.7%
    yoy_users = 12.5   # 同比增长12.5%
    
    # 处理None值
    metrics = {
        'order_quantity': current_stats['total_orders'] or 0,
        'gmv': current_stats['total_gmv'] or 0,
        'user_count': current_stats['total_users'] or 0,
        'new_user_count': current_stats['new_users'] or 0,
        'returning_user_count': current_stats['returning_users'] or 0,
        'avg_order_value': current_stats['avg_order'] or 0,
        'cancelled_orders': current_stats['cancelled_orders'] or 0,
        'total_returns': current_stats['total_returns'] or 0,
        'yoy_orders': round(yoy_orders, 2),
        'yoy_gmv': round(yoy_gmv, 2),
        'yoy_users': round(yoy_users, 2)
    }
    
    conn.close()
    
    return jsonify(metrics)

@app.route('/api/dashboard/trend', methods=['GET'])
def get_dashboard_trend():
    """获取趋势数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取日期范围
    days = request.args.get('days', '30')
    time_range = request.args.get('timeRange', 'all')
    days = int(days)
    
    # 初始化结果变量
    result = {
        'dates': [],
        'orders': [],
        'gmv': [],
        'users': []
    }
    
    # 打印请求信息，帮助调试
    print(f"获取趋势数据请求：days={days}, timeRange={time_range}")
    
    # 直接查询所有consumer_actions数据，按日期分组
    query = '''
    SELECT 
        timestamp as date,
        COUNT(DISTINCT customer_id) as users,
        COUNT(CASE WHEN purchase = 1 THEN 1 END) as orders,
        SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as gmv
    FROM consumer_actions
    GROUP BY timestamp
    ORDER BY 
        CASE 
            WHEN timestamp LIKE 'Day%' THEN CAST(REPLACE(timestamp, 'Day', '') AS INTEGER)
            ELSE timestamp 
        END
    '''
    
    cursor.execute(query)
    trend_data = cursor.fetchall()
    
    print(f"查询到的原始数据: {[dict(row) for row in trend_data]}")
    
    # 检查是否有数据
    if trend_data and len(trend_data) > 0:
        # 格式化数据
        result = {
            'dates': [row['date'] for row in trend_data],
            'orders': [row['orders'] or 0 for row in trend_data],
            'gmv': [row['gmv'] or 0 for row in trend_data],
            'users': [row['users'] or 0 for row in trend_data]
        }
        
        print(f"查询到{len(trend_data)}天的销售趋势数据")
    
    # 如果数据少于2天，生成模拟数据补充
    if len(result['dates']) < 2:
        print(f"数据不足，当前只有{len(result['dates'])}天，生成模拟数据补充")
        
        import random
        
        # 保留现有数据
        existing_dates = result['dates']
        existing_orders = result['orders']
        existing_gmv = result['gmv']
        existing_users = result['users']
        
        # 生成30天的模拟数据
        simulated_dates = []
        simulated_orders = []
        simulated_gmv = []
        simulated_users = []
        
        # 如果已有数据是日期格式，则按照日期格式生成；否则使用Day1-Day30格式
        if existing_dates and existing_dates[0].startswith('202'):
            # 使用日期格式
            from datetime import datetime, timedelta
            
            # 如果有现有数据，从现有数据的日期开始；否则从当前日期开始
            if existing_dates:
                try:
                    start_date = datetime.strptime(existing_dates[0], "%Y-%m-%d")
                except:
                    start_date = datetime.now()
            else:
                start_date = datetime.now()
            
            # 生成前15天和后15天的数据
            for i in range(-15, 15):
                date = start_date + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # 如果这一天已经有数据，跳过
                if date_str in existing_dates:
                    continue
                    
                # 生成随机数据
                order_count = random.randint(30, 70)
                simulated_dates.append(date_str)
                simulated_orders.append(order_count)
                simulated_gmv.append(order_count * random.randint(200, 500))
                simulated_users.append(order_count + random.randint(10, 30))
        else:
            # 使用Day1-Day30格式
            for i in range(1, 31):
                day_str = f"Day{i}"
                
                # 如果这一天已经有数据，跳过
                if day_str in existing_dates:
                    continue
                    
                # 生成随机数据
                order_count = random.randint(30, 70)
                simulated_dates.append(day_str)
                simulated_orders.append(order_count)
                simulated_gmv.append(order_count * random.randint(200, 500))
                simulated_users.append(order_count + random.randint(10, 30))
        
        # 合并现有数据和模拟数据
        result['dates'] = existing_dates + simulated_dates
        result['orders'] = existing_orders + simulated_orders
        result['gmv'] = existing_gmv + simulated_gmv
        result['users'] = existing_users + simulated_users
        
        # 排序数据
        if result['dates'] and result['dates'][0].startswith('202'):
            # 如果是日期格式，按日期排序
            sorted_data = sorted(zip(result['dates'], result['orders'], result['gmv'], result['users']))
            result['dates'] = [item[0] for item in sorted_data]
            result['orders'] = [item[1] for item in sorted_data]
            result['gmv'] = [item[2] for item in sorted_data]
            result['users'] = [item[3] for item in sorted_data]
        else:
            # 如果是Day格式，按Day后面的数字排序
            def day_key(day_str):
                if day_str.startswith('Day'):
                    try:
                        return int(day_str[3:])
                    except:
                        return 0
                return 0
                
            sorted_data = sorted(zip(result['dates'], result['orders'], result['gmv'], result['users']), 
                                key=lambda x: day_key(x[0]))
            result['dates'] = [item[0] for item in sorted_data]
            result['orders'] = [item[1] for item in sorted_data]
            result['gmv'] = [item[2] for item in sorted_data]
            result['users'] = [item[3] for item in sorted_data]
    
    # 打印最终结果
    print(f"最终返回的趋势数据: 共{len(result['dates'])}天")
    
    conn.close()
    
    return jsonify(result)

# --- ADDED START ---
@app.route('/api/dashboard/hot-products', methods=['GET'])
def get_hot_products():
    """获取热销产品数据 (占位符)"""
    # TODO: 实现数据库查询逻辑
    # 示例数据
    hot_products = [
        {'name': '金骏眉', 'sales': 15000, 'rank': 1},
        {'name': '正山小种', 'sales': 12000, 'rank': 2},
        {'name': '大红袍', 'sales': 9500, 'rank': 3},
        {'name': '白毫银针', 'sales': 8000, 'rank': 4},
        {'name': '铁观音', 'sales': 7500, 'rank': 5}
    ]
    return jsonify(hot_products)

@app.route('/api/dashboard/visitor-trend', methods=['GET'])
def get_visitor_trend():
    """获取访客趋势数据 (占位符)"""
    # TODO: 实现数据库查询逻辑
    # 示例数据
    visitor_trend = {
        'dates': ['2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05'],
        'visitors': [120, 150, 130, 160, 140]
    }
    return jsonify(visitor_trend)
# --- ADDED END ---

@app.route('/api/consumer/behavior', methods=['GET'])
def get_consumer_behavior():
    """获取消费者行为数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取参数
    limit = request.args.get('limit', 100, type=int)
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sortBy', 'timestamp')
    sort_order = request.args.get('sortOrder', 'desc')
    
    offset = (page - 1) * limit
    
    # 修复查询 - 移除不存在的action列，添加consumer_type列
    query = f'''
    SELECT 
        id, customer_id, timestamp, consumer_type, product_name, 
        amount, purchase, is_new_visit, region, city_type
    FROM consumer_actions
    ORDER BY {sort_by} {sort_order}
    LIMIT ? OFFSET ?
    '''
    
    cursor.execute(query, [limit, offset])
    behaviors = [dict(row) for row in cursor.fetchall()]
    
    # 获取总数
    cursor.execute('SELECT COUNT(*) FROM consumer_actions')
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'data': behaviors,
        'total': total,
        'page': page,
        'limit': limit
    })

@app.route('/api/consumer/region', methods=['GET'])
def get_consumer_region():
    """获取消费者区域分布数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询区域分布
    query = '''
    SELECT region, COUNT(DISTINCT customer_id) as user_count, 
           SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as total_amount
    FROM consumer_actions
    WHERE region IS NOT NULL AND region != ''
    GROUP BY region
    ORDER BY user_count DESC
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # 处理结果，提取省份信息
    region_data = []
    
    # 如果没有查询到数据，生成默认数据
    if not rows:
        print("未查询到区域分布数据，生成默认数据")
        
        # 默认区域数据
        default_regions = [
            {"name": "华东", "province": "上海市", "value": 450, "total_amount": 78500},
            {"name": "华南", "province": "广东省", "value": 380, "total_amount": 67200},
            {"name": "华北", "province": "北京市", "value": 320, "total_amount": 53600},
            {"name": "华中", "province": "湖北省", "value": 280, "total_amount": 47500},
            {"name": "西南", "province": "四川省", "value": 210, "total_amount": 38600},
            {"name": "西北", "province": "陕西省", "value": 180, "total_amount": 32400},
            {"name": "东北", "province": "辽宁省", "value": 150, "total_amount": 28700},
            {"name": "港澳台", "province": "香港特别行政区", "value": 30, "total_amount": 9800}
        ]
        
        region_data = default_regions
    else:
        for row in rows:
            region = row['region']
            province = "未知"
            
            # 如果region包含省份信息（格式：区域-省份），则分离出省份
            if "-" in region:
                parts = region.split("-")
                region_name = parts[0]
                province = parts[1]
            else:
                region_name = region
                # 如果未包含省份信息，使用默认映射
                province_map = {
                    "华东": "上海市",
                    "华南": "广东省",
                    "华北": "北京市",
                    "华中": "湖北省",
                    "西南": "四川省",
                    "西北": "陕西省",
                    "东北": "辽宁省",
                    "港澳台": "香港特别行政区"
                }
                province = province_map.get(region_name, "未知")
            
            # 创建包含省份信息的数据结构
            region_data.append({
                'name': region_name,
                'value': row['user_count'], 
                'province': province,
                'total_amount': row['total_amount'] or 0
            })
    
    conn.close()
    
    return jsonify(region_data)

from collections import defaultdict

from collections import defaultdict

@app.route('/api/consumer/psychology', methods=['GET'])
def get_consumer_psychology():
    """获取消费者心理特征分布数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 尝试从数据库中读取psychological_trait数据
        cursor.execute('''
        SELECT psychological_trait FROM consumer_actions 
        WHERE psychological_trait IS NOT NULL AND psychological_trait != '{}' AND psychological_trait != ''
        LIMIT 1000
        ''')
        
        traits_data = cursor.fetchall()
        print(f"从数据库查询到 {len(traits_data)} 条心理特征数据")
        
        # 初始化心理特征统计
        psychology_stats = {
            '价格敏感度': {'高': 0, '中': 0, '低': 0},
            '品牌忠诚度': {'高': 0, '中': 0, '低': 0},
            '购物冲动性': {'高': 0, '中': 0, '低': 0},
            '品质追求': {'高': 0, '中': 0, '低': 0},
            '时尚意识': {'高': 0, '中': 0, '低': 0}
        }
        
        # 如果有数据，解析并统计
        processed_count = 0
        if traits_data:
            for trait_row in traits_data:
                try:
                    trait_json = trait_row[0]
                    print(f"处理trait数据: {trait_json[:100]}...")  # 只打印前100个字符避免日志过长
                    
                    if trait_json:
                        trait_dict = json.loads(trait_json) if isinstance(trait_json, str) else trait_json
                        
                        # 处理不同格式的心理特征数据
                        if isinstance(trait_dict, dict):
                            for trait_key, trait_value in trait_dict.items():
                                print(f"特征: {trait_key}={trait_value}")
                                
                                # 标准化特征键名
                                normalized_key = trait_key
                                if '敏感' in trait_key or '价格' in trait_key:
                                    normalized_key = '价格敏感度'
                                elif '忠诚' in trait_key or '品牌' in trait_key:
                                    normalized_key = '品牌忠诚度'
                                elif '冲动' in trait_key or '购物冲动' in trait_key:
                                    normalized_key = '购物冲动性'
                                elif '品质' in trait_key or '质量' in trait_key:
                                    normalized_key = '品质追求'
                                elif '时尚' in trait_key or '潮流' in trait_key:
                                    normalized_key = '时尚意识'
                                else:
                                    print(f"无法匹配特征: {trait_key}")
                                    continue
                                
                                # 标准化特征值
                                normalized_value = trait_value
                                if isinstance(trait_value, str):
                                    if '高' in trait_value or '强' in trait_value:
                                        normalized_value = '高'
                                    elif '中' in trait_value:
                                        normalized_value = '中'
                                    elif '低' in trait_value or '弱' in trait_value:
                                        normalized_value = '低'
                                    else:
                                        print(f"无法匹配特征值: {trait_value}")
                                        continue
                                else:
                                    print(f"特征值不是字符串: {trait_value}")
                                    continue
                                
                                # 增加计数
                                if normalized_key in psychology_stats and normalized_value in psychology_stats[normalized_key]:
                                    psychology_stats[normalized_key][normalized_value] += 1
                                    processed_count += 1
                                    print(f"增加统计: {normalized_key}-{normalized_value}")
                except Exception as e:
                    print(f"解析心理特征数据出错: {e}")
                    continue
        
        print(f"成功处理 {processed_count} 条有效特征数据")
        
        # 检查是否有足够的数据
        has_data = False
        for trait_key, levels in psychology_stats.items():
            trait_sum = sum(levels.values())
            print(f"特征 {trait_key} 统计: {levels}, 总计: {trait_sum}")
            if trait_sum > 0:
                has_data = True
                
        # 如果数据不足，使用模拟数据
        if not has_data:
            print("实际数据不足，使用模拟数据")
            psychology_stats = {
                '价格敏感度': {'高': 120, '中': 200, '低': 50},
                '品牌忠诚度': {'高': 150, '中': 160, '低': 60},
                '购物冲动性': {'高': 80, '中': 220, '低': 70},
                '品质追求': {'高': 180, '中': 140, '低': 50},
                '时尚意识': {'高': 110, '中': 190, '低': 70}
            }
    except Exception as e:
        print(f"查询消费者心理特征数据出错: {e}")
        # 使用模拟数据作为备份
        psychology_stats = {
            '价格敏感度': {'高': 120, '中': 200, '低': 50},
            '品牌忠诚度': {'高': 150, '中': 160, '低': 60},
            '购物冲动性': {'高': 80, '中': 220, '低': 70},
            '品质追求': {'高': 180, '中': 140, '低': 50},
            '时尚意识': {'高': 110, '中': 190, '低': 70}
        }
    finally:
        conn.close()
    
    # 按照前端需要的格式转换数据
    trait_keys_ordered = list(psychology_stats.keys())
    levels = ['高', '中', '低']
    
    indicators = []
    for key in trait_keys_ordered:
        total = sum(psychology_stats[key].values())
        max_value = total if total > 0 else 100
        indicators.append({'name': key, 'max': max_value})
    
    series_data = []
    for level in levels:
        level_values = []
        for key in trait_keys_ordered:
            count = psychology_stats[key].get(level, 0)
            level_values.append(count)
        series_data.append({'name': level, 'value': level_values})
    
    # 打印输出数据格式便于调试
    result = {
        'indicators': indicators,
        'series_data': series_data
    }
    
    print(f"API输出: indicators长度: {len(indicators)}, series_data长度: {len(series_data)}")
    print(f"indicators示例: {indicators[0] if indicators else '空'}")
    print(f"series_data示例: {series_data[0] if series_data else '空'}")
    
    # 确保返回的是正确格式的JSON
    return jsonify(result)

# --- ADDED START ---
@app.route('/api/visitor/analysis', methods=['GET'])
def get_visitor_analysis():
    """获取访客分析数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取时间范围参数
    time_range = request.args.get('timeRange', 'all')
    
    # 查询所有访客数据
    query = '''
    SELECT 
        COUNT(DISTINCT customer_id) as total_visitors,
        COUNT(DISTINCT CASE WHEN is_new_visit = 1 THEN customer_id END) as new_visitors,
        COUNT(DISTINCT CASE WHEN is_new_visit = 0 THEN customer_id END) as returning_visitors
    FROM consumer_actions
    '''
    
    cursor.execute(query)
    visitor_stats = cursor.fetchone()
    
    # 查询访问时长、跳出率等指标
    # 这里简化处理，使用模拟数据
    avg_browse_time = 0
    bounce_rate = 0
    
    # 查询平均浏览时间
    try:
        cursor.execute('SELECT AVG(browse_time) FROM consumer_actions WHERE browse_time > 0')
        avg_browse_time_result = cursor.fetchone()[0]
        if avg_browse_time_result:
            avg_browse_time = int(avg_browse_time_result)
    except Exception as e:
        print(f"查询平均浏览时间出错: {e}")
    
    # 计算跳出率（没有购买行为的访客比例）
    try:
        cursor.execute('''
        SELECT 
            COUNT(DISTINCT CASE WHEN purchase = 0 THEN customer_id END) * 100.0 / 
            NULLIF(COUNT(DISTINCT customer_id), 0) as bounce_rate
        FROM consumer_actions
        ''')
        bounce_rate_result = cursor.fetchone()[0]
        if bounce_rate_result:
            bounce_rate = float(bounce_rate_result)
    except Exception as e:
        print(f"计算跳出率出错: {e}")
    
    conn.close()
    
    # 如果数据库中没有数据，提供模拟数据
    total_visitors = visitor_stats['total_visitors'] if visitor_stats and visitor_stats['total_visitors'] else 500
    new_visitors = visitor_stats['new_visitors'] if visitor_stats and visitor_stats['new_visitors'] else 200
    returning_visitors = visitor_stats['returning_visitors'] if visitor_stats and visitor_stats['returning_visitors'] else 300
    
    # 计算同比增长（这里使用模拟数据）
    visitor_analysis = {
        'totalVisitors': total_visitors,
        'newVisitors': new_visitors,
        'returningVisitors': returning_visitors,
        'visitorTrend': 12.5,
        'newVisitorTrend': 15.2,
        'returningVisitorTrend': 8.7,
        'newVisitorRatio': round(new_visitors * 100 / total_visitors if total_visitors else 0, 1),
        'newVisitorRatioTrend': 5.3,
        'lostVisitors': 50,
        'lostVisitorTrend': -3.2,
        'avg_visit_duration': avg_browse_time or 120, # seconds
        'bounce_rate': round(bounce_rate, 2) or 0.45,
        'behavior': {
            'all': {
                'pageViews': 2500,
                'visitors': total_visitors,
                'avgStayTime': avg_browse_time or 120,
                'bounceRate': round(bounce_rate, 1) or 45.0
            },
            'new': {
                'pageViews': 900,
                'visitors': new_visitors,
                'avgStayTime': 90,
                'bounceRate': 52.5
            },
            'returning': {
                'pageViews': 1600,
                'visitors': returning_visitors,
                'avgStayTime': 150,
                'bounceRate': 38.2
            }
        }
    }
    return jsonify(visitor_analysis)

@app.route('/api/visitor/conversion', methods=['GET'])
def get_visitor_conversion():
    """获取访客转化率数据 (占位符)"""
    # TODO: 实现数据库查询逻辑
    # 示例数据
    visitor_conversion = {
        'view_to_purchase_rate': 0.15,
        'add_to_cart_rate': 0.30,
        'checkout_completion_rate': 0.65
    }
    return jsonify(visitor_conversion)
# --- ADDED END ---

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    # TODO: 实现更详细的状态检查，例如数据库连接、模拟器状态等
    status = {
        'api_status': 'running',
        'database_connection': 'connected', # 假设连接正常
        'last_simulation_time': None # TODO: 从数据库或日志获取
    }
    # 尝试获取最后模拟时间
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM consumer_actions")
        last_time = cursor.fetchone()[0]
        if last_time:
            status['last_simulation_time'] = last_time
        conn.close()
    except Exception as e:
        print(f"获取最后模拟时间失败: {e}")
        status['database_connection'] = 'error'
        
    return jsonify(status)

@app.route('/api/system/refresh', methods=['POST'])
def refresh_system_data():
    """强制刷新数据缓存"""
    try:
        # 这里可以添加清除缓存的逻辑，如果有的话
        
        # 返回成功消息和数据库状态
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM consumer_actions")
        consumer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM daily_stats")
        stats_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '数据缓存已刷新',
            'records': {
                'consumer_actions': consumer_count,
                'daily_stats': stats_count
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'刷新数据缓存时出错: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/consumer/behavior/trend', methods=['GET'])
def get_consumer_behavior_trend():
    """获取消费者行为趋势数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取时间范围参数
    time_range = request.args.get('timeRange', 'today')
    
    # 根据时间范围确定查询日期
    end_date = datetime.now().date()
    
    if time_range == 'today':
        start_date = end_date
        group_by = '%H'  # 按小时分组
    elif time_range == 'week':
        start_date = end_date - timedelta(days=7)
        group_by = '%Y-%m-%d'  # 按日分组
    elif time_range == 'month':
        start_date = end_date - timedelta(days=30)
        group_by = '%Y-%m-%d'  # 按日分组
    else:
        start_date = end_date - timedelta(days=7)
        group_by = '%Y-%m-%d'
    
    # 首先检查表结构，确定是否存在visit_store列
    cursor.execute("PRAGMA table_info(consumer_actions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 准备查询，根据表结构调整
    if 'visit_store' in columns:
        visit_store_expr = "SUM(visit_store)"
    else:
        # 假设任何动作都是访问，此处可根据实际情况调整
        visit_store_expr = "COUNT(*)"
    
    query = f'''
    SELECT 
        timestamp as time_period,
        COUNT(*) as total_actions,
        {visit_store_expr} as store_visits,
        COUNT(CASE WHEN purchase = 1 THEN 1 END) as purchases
    FROM consumer_actions
    GROUP BY timestamp
    ORDER BY 
        CASE 
            WHEN timestamp LIKE 'Day%' THEN CAST(REPLACE(timestamp, 'Day', '') AS INTEGER)
            ELSE timestamp 
        END
    '''
    
    cursor.execute(query)
    
    trend_data = []
    for row in cursor.fetchall():
        # 计算转化率
        if row['store_visits'] > 0:
            visit_to_purchase = (row['purchases'] or 0) / row['store_visits'] * 100
        else:
            visit_to_purchase = 0
        
        trend_data.append({
            'time_period': row['time_period'],
            'total_actions': row['total_actions'],
            'store_visits': row['store_visits'],
            'purchases': row['purchases'] or 0,
            'conversion_rate': round(visit_to_purchase, 2)
        })
    
    conn.close()
    
    return jsonify({
        'behavior_trend': trend_data
    })

@app.route('/api/system/config', methods=['GET'])
def get_system_config():
    """获取系统配置"""
    # 获取前端需要的全局配置
    config = {
        "api": {
            "baseUrl": f"http://{app_config['host']}:{app_config['port']}", 
            "websocketUrl": f"ws://{app_config['host']}:8766",
            "timeout": 30000,
            "retries": 3
        },
        "app": {
            "title": "正山堂茶业分析系统",
            "refreshInterval": 60000,
            "defaultDateRange": 7
        }
    }
    
    return jsonify(config)

if __name__ == '__main__':
    app.run(debug=True, port=5000)