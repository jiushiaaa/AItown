#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
erniebot WebSocket集成模块
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from typing import Dict, List, Any, Optional, Callable

# 尝试导入WebSocket服务器
try:
    from common.tcp_server import TCPServer as WebSocketServer
except ImportError:
    # 配置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('erniebot_websocket')
    logger.error("无法导入WebSocketServer，请确保config目录存在且包含所需文件")
    sys.exit(1)

# 导入需要的erniebot模块
from modules.client import ApiClient
from modules.data_processor import string_to_dict, verify_and_fix_json
from modules.product_manager import (
    is_product_generation_request, extract_consumer_type,
    extract_brand_summary
)
from modules.sales_analytics import SalesTracker

# 定义消息类型常量
class TypeFieldDefs:
    TASK_NEW = "question"
    TASK_CONTINUE = "response"
    RESULT_TASK = "task"
    RESULT_CLOSING_REPORT = "closingReport"
    RESULT_PRODUCT_GENERATED = "product_generated"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('erniebot_websocket')

class ErnieBotWebSocket:
    """erniebot的WebSocket服务整合"""
    
    def __init__(self):
        """初始化ErnieBotWebSocket"""
        # 从环境变量获取WebSocket配置
        self.host = os.environ.get('WS_HOST', '127.0.0.1')
        self.port = int(os.environ.get('WS_PORT', '8765'))
        self.enable_legacy = True
        
        # 创建WebSocket服务器
        self.ws_server = WebSocketServer(self.host, self.port)
        
        # 创建API客户端和其他组件
        self.api_client = ApiClient()
        self.sales_tracker = SalesTracker()
        
        # 存储连接的客户端信息
        self.unity_clients = set()
        self.dashboard_clients = set()
        self.client_sessions = {}  # 会话数据，如对话历史等
        
        # 初始化完成
        logger.info(f"ErnieBotWebSocket初始化完成，服务器将运行在 ws://{self.host}:{self.port}")
    
    def setup_handlers(self):
        """设置消息处理器"""
        # 注册消息处理函数
        self.ws_server.register_handler("task_new", self.handle_new_task)
        self.ws_server.register_handler("task_continue", self.handle_continue_task)
        self.ws_server.register_handler("product_request", self.handle_product_request)
        self.ws_server.register_handler("simulation_query", self.handle_simulation_query)
        
        logger.info("消息处理器设置完成")
    
    async def handle_new_task(self, client_id: str, message: Dict):
        """处理新任务请求
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        logger.info(f"处理来自客户端 {client_id} 的新任务")
        
        try:
            # 获取任务内容
            task_content = message.get('content', '')
            
            # 处理直接发送的问题消息（适配Unity客户端）
            if not task_content and 'question' in message:
                task_content = message.get('question', '')
                logger.info(f"从question字段获取任务内容: {task_content}")
            
            if not task_content:
                await self.ws_server.send_to_client(client_id, {
                    "type": "error",
                    "message": "任务内容不能为空"
                })
                return
            
            # 创建或获取会话
            if client_id not in self.client_sessions:
                self.client_sessions[client_id] = {
                    "history": [],
                    "current_task": None
                }
            
            session = self.client_sessions[client_id]
            
            # 设置当前任务
            session["current_task"] = task_content
            
            # 将任务加入历史
            session["history"].append({"role": "user", "content": task_content})
            
            # 检查是否是产品生成请求
            if is_product_generation_request(task_content):
                logger.info(f"检测到产品生成请求: {task_content}")
                await self.handle_product_request(client_id, {
                    "type": "product_request",
                    "content": task_content
                })
                return
            
            # 发送到AI处理
            response = self.api_client.chat_with_messages(session["history"])
            
            # 提取JSON数据(如果有)
            json_text = self.api_client.extract_json(response)
            if json_text:
                json_data = string_to_dict(json_text)
                if json_data:
                    # 验证和修复JSON
                    json_data = verify_and_fix_json(json_data)
                    
                    # 添加AI回复到历史
                    session["history"].append({"role": "assistant", "content": response})
                    
                    # 发送处理后的结果
                    await self.ws_server.send_to_client(client_id, {
                        "type": "task_result",
                        "task": task_content,
                        "result": json_data,
                        "raw_response": response
                    })
                    
                    # 如果是Unity客户端，还需要发送专门的任务数据
                    if client_id in self.unity_clients:
                        await self.send_unity_task_data(client_id, json_data)
                    
                    return
            
            # 如果没有有效的JSON数据，只返回原始响应
            session["history"].append({"role": "assistant", "content": response})
            
            await self.ws_server.send_to_client(client_id, {
                "type": "text_response",
                "task": task_content,
                "response": response
            })
            
        except Exception as e:
            logger.error(f"处理新任务时出错: {e}")
            await self.ws_server.send_to_client(client_id, {
                "type": "error",
                "message": f"处理任务时出错: {str(e)}"
            })
    
    async def handle_continue_task(self, client_id: str, message: Dict):
        """处理继续任务请求
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        logger.info(f"处理来自客户端 {client_id} 的继续任务请求")
        
        try:
            # 检查会话是否存在
            if client_id not in self.client_sessions:
                await self.ws_server.send_to_client(client_id, {
                    "type": "error",
                    "message": "没有活动的会话"
                })
                return
            
            session = self.client_sessions[client_id]
            
            # 检查是否有任务可以继续
            if not session["history"]:
                await self.ws_server.send_to_client(client_id, {
                    "type": "error",
                    "message": "没有可以继续的任务"
                })
                return
            
            # 添加继续指令到历史
            session["history"].append({"role": "user", "content": "继续"})
            
            # 发送到AI处理
            response = self.api_client.chat_with_messages(session["history"])
            
            # 提取JSON数据(如果有)
            json_text = self.api_client.extract_json(response)
            if json_text:
                json_data = string_to_dict(json_text)
                if json_data:
                    # 验证和修复JSON
                    json_data = verify_and_fix_json(json_data)
                    
                    # 添加AI回复到历史
                    session["history"].append({"role": "assistant", "content": response})
                    
                    # 发送处理后的结果
                    await self.ws_server.send_to_client(client_id, {
                        "type": "task_result",
                        "task": "继续",
                        "result": json_data,
                        "raw_response": response
                    })
                    
                    # 如果是Unity客户端，还需要发送专门的任务数据
                    if client_id in self.unity_clients:
                        await self.send_unity_task_data(client_id, json_data)
                    
                    return
            
            # 如果没有有效的JSON数据，只返回原始响应
            session["history"].append({"role": "assistant", "content": response})
            
            await self.ws_server.send_to_client(client_id, {
                "type": "text_response",
                "task": "继续",
                "response": response
            })
            
        except Exception as e:
            logger.error(f"处理继续任务时出错: {e}")
            await self.ws_server.send_to_client(client_id, {
                "type": "error",
                "message": f"处理继续任务时出错: {str(e)}"
            })
    
    async def handle_product_request(self, client_id: str, message: Dict):
        """处理产品生成请求
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        logger.info(f"处理来自客户端 {client_id} 的产品生成请求")
        
        try:
            content = message.get('content', '')
            if not content:
                await self.ws_server.send_to_client(client_id, {
                    "type": "error",
                    "message": "产品请求内容不能为空"
                })
                return
            
            # 提取目标消费群体
            target_consumers = extract_consumer_type(content)
            
            # 生成产品建议
            brand_suggestion = self.api_client.generate_tea_product(target_consumers)
            
            # 提取品牌名称和简洁描述
            brand_name, simple_description = extract_brand_summary(brand_suggestion)
            
            # 设置新产品名称到销售追踪器
            self.sales_tracker.new_product_name = brand_name
            
            # 添加产品生成记录到会话
            if client_id in self.client_sessions:
                self.client_sessions[client_id]["product_info"] = {
                    "name": brand_name,
                    "description": simple_description,
                    "full_suggestion": brand_suggestion,
                    "target_consumers": target_consumers
                }
            
            # 发送产品生成结果 - 适配Unity客户端所需格式
            product_data = {
                "type": "product_generated",
                "resultType": TypeFieldDefs.RESULT_PRODUCT_GENERATED,  # 添加resultType字段
                "product": {
                    "name": brand_name,
                    "description": simple_description,
                    "target_consumers": target_consumers
                },
                "raw_suggestion": brand_suggestion
            }
            
            logger.info(f"向客户端 {client_id} 发送产品生成结果: {brand_name}")
            await self.ws_server.send_to_client(client_id, product_data)
            
            # 广播产品生成通知到所有客户端
            await self.ws_server.broadcast({
                "type": "notification",
                "notification_type": "product_generated",
                "product_name": brand_name
            })
            
        except Exception as e:
            logger.error(f"处理产品生成请求时出错: {e}")
            await self.ws_server.send_to_client(client_id, {
                "type": "error",
                "message": f"生成产品时出错: {str(e)}"
            })
    
    async def handle_simulation_query(self, client_id: str, message: Dict):
        """处理模拟数据查询请求
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        logger.info(f"处理来自客户端 {client_id} 的模拟数据查询")
        
        try:
            query_type = message.get('query_type', 'summary')
            
            # 根据查询类型返回不同的数据
            if query_type == 'summary':
                # 获取摘要数据
                summary_data = self.sales_tracker.get_summary()
                await self.ws_server.send_to_client(client_id, {
                    "type": "simulation_data",
                    "data_type": "summary",
                    "data": summary_data
                })
            
            elif query_type == 'daily':
                # 获取每日数据
                days = message.get('days', 7)
                daily_data = self.sales_tracker.get_daily_stats(days)
                await self.ws_server.send_to_client(client_id, {
                    "type": "simulation_data",
                    "data_type": "daily",
                    "data": daily_data
                })
            
            elif query_type == 'consumer':
                # 获取消费者数据
                consumer_data = self.sales_tracker.get_consumer_data()
                await self.ws_server.send_to_client(client_id, {
                    "type": "simulation_data",
                    "data_type": "consumer",
                    "data": consumer_data
                })
            
            else:
                await self.ws_server.send_to_client(client_id, {
                    "type": "error",
                    "message": f"不支持的查询类型: {query_type}"
                })
        
        except Exception as e:
            logger.error(f"处理模拟数据查询时出错: {e}")
            await self.ws_server.send_to_client(client_id, {
                "type": "error",
                "message": f"查询模拟数据时出错: {str(e)}"
            })
    
    async def send_unity_task_data(self, client_id: str, json_data: Dict):
        """发送任务数据到Unity客户端
        
        Args:
            client_id: 客户端ID
            json_data: 任务数据
        """
        # 提取Unity需要的任务数据
        try:
            # 格式化为Unity可用的格式
            unity_data = {
                "resultType": "task",
                "task": json_data.get("task", ""),
                "process": json_data.get("process", 0),
                "time": json_data.get("time", 0),
                "tasks": json_data.get("tasks", [])
            }
            
            # 发送到Unity客户端
            await self.ws_server.send_to_client(client_id, unity_data)
            
        except Exception as e:
            logger.error(f"格式化Unity任务数据时出错: {e}")
    
    def start(self):
        """启动WebSocket服务器"""
        # 设置消息处理器
        self.setup_handlers()
        
        # 启动WebSocket服务器
        self.ws_server.start()
    
    def start_in_thread(self):
        """在新线程中启动WebSocket服务器"""
        thread = threading.Thread(target=self.start)
        thread.daemon = True
        thread.start()
        return thread

# 如果直接运行此脚本，启动服务
if __name__ == "__main__":
    websocket_server = ErnieBotWebSocket()
    websocket_server.start()