#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库写入脚本
用于将模拟日志数据处理并写入数据库
"""

import os
import json
import sqlite3
from datetime import datetime
import sys
import glob
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加上级目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据库管理器
try:
    from modules.db_manager import DBManager
except ImportError:
    # 如果直接运行此脚本，添加上级目录到路径，以便导入模块
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from modules.db_manager import DBManager

def find_latest_log_file():
    """查找最新的日志文件"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_files = glob.glob(os.path.join(base_dir, 'realtime_simulation_log_*.json'))
    
    if not log_files:
        logging.error("未找到模拟日志文件，请先运行模拟生成数据")
        return None
    
    # 按时间倒序排列，获取最新的日志文件
    log_files.sort(reverse=True)
    latest_log = log_files[0]
    logging.info(f"找到最新日志文件: {os.path.basename(latest_log)}")
    
    return latest_log

def read_log_file(log_path):
    """读取日志文件"""
    if not log_path or not os.path.exists(log_path):
        logging.error(f"日志文件不存在: {log_path}")
        return None
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
            logging.info(f"成功读取日志文件: {len(log_data)} 个顶级键")
            return log_data
    except Exception as e:
        logging.error(f"读取日志文件失败: {e}")
        return None

def ensure_db_tables(db_manager):
    """确保数据库表已创建"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查数据库表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        existing_tables = [table[0] for table in tables]
        logging.info(f"数据库现有表: {existing_tables}")
        
        # 初始化必要的表(如果不存在)
        if 'consumer_actions' not in existing_tables:
            logging.info("创建 consumer_actions 表")
            cursor.execute('''
            CREATE TABLE consumer_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id VARCHAR(50) NOT NULL,
                timestamp DATETIME NOT NULL,
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
                is_new_visit BOOLEAN
            )
            ''')
            
        if 'daily_stats' not in existing_tables:
            logging.info("创建 daily_stats 表")
            cursor.execute('''
            CREATE TABLE daily_stats (
                date DATE PRIMARY KEY,
                order_count INTEGER,
                gmv DECIMAL(12,2),
                user_count INTEGER,
                new_user_count INTEGER,
                returning_user_count INTEGER,
                avg_order_value DECIMAL(10,2),
                cancelled_order_count INTEGER,
                return_count INTEGER
            )
            ''')
            
        if 'consumers' not in existing_tables:
            logging.info("创建 consumers 表")
            cursor.execute('''
            CREATE TABLE consumers (
                customer_id VARCHAR(50) PRIMARY KEY,
                first_visit_date DATE NOT NULL,
                customer_type VARCHAR(50) NOT NULL,
                is_new_customer BOOLEAN DEFAULT 1,
                visit_count INTEGER DEFAULT 1,
                last_visit_date DATE,
                total_amount DECIMAL(10,2) DEFAULT 0
            )
            ''')
            
        conn.commit()
        logging.info("数据库表结构检查/创建完成")
        return True
    except Exception as e:
        logging.error(f"创建数据库表时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def clear_existing_data(db_manager, auto_confirm=False):
    """清除现有数据"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # 询问用户是否需要清空现有数据
        should_clear = auto_confirm
        if not auto_confirm:
            response = input("是否清空现有数据？(y/n): ").lower()
            should_clear = response == 'y'
        
        if should_clear:
            logging.info("清空现有数据...")
            cursor.execute("DELETE FROM consumer_actions")
            cursor.execute("DELETE FROM daily_stats")
            cursor.execute("DELETE FROM consumers")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='consumer_actions'")
            conn.commit()
            logging.info("数据已清空")
            return True
        else:
            logging.info("保留现有数据")
            return False
    except Exception as e:
        logging.error(f"清除数据时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def process_days_data(log_data, db_manager):
    """处理日志中的每一天模拟数据并写入数据库"""
    if not log_data:
        logging.error("日志数据为空，无法处理")
        return False
    
    days_data = log_data.get('days', [])
    logging.info(f"找到 {len(days_data)} 天的模拟数据")
    
    if not days_data:
        logging.error("日志中没有找到天数据")
        
        # 创建默认的一天数据作为备用方案
        current_date = datetime.now()
        default_day_data = {
            "day": 1,
            "data": {
                "consumers": [
                    {
                        "id": "default_customer_001",
                        "timestamp": current_date.strftime('%Y-%m-%dT10:00:00'),
                        "consumer_type": "茶文化爱好者",
                        "region": "华东",
                        "city_type": "一线城市",
                        "visit_store": True,
                        "browse_time": 15,
                        "purchase": True,
                        "product_name": "经典红茶",
                        "amount": 150.0,
                        "psychological_trait": {"价格敏感度": "中", "品牌忠诚度": "中", "决策速度": "中"}
                    }
                ]
            }
        }
        
        logging.info("创建默认天数据作为备用方案")
        days_data = [default_day_data]
    
    # 使用集合记录已处理天数，避免重复处理
    processed_days = set()
    success_count = 0
    
    for day_entry in days_data:
        day = day_entry.get('day', 0)
        
        # 跳过已处理的天数
        if day in processed_days:
            logging.info(f"第 {day} 天的数据已处理，跳过")
            continue
        
        processed_days.add(day)
        data = day_entry.get('data', {})
        
        logging.info(f"处理第 {day} 天的数据")
        
        # 适配不同的数据结构
        adapted_data = data.copy()
        
        # 兼容两种可能的数据结构
        if "customer_interactions" in data and not "consumers" in data:
            logging.info("转换 customer_interactions 为 consumers 格式")
            adapted_data["consumers"] = data["customer_interactions"]
        
        # 如果没有consumers数据，创建一个空的列表
        if "consumers" not in adapted_data:
            logging.warning(f"第 {day} 天没有consumers数据，创建空列表")
            adapted_data["consumers"] = []
        
        # 保存到数据库
        result = db_manager.save_simulation_data(adapted_data, day)
        
        if result:
            success_count += 1
    
    logging.info(f"成功处理 {success_count}/{len(processed_days)} 天的数据")
    return success_count > 0

def process_consumer_data(log_data, db_manager):
    """从日志中提取消费者信息并写入数据库"""
    if not log_data:
        return False
    
    # 获取所有天的数据
    days_data = log_data.get('days', [])
    if not days_data:
        return False
    
    # 收集所有消费者信息
    consumers_info = {}
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        for day_entry in days_data:
            day = day_entry.get('day', 0)
            data = day_entry.get('data', {})
            
            # 获取消费者数据
            consumers = data.get("consumers", [])
            if not consumers and "customer_interactions" in data:
                consumers = data.get("customer_interactions", [])
            
            day_timestamp = datetime.now().isoformat()
            
            for consumer in consumers:
                # 提取或生成消费者ID
                customer_id = consumer.get("id", str(hash(json.dumps(consumer, sort_keys=True))))
                
                # 检查是否已经记录此消费者
                if customer_id in consumers_info:
                    # 更新现有记录
                    consumer_info = consumers_info[customer_id]
                    consumer_info["visit_count"] += 1
                    consumer_info["last_visit_date"] = day_timestamp
                    
                    # 如果有购买，增加总金额
                    if consumer.get("purchase", False) or consumer.get("made_purchase", False):
                        amount = consumer.get("amount", 0)
                        if not amount:
                            # 尝试从behavior中获取
                            behavior = consumer.get("behavior", {})
                            if isinstance(behavior, dict):
                                amount = behavior.get("amount_spent", 0)
                        
                        consumers_info[customer_id]["total_amount"] += float(amount)
                else:
                    # 创建新记录
                    consumer_type = consumer.get("type", "未知")
                    
                    # 确定是否为新客户
                    is_new_customer = consumer.get("is_new", True)
                    if "is_new_visit" in consumer:
                        is_new_customer = bool(consumer.get("is_new_visit"))
                    
                    # 初始购买金额
                    amount = 0
                    if consumer.get("purchase", False) or consumer.get("made_purchase", False):
                        amount = consumer.get("amount", 0)
                        if not amount:
                            # 尝试从behavior中获取
                            behavior = consumer.get("behavior", {})
                            if isinstance(behavior, dict):
                                amount = behavior.get("amount_spent", 0)
                    
                    consumers_info[customer_id] = {
                        "customer_id": customer_id,
                        "first_visit_date": day_timestamp,
                        "customer_type": consumer_type,
                        "is_new_customer": is_new_customer,
                        "visit_count": 1,
                        "last_visit_date": day_timestamp,
                        "total_amount": float(amount)
                    }
        
        # 将收集到的消费者信息写入数据库
        for customer_id, consumer_info in consumers_info.items():
            cursor.execute('''
            INSERT OR REPLACE INTO consumers
            (customer_id, first_visit_date, customer_type, 
            is_new_customer, visit_count, last_visit_date, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                consumer_info["customer_id"],
                consumer_info["first_visit_date"],
                consumer_info["customer_type"],
                1 if consumer_info["is_new_customer"] else 0,
                consumer_info["visit_count"],
                consumer_info["last_visit_date"],
                consumer_info["total_amount"]
            ))
        
        conn.commit()
        logging.info(f"成功保存 {len(consumers_info)} 位消费者信息")
        return True
    except Exception as e:
        logging.error(f"处理消费者数据时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_daily_stats(db_manager):
    """根据消费者行为数据更新每日统计"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # 从消费者行为数据中汇总统计信息
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
        logging.info(f"成功更新 {len(daily_stats)} 条每日统计数据")
        return True
    except Exception as e:
        logging.error(f"更新每日统计时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def check_database_status(db_manager):
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
        
        logging.info(f"数据库状态: consumers表中有 {customer_count} 条记录，consumer_actions表中有 {action_count} 条记录，daily_stats表中有 {stats_count} 条记录")
        
        # 检查新老客户分布
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN is_new_customer = 1 THEN 1 ELSE 0 END) as new_customers,
            SUM(CASE WHEN is_new_customer = 0 THEN 1 ELSE 0 END) as returning_customers
        FROM consumers
        ''')
        
        customer_stats = cursor.fetchone()
        if customer_stats and customer_stats[0] is not None:
            logging.info(f"客户分布: {customer_stats['new_customers']} 位新客户, {customer_stats['returning_customers']} 位老客户")
        
        # 检查购买和访问记录
        cursor.execute('''
        SELECT 
            SUM(visit_store) as total_visits,
            SUM(purchase) as total_purchases,
            SUM(CASE WHEN purchase = 1 THEN amount ELSE 0 END) as total_gmv
        FROM consumer_actions
        ''')
        
        visit_stats = cursor.fetchone()
        if visit_stats and visit_stats[0] is not None:
            logging.info(f"访问记录: {visit_stats['total_visits']} 次访问, {visit_stats['total_purchases']} 次购买, 总GMV: {visit_stats['total_gmv']:.2f}")
        
        return True
    except Exception as e:
        logging.error(f"检查数据库状态时出错: {e}")
        return False
    finally:
        conn.close()

def main(auto_confirm=False):
    """主函数，处理所有逻辑流程"""
    logging.info("=== 开始处理模拟日志并写入数据库 ===")
    
    # 查找最新的日志文件
    log_path = find_latest_log_file()
    if not log_path:
        return False
    
    # 读取日志文件
    log_data = read_log_file(log_path)
    if not log_data:
        return False
    
    # 初始化数据库管理器
    db_manager = DBManager()
    
    # 确保数据库表已创建
    if not ensure_db_tables(db_manager):
        return False
    
    # 检查数据库初始状态
    check_database_status(db_manager)
    
    # 清除现有数据 (使用auto_confirm参数)
    clear_existing_data(db_manager, auto_confirm)
    
    # 处理日志中的每天模拟数据
    if not process_days_data(log_data, db_manager):
        logging.error("处理模拟数据失败")
        return False
    
    # 处理消费者数据
    if not process_consumer_data(log_data, db_manager):
        logging.warning("处理消费者数据失败，继续执行后续步骤")
    
    # 更新每日统计
    if not update_daily_stats(db_manager):
        logging.warning("更新每日统计失败，继续执行后续步骤")
    
    # 检查最终数据库状态
    check_database_status(db_manager)
    
    logging.info("=== 日志处理完成，数据已写入数据库 ===")
    return True

if __name__ == "__main__":
    # 检查命令行参数
    auto_confirm = False
    if len(sys.argv) > 1 and sys.argv[1] == '--auto-confirm':
        auto_confirm = True
    
    main(auto_confirm) 