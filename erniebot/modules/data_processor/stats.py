#coding=utf-8
"""
统计数据相关函数模块
"""

import random
import math
import logging
from typing import Dict, Any, List, Optional

from ..config import get_product_info

def generate_default_daily_stats(day: int) -> Dict[str, Any]:
    """生成默认的每日统计数据"""
    base_customer_flow = 25 + min(day * 2, 20)  # 基础客流量，从大约25人开始，最多增加20人
    
    # 添加周末和节假日的波动影响
    is_weekend = day % 7 == 0 or day % 7 == 6  # 判断是否为周末
    
    # 节假日列表 (春节、清明、五一、中秋、国庆等重要节日)
    holiday_days = [3, 8, 15, 22, 28]  # 模拟重要节日天数
    is_holiday = day in holiday_days
    
    # 促销活动类型
    promotion_types = [
        "会员积分双倍日", 
        "新品上市特惠", 
        "节日礼盒优惠", 
        "茶艺体验免费日",
        "限时折扣", 
        "买赠活动", 
        "VIP专享日"
    ]
    
    # 促销日判断 - 节假日必定是促销日
    is_promotion_day = is_holiday or day % 4 == 0 or random.random() < 0.15
    # 选择促销类型
    promotion_type = random.choice(promotion_types) if is_promotion_day else None
    
    # 模拟季节性波动（假设模拟的30天在一个季度内）
    season_phase = (day % 30) / 30.0  # 0到1之间的值表示在季度中的位置
    seasonal_factor = 1.0 + 0.2 * math.sin(2 * math.pi * season_phase)  # 正弦波形的季节性因子，+/-20%
    
    # 计算客流量
    flow_modifier = 1.0
    if is_weekend:
        flow_modifier += 0.3  # 周末客流量增加30%
    if is_promotion_day:
        flow_modifier += 0.4  # 促销日客流量增加40%
    
    # 加入随机波动
    random_factor = random.uniform(0.85, 1.15)  # 随机波动在85%-115%之间
    
    # 最终客流量
    customer_flow = int(base_customer_flow * flow_modifier * seasonal_factor * random_factor)
    customer_flow = max(20, min(80, customer_flow))  # 限制在20-80人之间，避免极端值
    
    # 新客户比例随时间降低，回头客比例随时间增加
    new_customer_ratio = max(0.6, 0.85 - day * 0.01)  # 从85%降到至少60%
    new_customers = int(customer_flow * new_customer_ratio)
    returning_customers = customer_flow - new_customers
    
    # 转化率（随天数略微增加，但有波动）
    base_conversion_rate = 50 + min(day * 0.5, 10)  # 基础转化率从50%开始，最多增加10%
    
    # 转化率受促销和周末影响
    conversion_modifier = 0
    if is_promotion_day:
        conversion_modifier += 10  # 促销日转化率增加10%
    if is_weekend:
        conversion_modifier += 5   # 周末转化率增加5%
    
    # 加入随机波动
    conversion_random = random.randint(-10, 10)  # 随机波动在-10%到+10%之间
    
    # 最终转化率
    conversion_rate = min(90, max(40, base_conversion_rate + conversion_modifier + conversion_random))  # 限制在40%-90%
    
    # 客单价（随促销和周末波动）
    base_avg_expense = 250 + min(day * 2, 50)  # 基础客单价从250元开始，最多增加50元
    
    # 客单价受促销和周末影响
    expense_modifier = 1.0
    if is_promotion_day:
        expense_modifier = 0.9  # 促销日单价降低10%但销量增加
    if is_weekend:
        expense_modifier *= 1.15  # 周末单价增加15%
    
    # 客单价随机波动
    expense_random = random.uniform(0.9, 1.1)  # 随机波动在90%-110%之间
    
    # 最终客单价
    avg_expense = int(base_avg_expense * expense_modifier * expense_random)
    avg_expense = max(200, min(500, avg_expense))  # 限制在200-500元之间
    
    # 计算总销售额
    total_sales = int(customer_flow * (conversion_rate / 100) * avg_expense)
    
    # 模拟高峰时段（有一定规律但也有变化）
    peak_hour_patterns = [
        "10:00-12:00", "11:00-13:00", "12:00-14:00",  # 午餐时段
        "14:00-16:00", "15:00-17:00", "16:00-18:00",  # 下午时段
        "17:00-19:00", "18:00-20:00"                  # 晚餐时段
    ]
    
    # 周末和工作日的高峰不同
    if is_weekend:
        peak_hours = random.choice(["10:00-12:00", "14:00-16:00", "15:00-17:00", "16:00-18:00"])
    else:
        # 工作日早晚更可能是高峰
        peak_hours = random.choice(["11:00-13:00", "12:00-14:00", "17:00-19:00", "18:00-20:00"])
    
    # 随机选择2-3款畅销产品
    all_products = list(get_product_info().keys())
    num_best_sellers = random.randint(2, 3)
    
    # 产品受季节和促销影响
    seasonal_products = []
    if season_phase < 0.33:  # 季初
        seasonal_products = ["金骏眉特级", "正山小种特级", "银骏眉"]
    elif season_phase < 0.66:  # 季中
        seasonal_products = ["正山韵·传世金红", "妃子笑", "宋风雅韵礼盒"]
    else:  # 季末
        seasonal_products = ["秘境寻踪礼盒", "全家福组合礼盒", "骏眉红"]
    
    # 促销产品在促销日有更高概率成为畅销品
    if is_promotion_day:
        promo_products = ["正山韵·传世金红", "金骏眉特级", "经典马口罐礼盒"]
        
        # 80%的概率至少有一款促销产品成为畅销品
        if random.random() < 0.8:
            best_sellers = [random.choice(promo_products)]
            remaining_products = [p for p in all_products if p not in best_sellers]
            best_sellers += random.sample(remaining_products, num_best_sellers - 1)
        else:
            best_sellers = random.sample(all_products, num_best_sellers)
    else:
        # 非促销日
        # 60%的概率至少有一款季节产品成为畅销品
        if random.random() < 0.6:
            best_sellers = [random.choice(seasonal_products)]
            remaining_products = [p for p in all_products if p not in best_sellers]
            best_sellers += random.sample(remaining_products, num_best_sellers - 1)
        else:
            best_sellers = random.sample(all_products, num_best_sellers)
    
    return {
        'customer_flow': customer_flow,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'conversion_rate': f"{conversion_rate}%",
        'total_sales': total_sales,
        'avg_expense': avg_expense,
        'peak_hours': peak_hours,
        'best_sellers': best_sellers,
        # 添加额外的促销信息
        'is_promotion_day': is_promotion_day,
        'is_weekend': is_weekend,
        'is_holiday': is_holiday,
        'promotion_type': promotion_type
    }

