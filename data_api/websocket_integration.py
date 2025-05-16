#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据API WebSocket集成模块 - 提供实时数据更新
"""

import asyncio
import json
import logging
import os
import sys
import sqlite3
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta

# 确保优先导入当前目录下的模块
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 尝试导入WebSocket服务器和配置
try:
    # 假设 common 目录在项目根目录下
    common_path = Path(__file__).parent.parent / 'common'
    if str(common_path) not in sys.path:
        sys.path.insert(0, str(common_path))
    from tcp_server import TCPServer as WebSocketServer
    from config_loader import config # 使用 common 中的 config_loader
    print(f"成功从 {common_path} 导入 tcp_server 和 config_loader")
except ImportError as e:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('data_api_websocket')
    logger.error(f"无法导入依赖项: {e}，请确保common目录及其文件存在")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('data_api_websocket')

class DataApiWebSocket:
    """数据API的WebSocket服务整合"""

    def __init__(self):
        """初始化DataApiWebSocket"""
        # 从统一配置获取WebSocket配置
        self.host = config.get('services', 'data_api', 'websocket', 'host', default='127.0.0.1')
        self.port = config.get('services', 'data_api', 'websocket', 'port', default=8766)
        self.db_path = config.get('services', 'erniebot', 'database', 'path', default='../erniebot/simulation_data.db')
        # 确保db_path是绝对路径
        if not os.path.isabs(self.db_path):
            self.db_path = str(Path(__file__).parent.parent / self.db_path)

        # 创建WebSocket服务器
        self.ws_server = WebSocketServer(self.host, self.port)

        # 存储连接的客户端信息
        self.clients = set() # Store client_id
        self.client_subscriptions = {} # client_id -> set of subscribed data types

        # 定时任务
        self.update_interval = config.get('services', 'dashboard', 'refresh_interval', default=30000) / 1000 # seconds
        self.update_task = None

        # 初始化完成
        logger.info(f"数据API WebSocket初始化完成，服务器将运行在 ws://{self.host}:{self.port}")
        logger.info(f"数据库路径: {self.db_path}")
        logger.info(f"数据更新间隔: {self.update_interval} 秒")

    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"连接数据库失败: {self.db_path}, 错误: {e}")
            return None

    def setup_handlers(self):
        """设置消息处理器"""
        self.ws_server.register_handler("subscribe", self.handle_subscribe)
        self.ws_server.register_handler("unsubscribe", self.handle_unsubscribe)
        # 注册连接和断开事件
        self.ws_server.on_connect = self.handle_connect
        self.ws_server.on_disconnect = self.handle_disconnect
        logger.info("数据API WebSocket消息处理器设置完成")

    async def handle_connect(self, client_id: str):
        """处理客户端连接"""
        logger.info(f"客户端 {client_id} 已连接")
        self.clients.add(client_id)
        self.client_subscriptions[client_id] = set()
        # 发送连接确认消息
        await self.ws_server.send_to_client(client_id, {
            "type": "connection_established",
            "client_id": client_id
        })

    async def handle_disconnect(self, client_id: str):
        """处理客户端断开连接"""
        logger.info(f"客户端 {client_id} 已断开连接")
        self.clients.discard(client_id)
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]

    async def handle_subscribe(self, client_id: str, message: Dict):
        """处理订阅请求"""
        data_types = message.get('data_types', [])
        if not isinstance(data_types, list):
            data_types = [data_types]

        if client_id not in self.client_subscriptions:
             self.client_subscriptions[client_id] = set()

        for dt in data_types:
            self.client_subscriptions[client_id].add(dt)

        logger.info(f"客户端 {client_id} 订阅了: {data_types}")
        await self.ws_server.send_to_client(client_id, {
            "type": "subscription_confirmed",
            "data_types": list(self.client_subscriptions[client_id])
        })
        # 立即发送一次当前数据
        await self.send_updates(client_id, data_types)

    async def handle_unsubscribe(self, client_id: str, message: Dict):
        """处理取消订阅请求"""
        data_types = message.get('data_types', [])
        if not isinstance(data_types, list):
            data_types = [data_types]

        if client_id in self.client_subscriptions:
            for dt in data_types:
                self.client_subscriptions[client_id].discard(dt)
            logger.info(f"客户端 {client_id} 取消订阅了: {data_types}")
            await self.ws_server.send_to_client(client_id, {
                "type": "unsubscription_confirmed",
                "data_types": list(self.client_subscriptions[client_id])
            })

    async def fetch_data(self, data_type: str) -> Optional[Dict]:
        """从数据库获取指定类型的数据"""
        conn = self.get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        data = None
        try:
            # --- 获取核心指标 --- (与 app.py 逻辑类似)
            if data_type == 'metrics':
                cursor.execute('''
                SELECT
                    SUM(order_count) as total_orders,
                    SUM(gmv) as total_gmv,
                    SUM(user_count) as total_users,
                    SUM(new_user_count) as new_users,
                    SUM(returning_user_count) as returning_users,
                    AVG(avg_order_value) as avg_order
                FROM daily_stats
                ''')
                stats = cursor.fetchone()
                if stats and stats['total_orders'] is not None:
                    data = dict(stats)
                else: # Fallback to consumer_actions
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
                    stats_ca = cursor.fetchone()
                    if stats_ca:
                        data = dict(stats_ca)

            # --- 获取趋势数据 --- (简化示例，获取最近7天)
            elif data_type == 'trend':
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
                cursor.execute('''
                SELECT date, gmv, user_count
                FROM daily_stats
                WHERE date BETWEEN ? AND ?
                ORDER BY date ASC
                ''', [start_date.isoformat(), end_date.isoformat()])
                rows = cursor.fetchall()
                data = {'dates': [], 'gmv': [], 'users': []}
                for row in rows:
                    data['dates'].append(row['date'])
                    data['gmv'].append(row['gmv'] or 0)
                    data['users'].append(row['user_count'] or 0)

            # --- 获取消费者行为数据 (示例：按类型统计购买次数) ---
            elif data_type == 'consumer_behavior':
                cursor.execute('''
                SELECT consumer_type, COUNT(*) as purchase_count
                FROM consumer_actions
                WHERE purchase = 1
                GROUP BY consumer_type
                ORDER BY purchase_count DESC
                ''')
                rows = cursor.fetchall()
                data = {row['consumer_type']: row['purchase_count'] for row in rows}

            # --- 获取消费者地域数据 (示例：按区域统计用户数) ---
            elif data_type == 'consumer_region':
                 cursor.execute('''
                 SELECT region, COUNT(DISTINCT customer_id) as user_count
                 FROM consumer_actions
                 WHERE region IS NOT NULL AND region != '未知'
                 GROUP BY region
                 ORDER BY user_count DESC
                 ''')
                 rows = cursor.fetchall()
                 data = {row['region']: row['user_count'] for row in rows}

            # --- 获取消费者心理数据 (示例：统计主要特征) ---
            elif data_type == 'consumer_psychology':
                cursor.execute('''
                SELECT psychological_trait FROM consumer_actions WHERE psychological_trait IS NOT NULL
                ''')
                rows = cursor.fetchall()
                traits_summary = {}
                for row in rows:
                    try:
                        traits = json.loads(row['psychological_trait'])
                        if isinstance(traits, dict):
                            for key, value in traits.items():
                                if key not in traits_summary:
                                    traits_summary[key] = 0
                                traits_summary[key] += 1
                    except:
                        pass # Ignore parsing errors
                # 取前5个特征
                sorted_traits = sorted(traits_summary.items(), key=lambda item: item[1], reverse=True)
                data = dict(sorted_traits[:5])

        except Exception as e:
            logger.error(f"获取数据类型 '{data_type}' 时出错: {e}")
            data = None
        finally:
            conn.close()

        # 清理 None 值
        if isinstance(data, dict):
            return {k: (v if v is not None else 0) for k, v in data.items()}
        return data

    async def send_updates(self, client_id: Optional[str] = None, data_types: Optional[List[str]] = None):
        """发送数据更新给客户端"""
        target_clients = [client_id] if client_id else list(self.clients)

        for cid in target_clients:
            if cid not in self.client_subscriptions:
                continue

            subscribed_types = self.client_subscriptions[cid]
            types_to_send = subscribed_types
            if data_types:
                # 如果指定了类型，只发送订阅了的指定类型
                types_to_send = subscribed_types.intersection(data_types)

            for data_type in types_to_send:
                fetched_data = await self.fetch_data(data_type)
                if fetched_data is not None:
                    message = {
                        "type": f"{data_type}_data", # e.g., metrics_data, trend_data
                        "timestamp": time.time(),
                        "data": fetched_data
                    }
                    await self.ws_server.send_to_client(cid, message)
                    # logger.debug(f"已发送 {data_type} 数据给客户端 {cid}")
                else:
                    logger.warning(f"无法获取数据类型 '{data_type}' 的数据")

    async def periodic_update_loop(self):
        """定期获取并广播数据更新"""
        while self.ws_server.running:
            try:
                logger.info("执行定期数据更新...")
                await self.send_updates() # Broadcast to all subscribed clients
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                logger.info("定期更新任务已取消")
                break
            except Exception as e:
                logger.error(f"定期更新循环出错: {e}")
                await asyncio.sleep(self.update_interval) # Wait before retrying

    async def start(self):
        """启动WebSocket服务器和定时任务"""
        self.setup_handlers()
        # 启动定期更新任务
        self.update_task = asyncio.create_task(self.periodic_update_loop())
        # 启动WebSocket服务器
        await self.ws_server.start()

    async def stop(self):
        """停止WebSocket服务器和定时任务"""
        if self.update_task:
            self.update_task.cancel()
            with suppress(asyncio.CancelledError):
                 await self.update_task
        await self.ws_server.stop()
        logger.info("数据API WebSocket服务已停止")

async def main():
    """主函数入口"""
    ws_app = DataApiWebSocket()
    try:
        await ws_app.start()
    except KeyboardInterrupt:
        logger.info("收到停止信号...")
    finally:
        await ws_app.stop()

if __name__ == "__main__":
    asyncio.run(main())