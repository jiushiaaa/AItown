#coding=utf-8
"""
数据验证与修复函数模块
"""

import json
import random
import logging
from typing import Dict, Any, Optional, List, Union

from ..config import VALID_LOCATIONS, get_valid_names
from .utils import to_number
from .customer import generate_default_customer_interactions, add_consumer_details
from .stats import generate_default_daily_stats, generate_default_cumulative_stats

def verify_and_fix_json(
    json_data: Union[Dict[str, Any], str], 
    day: int, 
    prev_cumulative: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """验证并修复JSON数据，确保关键字段存在并有效，添加新的销售指标"""
    try:
        # 检查是否为字符串，需要解析
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except Exception as e:
                logging.warning(f"转换字符串为字典时出错: {e}")
                return generate_default_data(day, prev_cumulative)
                    
        # 如果数据为None或空，生成默认数据
        if not json_data:
            logging.warning(f"Day {day}: JSON数据为空，使用默认数据")
            return generate_default_data(day, prev_cumulative)
                
        # 有效名称列表
        valid_names = get_valid_names()
        
        # 检查是否缺少必要的字段
        missing_fields = []
        required_fields = ['store_name', 'day', 'business_hour', 'daily_stats', 'customer_interactions']
        
        for field in required_fields:
            if field not in json_data:
                missing_fields.append(field)
        
        if missing_fields:
            logging.warning(f"Day {day}: JSON缺少必要字段: {', '.join(missing_fields)}")
            # 如果缺少太多字段，可能需要使用默认数据
            if len(missing_fields) > 2:
                return generate_default_data(day, prev_cumulative)
                
            # 修复缺失字段
            for field in missing_fields:
                if field == 'store_name':
                    json_data['store_name'] = '正山堂茶业体验店'
                elif field == 'day':
                    json_data['day'] = day
                elif field == 'business_hour':
                    json_data['business_hour'] = '9:00-21:00'
                elif field == 'daily_stats':
                    json_data['daily_stats'] = generate_default_daily_stats(day)
                elif field == 'customer_interactions':
                    json_data['customer_interactions'] = generate_default_customer_interactions(day)
        
        # 确保必要字段存在
        if 'store_name' not in json_data:
            json_data['store_name'] = '正山堂茶业体验店'
        
        if 'day' not in json_data:
            json_data['day'] = day
        else:
            json_data['day'] = min(to_number(json_data['day']), 30)  # 最多30天
        
        if 'business_hour' not in json_data:
            json_data['business_hour'] = '9:00-20:00'
        
        # 检查并修复daily_stats
        if 'daily_stats' not in json_data or not isinstance(json_data['daily_stats'], dict):
            json_data['daily_stats'] = generate_default_daily_stats(day)
        else:
            required_daily_fields = [
                'customer_flow', 'new_customers', 'returning_customers', 
                'conversion_rate', 'total_sales', 'avg_expense', 'peak_hours', 'best_sellers'
            ]
            
            for field in required_daily_fields:
                if field not in json_data['daily_stats']:
                    if field == 'best_sellers':
                        json_data['daily_stats'][field] = [
                            "金骏眉特级", "金骏眉典藏", "正山小种特级"
                        ]
                    elif field == 'peak_hours':
                        json_data['daily_stats'][field] = "14:00-16:00"
                    elif field == 'conversion_rate':
                        json_data['daily_stats'][field] = "70%"
                    else:
                        # 数字字段，使用默认值
                        json_data['daily_stats'][field] = 50
        
        # 检查并修复cumulative_stats
        if 'cumulative_stats' not in json_data or not isinstance(json_data['cumulative_stats'], dict):
            json_data['cumulative_stats'] = generate_default_cumulative_stats(
                json_data['daily_stats'], prev_cumulative
            )
        else:
            required_cumulative_fields = [
                'total_customers', 'unique_customers', 'loyal_customers', 
                'total_revenue', 'customer_retention', 'avg_visits_per_customer'
            ]
            
            for field in required_cumulative_fields:
                if field not in json_data['cumulative_stats']:
                    if field == 'customer_retention':
                        json_data['cumulative_stats'][field] = "30%"
                    elif field == 'avg_visits_per_customer':
                        json_data['cumulative_stats'][field] = 1.5
                    else:
                        # 数字字段，使用默认值
                        base_value = day * 50
                        json_data['cumulative_stats'][field] = base_value
        
        # 检查customer_interactions
        if 'customer_interactions' not in json_data or not isinstance(json_data['customer_interactions'], list):
            json_data['customer_interactions'] = generate_default_customer_interactions(day)
        elif len(json_data['customer_interactions']) < 7:  # 调整为最少7个交互
            # 不够7个交互，补充到7个
            additional = generate_default_customer_interactions(day)
            json_data['customer_interactions'].extend(additional[:7-len(json_data['customer_interactions'])])
        
        # 检查每个customer_interaction的完整性
        for i, interaction in enumerate(json_data['customer_interactions']):
            required_interaction_fields = ['name', 'type', 'age', 'location', 'visit_count', 'behavior', 'comments', 'emoji']
            for field in required_interaction_fields:
                if field not in interaction:
                    if field == 'name':
                        # 选择一个有效的名字
                        interaction[field] = random.choice(valid_names)
                    elif field == 'type':
                        # 使用正山堂的消费者类型
                        interaction[field] = random.choice([
                            "传统茶文化爱好者", "品质生活追求者", "商务人士", "健康生活主义者", "年轻新贵"
                        ])
                    elif field == 'age':
                        interaction[field] = random.randint(18, 65)
                    elif field == 'location':
                        interaction[field] = random.choice(VALID_LOCATIONS)
                    elif field == 'visit_count':
                        interaction[field] = random.randint(1, day)
                    elif field == 'behavior':
                        interaction[field] = {
                            'entered_store': True,
                            'browsed_minutes': random.randint(15, 45),
                            'made_purchase': random.choice([True, False]),
                            'items_purchased': ["金骏眉特级"],
                            'amount_spent': 150,
                            'satisfaction': 4,
                            'will_return': True,
                            'will_recommend': True
                        }
                    elif field == 'comments':
                        interaction[field] = "总体体验良好"
                    elif field == 'emoji':
                        interaction[field] = "👍✨"
            
            # 确保名字是有效的
            if 'name' in interaction and interaction['name'] not in valid_names:
                interaction['name'] = random.choice(valid_names)
                
            # 确保地点是正确的
            if 'location' in interaction and interaction['location'] not in VALID_LOCATIONS:
                interaction['location'] = random.choice(VALID_LOCATIONS)
                
        # 确保每个客户互动包含地域和消费心理特征
        for interaction in json_data['customer_interactions']:
            if 'region' not in interaction:
                # 获取消费者类型
                consumer_type = interaction.get('type')
                # 调用函数添加地域和消费心理特征
                interaction = add_consumer_details(interaction)
        
        # 如果是分批处理结果，可能需要重新计算daily_stats
        if len(json_data.get('customer_interactions', [])) > 8:  # 判断是否为分批处理结果
            from .stats import recalculate_daily_stats
            recalculate_daily_stats(json_data)
        
        return json_data
            
    except Exception as e:
        logging.error(f"验证和修复JSON时出错: {e}")
        return generate_default_data(day, prev_cumulative)

def generate_default_data(
    day: int, 
    prev_cumulative: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """生成默认数据，包括每日统计和客户互动"""
    daily_stats = generate_default_daily_stats(day)
    cumulative_stats = generate_default_cumulative_stats(daily_stats, prev_cumulative)
    
    return {
        'store_name': '正山堂茶业体验店',
        'day': day,
        'business_hour': '9:00-20:00',
        'daily_stats': daily_stats,
        'cumulative_stats': cumulative_stats,
        'customer_interactions': generate_default_customer_interactions(day)
    } 