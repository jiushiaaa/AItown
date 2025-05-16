#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接创建测试数据的脚本
绕过复杂的解析逻辑，直接向数据库中插入可用于测试的数据
"""

import os
import json
from datetime import datetime, timedelta
import random
import uuid

from modules.db_manager import DBManager

# DBManager 将处理数据库初始化和连接
db_manager = DBManager()

def clear_existing_data():
    """清除现有数据"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM consumer_actions")
        cursor.execute("DELETE FROM daily_stats")
        cursor.execute("DELETE FROM consumers")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='consumer_actions'")
        conn.commit()
        print("已清除现有数据")
    except Exception as e:
        print(f"清除数据时出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def create_customer_base(days=10, customer_count=30):
    """创建基础客户数据"""
    current_date = datetime.now()
    customers = []
    
    # 消费者类型
    consumer_types = ["传统茶文化爱好者", "品质生活追求者", "商务人士", "健康生活主义者", "年轻新贵"]
    
    # 生成客户基础数据
    for i in range(customer_count):
        # 分配首次访问日期，确保在模拟时间范围内有新老客户
        first_visit_day = random.randint(1, days)
        first_visit_date = (current_date - timedelta(days=10-first_visit_day)).date()
        
        # 创建一个随机客户ID
        customer_id = str(uuid.uuid4())
        
        # 随机分配消费者类型
        consumer_type = random.choice(consumer_types)
        
        # 根据首次访问日期确定是否为新客户（模拟前5天来的都是老客户）
        is_new_customer = first_visit_day > 5
        
        customers.append({
            "customer_id": customer_id,
            "first_visit_date": first_visit_date.isoformat(),
            "customer_type": consumer_type,
            "is_new_customer": is_new_customer,
            "visit_count": 0,  # 将在行为生成中更新
            "last_visit_date": None,  # 将在行为生成中更新
            "total_amount": 0  # 将在行为生成中更新
        })
    
    return customers

def create_consumer_data():
    """创建测试消费者数据"""
    # 首先创建消费者基础数据
    customers = create_customer_base(days=10, customer_count=30)
    
    # 区域信息
    regions = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
    city_types = ["一线城市", "新一线城市", "二线城市", "三线城市"]
    
    # 产品信息
    products = [
        {"name": "正山小种", "price": 200},
        {"name": "金骏眉", "price": 350},
        {"name": "正山瑰宝·御韵红茶", "price": 800},
        {"name": "正山小种礼盒装", "price": 600},
        {"name": "骏眉红茶", "price": 220},
        {"name": "定制金骏眉", "price": 500}
    ]
    
    # 心理特征
    psych_traits = [
        {"价格敏感度": "低", "品牌忠诚度": "高", "决策速度": "快"},
        {"价格敏感度": "中", "品牌忠诚度": "中", "决策速度": "中"},
        {"价格敏感度": "高", "品牌忠诚度": "低", "决策速度": "慢"},
        {"价格敏感度": "中高", "品牌忠诚度": "中低", "决策速度": "中慢"},
        {"价格敏感度": "中低", "品牌忠诚度": "中高", "决策速度": "中快"}
    ]
    
    # 生成测试数据
    consumer_actions = []
    
    # 从今天开始，向前推10天
    current_date = datetime.now()
    
    # 跟踪客户访问记录
    customer_visits = {customer["customer_id"]: [] for customer in customers}
    
    for day in range(1, 11):
        day_date = current_date - timedelta(days=10-day)
        
        # 确定当天可能来访的客户
        day_customers = [c for c in customers if datetime.strptime(c["first_visit_date"], "%Y-%m-%d").date() <= day_date.date()]
        
        # 每天随机选择10-15个客户来访
        day_visitor_count = min(len(day_customers), random.randint(10, 15))
        day_visitors = random.sample(day_customers, day_visitor_count)
        
        for customer in day_visitors:
            customer_id = customer["customer_id"]
            day_timestamp = day_date.replace(
                hour=random.randint(9, 20),
                minute=random.randint(0, 59)
            ).isoformat()
            
            # 更新客户访问计数和最后访问日期
            customer["visit_count"] += 1
            customer["last_visit_date"] = day_date.date().isoformat()
            
            # 确定是否为该客户的首次访问
            is_first_visit = customer_id not in customer_visits or not customer_visits[customer_id]
            is_new_visit = len(customer_visits.get(customer_id, [])) == 0
            
            # 记录本次访问
            customer_visits[customer_id].append(day_date.date())
            
            region = random.choice(regions)
            city_type = random.choice(city_types)
            
            # 访问店铺概率：新客户80%，老客户90%
            visit_prob = 0.8 if is_first_visit else 0.9
            visit_store = random.random() < visit_prob
            
            # 浏览时间：新客户10-40分钟，老客户15-60分钟
            if visit_store:
                browse_time = random.randint(10, 40) if is_first_visit else random.randint(15, 60)
            else:
                browse_time = 0
            
            # 购买概率：新客户50%，老客户70%
            purchase_prob = 0.5 if is_first_visit else 0.7
            purchase = random.random() < purchase_prob if visit_store else False
            
            # 如果购买，选择一个产品
            product = random.choice(products) if purchase else {"name": "", "price": 0}
            
            # 如果购买，金额为产品价格的0.8-1.2倍
            amount = 0
            if purchase:
                amount = product["price"] * (0.8 + random.random() * 0.4)
                customer["total_amount"] += amount
            
            # 随机选择心理特征
            trait = random.choice(psych_traits)
            
            consumer_actions.append({
                "customer_id": customer_id,
                "timestamp": day_timestamp,
                "consumer_type": customer["customer_type"],
                "region": region,
                "city_type": city_type,
                "visit_store": 1 if visit_store else 0,
                "browse_time": browse_time,
                "purchase": 1 if purchase else 0,
                "product_name": product["name"],
                "amount": amount,
                "psychological_trait": json.dumps(trait, ensure_ascii=False),
                "day_of_simulation": day,
                "is_new_visit": 1 if is_new_visit else 0
            })
    
    return customers, consumer_actions

def save_test_data(customers, consumer_actions):
    """保存测试数据到数据库"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # 保存消费者基础数据
        for customer in customers:
            cursor.execute('''
            INSERT INTO consumers (
                customer_id, first_visit_date, customer_type, is_new_customer,
                visit_count, last_visit_date, total_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer["customer_id"],
                customer["first_visit_date"],
                customer["customer_type"],
                customer["is_new_customer"],
                customer["visit_count"],
                customer["last_visit_date"],
                customer["total_amount"]
            ))
        
        # 保存消费者行为数据
        for action in consumer_actions:
            cursor.execute('''
            INSERT INTO consumer_actions (
                customer_id, timestamp, consumer_type, region, city_type, visit_store, 
                browse_time, purchase, product_name, amount, psychological_trait, 
                day_of_simulation, is_new_visit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                action["customer_id"],
                action["timestamp"],
                action["consumer_type"],
                action["region"],
                action["city_type"],
                action["visit_store"],
                action["browse_time"],
                action["purchase"],
                action["product_name"],
                action["amount"],
                action["psychological_trait"],
                action["day_of_simulation"],
                action["is_new_visit"]
            ))
        
        # 按日期统计并保存每日数据
        cursor.execute('''
        SELECT 
            date(timestamp) as date,
            COUNT(CASE WHEN purchase = 1 THEN 1 END) as order_count,
            SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as gmv,
            COUNT(DISTINCT customer_id) as user_count,
            COUNT(DISTINCT CASE WHEN is_new_visit = 1 THEN customer_id END) as new_user_count,
            COUNT(DISTINCT CASE WHEN is_new_visit = 0 THEN customer_id END) as returning_user_count,
            AVG(CASE WHEN purchase = 1 THEN amount END) as avg_order_value,
            0 as cancelled_order_count,
            0 as return_count
        FROM consumer_actions
        GROUP BY date(timestamp)
        ''')
        
        daily_stats = cursor.fetchall()
        
        for stats in daily_stats:
            cursor.execute('''
            INSERT OR REPLACE INTO daily_stats (
                date, order_count, gmv, user_count, new_user_count, returning_user_count,
                avg_order_value, cancelled_order_count, return_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats["date"],
                stats["order_count"],
                stats["gmv"],
                stats["user_count"],
                stats["new_user_count"],
                stats["returning_user_count"],
                stats["avg_order_value"],
                stats["cancelled_order_count"],
                stats["return_count"]
            ))
        
        conn.commit()
        print(f"成功保存 {len(customers)} 位消费者、{len(consumer_actions)} 条行为数据和 {len(daily_stats)} 条每日统计数据")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def check_database_status():
    """检查数据库状态"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM consumers")
        customer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM consumer_actions")
        action_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM daily_stats")
        stats_count = cursor.fetchone()[0]
        
        print(f"数据库状态: consumers表中有 {customer_count} 条记录，consumer_actions表中有 {action_count} 条记录，daily_stats表中有 {stats_count} 条记录")
        
        # 检查新老客户分布
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN is_new_customer = 1 THEN 1 ELSE 0 END) as new_customers,
            SUM(CASE WHEN is_new_customer = 0 THEN 1 ELSE 0 END) as returning_customers
        FROM consumers
        ''')
        
        customer_stats = cursor.fetchone()
        print(f"客户分布: {customer_stats['new_customers']} 位新客户, {customer_stats['returning_customers']} 位老客户")
        
        # 检查购买和访问记录
        cursor.execute('''
        SELECT 
            SUM(visit_store) as total_visits,
            SUM(purchase) as total_purchases,
            SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as total_gmv
        FROM consumer_actions
        ''')
        
        visit_stats = cursor.fetchone()
        print(f"访问记录: {visit_stats['total_visits']} 次访问, {visit_stats['total_purchases']} 次购买, 总GMV: {visit_stats['total_gmv']:.2f}")
    except Exception as e:
        print(f"检查数据库状态时出错: {str(e)}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("=== 开始创建测试数据 ===")

    # DBManager 在实例化时会自动初始化数据库结构
    # init_database() # 不再需要调用
    
    # 检查现有数据
    check_database_status()
    
    # 询问是否清除现有数据
    response = input("是否清除现有数据？(y/n): ")
    if response.lower() == 'y':
        clear_existing_data()
    
    # 创建测试数据
    customers, consumer_actions = create_consumer_data()
    print(f"已生成 {len(customers)} 位消费者和 {len(consumer_actions)} 条行为记录")
    
    # 保存测试数据
    save_test_data(customers, consumer_actions)
    
    # 检查结果
    check_database_status()
    
    print("=== 测试数据创建完成 ===")

if __name__ == "__main__":
    main()