#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebSocket 与统一数据存储集成示例

此文件演示如何在WebSocket服务器和客户端中正确使用统一数据存储方案。
"""

import os
import json
import logging
import asyncio
import websockets
import threading
from datetime import datetime
from common.data_manager import (
    data_manager,
    get_path, 
    load_yaml, 
    save_json, 
    load_json,
    setup_logger
)

# 设置日志记录器
logger = setup_logger('websocket_integration', level=logging.INFO)

class DataStorageWebSocketServer:
    """使用统一数据存储方案的WebSocket服务器"""
    
    def __init__(self):
        # 从配置文件加载WebSocket服务器配置
        self.config = load_yaml('config', 'server_settings.yaml')
        self.port = self.config.get('server', {}).get('port', 8767)
        self.host = self.config.get('server', {}).get('host', '127.0.0.1')
        
        # 初始化客户端连接存储
        self.clients = set()
        self.client_info = {}
        
        # 设置会话目录路径
        self.session_dir = 'sessions'
        if not data_manager.dir_exists(self.session_dir):
            data_manager.create_directory(self.session_dir)
        
        logger.info(f"WebSocket服务器初始化完成，配置为: {self.host}:{self.port}")
    
    async def register_client(self, websocket, client_id=None):
        """注册新客户端连接并保存会话信息"""
        self.clients.add(websocket)
        
        # 生成客户端ID(如果未提供)
        client_id = client_id or f"client_{len(self.clients)}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 记录客户端信息
        self.client_info[websocket] = {
            'id': client_id,
            'connected_at': datetime.now().isoformat(),
            'remote_address': websocket.remote_address if hasattr(websocket, 'remote_address') else 'unknown'
        }
        
        # 保存会话信息到文件
        session_file = f"{client_id}.json"
        await self.save_session_data(client_id, self.client_info[websocket])
        
        logger.info(f"客户端 {client_id} 已连接")
        return client_id
    
    async def unregister_client(self, websocket):
        """注销客户端连接并更新会话信息"""
        if websocket in self.clients:
            client_id = self.client_info[websocket]['id']
            self.client_info[websocket]['disconnected_at'] = datetime.now().isoformat()
            
            # 更新会话信息
            await self.save_session_data(client_id, self.client_info[websocket])
            
            # 移除客户端
            self.clients.remove(websocket)
            logger.info(f"客户端 {client_id} 已断开连接")
    
    async def save_session_data(self, client_id, session_data):
        """保存会话数据到文件"""
        session_file = f"{client_id}.json"
        success = save_json(session_data, self.session_dir, session_file)
        if success:
            logger.debug(f"已保存会话数据: {client_id}")
        else:
            logger.error(f"保存会话数据失败: {client_id}")
    
    async def load_session_data(self, client_id):
        """加载会话数据"""
        session_file = f"{client_id}.json"
        if data_manager.file_exists(self.session_dir, session_file):
            return load_json(self.session_dir, session_file)
        return None
    
    async def save_message(self, client_id, message_data):
        """保存客户端消息到消息历史文件"""
        # 获取并创建客户端消息目录
        message_dir = f"messages/{client_id}"
        if not data_manager.dir_exists('sessions', message_dir):
            data_manager.create_directory('sessions', message_dir)
        
        # 生成消息文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_file = f"{timestamp}.json"
        
        # 构建消息数据并保存
        message_record = {
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id,
            'data': message_data,
            'type': message_data.get('type', 'unknown')
        }
        
        success = save_json(message_record, 'sessions', f"{message_dir}/{message_file}")
        if success:
            logger.debug(f"已保存消息: {client_id}/{message_file}")
        else:
            logger.error(f"保存消息失败: {client_id}/{message_file}")
        
        return message_file
    
    async def process_message(self, websocket, message):
        """处理接收到的消息"""
        client_id = self.client_info[websocket]['id']
        logger.info(f"收到来自 {client_id} 的消息: {message[:50]}...")
        
        try:
            # 解析消息
            data = json.loads(message)
            
            # 保存消息
            message_file = await self.save_message(client_id, data)
            
            # 处理不同类型的消息
            msg_type = data.get('type', 'unknown')
            response = {'status': 'ok', 'message': f'已处理 {msg_type} 消息'}
            
            # 根据消息类型执行相应操作
            if msg_type == 'query':
                # 示例: 加载产品数据
                product_id = data.get('product_id')
                if product_id:
                    product_path = f"tea/{product_id}.json"
                    if data_manager.file_exists('products', product_path):
                        product = load_json('products', product_path)
                        response['data'] = product
                    else:
                        response = {'status': 'error', 'message': f'产品 {product_id} 不存在'}
            
            elif msg_type == 'save':
                # 示例: 保存用户数据
                user_data = data.get('user_data')
                if user_data and 'id' in user_data:
                    user_id = user_data['id']
                    user_path = f"{user_id}.json"
                    success = save_json(user_data, 'users', user_path)
                    if not success:
                        response = {'status': 'error', 'message': '保存用户数据失败'}
            
            elif msg_type == 'log':
                # 示例: 记录客户端日志
                log_entry = data.get('log_entry')
                if log_entry:
                    log_file = f"client_{client_id}.log"
                    log_path = get_path('logs', 'clients', log_file)
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.now().isoformat()} - {log_entry}\n")
            
            # 发送响应
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            logger.error(f"无效的JSON消息: {message[:50]}...")
            await websocket.send(json.dumps({'status': 'error', 'message': '无效的JSON格式'}))
        except Exception as e:
            logger.exception(f"处理消息时出错: {str(e)}")
            await websocket.send(json.dumps({'status': 'error', 'message': f'服务器错误: {str(e)}'}))
    
    async def handler(self, websocket, path):
        """处理WebSocket连接"""
        # 注册客户端
        client_id = await self.register_client(websocket)
        
        try:
            # 发送欢迎消息
            await websocket.send(json.dumps({
                'type': 'welcome',
                'client_id': client_id,
                'message': '欢迎连接到茶叶分析系统WebSocket服务!'
            }))
            
            # 接收和处理消息
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_id} 连接关闭")
        except Exception as e:
            logger.exception(f"处理连接时出错: {str(e)}")
        finally:
            # 注销客户端
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """启动WebSocket服务器"""
        logger.info(f"正在启动WebSocket服务器: {self.host}:{self.port}")
        server = await websockets.serve(self.handler, self.host, self.port)
        await asyncio.Future()  # 保持服务器运行

# WebSocket客户端示例
class DataStorageWebSocketClient:
    """使用统一数据存储方案的WebSocket客户端"""
    
    def __init__(self):
        # 从配置文件加载WebSocket客户端配置
        self.config = load_yaml('config', 'server_settings.yaml')
        self.server_url = f"ws://{self.config.get('server', {}).get('host', '127.0.0.1')}:{self.config.get('server', {}).get('port', 8765)}"
        
        # 设置客户端ID和会话存储
        self.client_id = f"client_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.cache_dir = 'cache/websocket'
        
        # 确保缓存目录存在
        if not data_manager.dir_exists(self.cache_dir):
            data_manager.create_directory(self.cache_dir)
        
        logger.info(f"WebSocket客户端初始化完成，服务器地址: {self.server_url}")
    
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"已连接到服务器: {self.server_url}")
            
            # 接收并处理欢迎消息
            welcome = await self.websocket.recv()
            welcome_data = json.loads(welcome)
            if welcome_data.get('type') == 'welcome':
                self.client_id = welcome_data.get('client_id', self.client_id)
                logger.info(f"服务器分配的客户端ID: {self.client_id}")
                
                # 保存连接信息
                connection_info = {
                    'client_id': self.client_id,
                    'server_url': self.server_url,
                    'connected_at': datetime.now().isoformat(),
                    'welcome_message': welcome_data.get('message', '')
                }
                save_json(connection_info, self.cache_dir, 'connection.json')
                
            return True
        except Exception as e:
            logger.error(f"连接到服务器失败: {str(e)}")
            return False
    
    async def disconnect(self):
        """断开与服务器的连接"""
        if hasattr(self, 'websocket'):
            await self.websocket.close()
            logger.info("已断开与服务器的连接")
            
            # 更新连接信息
            if data_manager.file_exists(self.cache_dir, 'connection.json'):
                connection_info = load_json(self.cache_dir, 'connection.json')
                connection_info['disconnected_at'] = datetime.now().isoformat()
                save_json(connection_info, self.cache_dir, 'connection.json')
    
    async def send_message(self, message_data):
        """发送消息到服务器"""
        if not hasattr(self, 'websocket'):
            logger.error("未连接到服务器")
            return None
        
        try:
            # 发送消息
            await self.websocket.send(json.dumps(message_data))
            logger.info(f"已发送消息类型: {message_data.get('type', 'unknown')}")
            
            # 接收响应
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            # 缓存消息和响应
            message_record = {
                'timestamp': datetime.now().isoformat(),
                'message': message_data,
                'response': response_data
            }
            
            # 生成消息文件名并保存
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            message_file = f"{timestamp}_{message_data.get('type', 'unknown')}.json"
            save_json(message_record, self.cache_dir, f"messages/{message_file}")
            
            return response_data
        except Exception as e:
            logger.exception(f"发送消息失败: {str(e)}")
            return None
    
    async def query_product(self, product_id):
        """查询产品信息"""
        message = {
            'type': 'query',
            'product_id': product_id
        }
        return await self.send_message(message)
    
    async def save_user_data(self, user_data):
        """保存用户数据"""
        message = {
            'type': 'save',
            'user_data': user_data
        }
        return await self.send_message(message)
    
    async def send_log(self, log_entry):
        """发送日志条目到服务器"""
        message = {
            'type': 'log',
            'log_entry': log_entry
        }
        return await self.send_message(message)

# 以下为示例代码，演示如何启动服务器和客户端
async def run_demo_server():
    """启动示例服务器"""
    server = DataStorageWebSocketServer()
    await server.start_server()

async def run_demo_client():
    """启动示例客户端"""
    client = DataStorageWebSocketClient()
    
    try:
        # 连接到服务器
        connected = await client.connect()
        if not connected:
            logger.error("无法连接到服务器，客户端演示终止")
            return
        
        # 查询产品
        product_response = await client.query_product("tea-001")
        logger.info(f"产品查询响应: {product_response}")
        
        # 保存用户数据
        user_data = {
            'id': 'user123',
            'name': '张三',
            'preferences': ['龙井', '碧螺春'],
            'last_login': datetime.now().isoformat()
        }
        user_response = await client.save_user_data(user_data)
        logger.info(f"保存用户数据响应: {user_response}")
        
        # 发送日志
        log_response = await client.send_log("客户端测试日志条目")
        logger.info(f"发送日志响应: {log_response}")
        
    finally:
        # 断开连接
        await client.disconnect()

if __name__ == "__main__":
    # 运行示例服务器 (实际使用时，服务器和客户端应该在不同的进程或机器上运行)
    # asyncio.run(run_demo_server())
    
    # 运行示例客户端
    # asyncio.run(run_demo_client())
    
    logger.info("请取消注释以上代码来分别运行服务器或客户端示例")