def generate_default_cumulative_stats(
    daily_stats: Dict[str, Any], 
    previous_cumulative: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """根据每日统计和之前的累计统计生成新的累计统计"""
    if previous_cumulative is None:
        # 首日数据
        return {
            'total_customers': daily_stats['customer_flow'],
            'unique_customers': daily_stats['customer_flow'],
            'loyal_customers': 0,
            'total_revenue': daily_stats['total_sales'],
            'customer_retention': '0%',
            'avg_visits_per_customer': 1.0
        }
    else:
        # 累计数据更新
        new_unique = int(daily_stats['new_customers'])
        total_customers = previous_cumulative['total_customers'] + daily_stats['customer_flow']
        unique_customers = previous_cumulative['unique_customers'] + new_unique
        loyal_customers = previous_cumulative['loyal_customers'] + int(daily_stats['returning_customers'] * 0.3)
        total_revenue = previous_cumulative['total_revenue'] + daily_stats['total_sales']
        
        if unique_customers > 0:
            customer_retention = f"{int((loyal_customers / unique_customers) * 100)}%"
            avg_visits = round(total_customers / unique_customers, 2)
        else:
            customer_retention = "0%"
            avg_visits = 1.0
            
        return {
            'total_customers': total_customers,
            'unique_customers': unique_customers,
            'loyal_customers': loyal_customers,
            'total_revenue': total_revenue,
            'customer_retention': customer_retention,
            'avg_visits_per_customer': avg_visits
        }

def recalculate_daily_stats(json_data: Dict[str, Any]) -> None:
    """重新计算daily_stats，适用于分批处理合并后的数据"""
    try:
        interactions = json_data.get('customer_interactions', [])
        
        # 无交互则不处理
        if not interactions:
            return
        
        # 统计客流量
        customer_flow = len(interactions)
        
        # 计算新客户和回头客
        new_customers = sum(1 for interaction in interactions if interaction.get('visit_count', 0) == 1)
        returning_customers = customer_flow - new_customers
        
        # 计算消费转化率
        purchases = sum(1 for interaction in interactions if 
                      interaction.get('behavior', {}).get('made_purchase', False))
        conversion_rate = f"{int((purchases/customer_flow*100) if customer_flow > 0 else 0)}%"
        
        # 计算销售总额
        total_sales = sum(interaction.get('behavior', {}).get('amount_spent', 0) for interaction in interactions)
        
        # 计算人均消费
        avg_expense = int(total_sales / purchases) if purchases > 0 else 0
        
        # 确定最畅销产品
        product_counts = {}
        for interaction in interactions:
            for product in interaction.get('behavior', {}).get('items_purchased', []):
                product_counts[product] = product_counts.get(product, 0) + 1
        
        best_sellers = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
        best_seller_names = [product for product, _ in best_sellers[:3]] if best_sellers else []
        
        # 确定高峰时段 (简化处理，随机选择)
        import random
        peak_hours_options = ['10:00-12:00', '14:00-16:00', '16:00-18:00', '18:00-20:00']
        peak_hours = random.choice(peak_hours_options)
        
        # 更新daily_stats
        json_data['daily_stats'] = {
            'customer_flow': customer_flow,
            'new_customers': new_customers,
            'returning_customers': returning_customers,
            'conversion_rate': conversion_rate,
            'total_sales': total_sales,
            'avg_expense': avg_expense,
            'peak_hours': peak_hours,
            'best_sellers': best_seller_names[:3] if best_seller_names else ['金骏眉', '正山小种']
        }
        
    except Exception as e:
        logging.error(f"重新计算daily_stats时出错: {e}")
        # 保留原始daily_stats 