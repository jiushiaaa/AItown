#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一TCP服务器模块 - 供erniebot和data_api使用
"""

import asyncio
import json
import logging
import uuid
import time
import traceback
import socket
import select
import threading
from typing import Dict, List, Any, Callable, Optional, Union
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 使用DEBUG级别获取更多日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('websocket_server.log')
    ]
)
logger = logging.getLogger('TCPServer')

class TCPServer:
    """统一TCP服务器实现"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 12339, 
                heartbeat_interval: int = 30,
                connection_timeout: int = 60):
        """初始化TCP服务器
        
        Args:
            host: 服务器地址
            port: 服务器端口
            heartbeat_interval: 心跳包发送间隔（秒）
            connection_timeout: 连接超时时间（秒）
        """
        self.host = host
        self.port = port
        self.clients = {}  # 客户端连接字典 {client_id: socket}
        self.client_types = {}  # 客户端类型映射，如 "unity", "dashboard" 等
        self.client_last_seen = {}  # 客户端最后活动时间
        self.handlers = {}  # 消息处理器
        self.server_socket = None
        self.running = False
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        self.heartbeat_thread = None
        self.cleanup_thread = None
        self.max_message_size = 1024 * 1024  # 1MB
        self.max_retries = 3
        self.retry_delay = 1.0
        self.client_thread = None
        self.lock = threading.Lock()  # 用于线程安全操作
        
        logger.info(f"TCP服务器初始化: {host}:{port}")
        logger.info(f"心跳间隔: {heartbeat_interval}秒, 连接超时: {connection_timeout}秒")
    
    def handle_client(self, client_socket, address):
        """处理客户端连接
        
        Args:
            client_socket: 客户端socket
            address: 客户端地址
        """
        # 生成客户端ID
        client_id = str(uuid.uuid4())
        with self.lock:
            self.clients[client_id] = client_socket
            self.client_last_seen[client_id] = time.time()
        client_type = "unknown"
        
        logger.info(f"客户端连接: {client_id} 从 {address}")
        logger.info(f"当前连接数: {len(self.clients)}")
        
        try:
            # 发送欢迎消息
            welcome_msg = {
                "type": "welcome",
                "client_id": client_id,
                "message": "欢迎连接到TCP服务器",
                "server_time": time.time()
            }
            self.send_to_client(client_id, welcome_msg)
            logger.info(f"已发送欢迎消息到客户端 {client_id}")
            
            # 处理客户端消息
            data_buffer = b""
            while self.running:
                try:
                    ready = select.select([client_socket], [], [], 1.0)
                    if ready[0]:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            logger.info(f"客户端 {client_id} 关闭连接")
                            break
                        
                        data_buffer += chunk
                        # 更新客户端最后活动时间
                        with self.lock:
                            self.client_last_seen[client_id] = time.time()
                        
                        # 尝试处理完整的JSON消息
                        try:
                            # 检查是否是心跳消息 "ping"
                            if data_buffer == b"ping":
                                client_socket.send(b"pong")
                                logger.debug(f"收到ping,回复pong (客户端: {client_id})")
                                data_buffer = b""
                                continue
                            
                            # 尝试解析JSON
                            message = data_buffer.decode('utf-8')
                            data = json.loads(message)
                            logger.info(f"收到来自客户端 {client_id} 的消息: {data}")
                            data_buffer = b""  # 清空缓冲区
                            
                            # 识别客户端类型
                            if 'client_type' in data:
                                client_type = data['client_type']
                                with self.lock:
                                    self.client_types[client_id] = client_type
                                logger.info(f"客户端 {client_id} 标识为: {client_type}")
                                
                                # 发送确认消息
                                self.send_to_client(client_id, {
                                    "type": "connection_established",
                                    "client_id": client_id,
                                    "message": f"连接已建立 ({client_type})",
                                    "server_time": time.time()
                                })
                                continue
                            
                            # 处理消息类型
                            if 'type' in data:
                                msg_type = data['type']
                                logger.info(f"处理类型 {msg_type} 的消息")
                                
                                # 处理心跳消息
                                if msg_type == "heartbeat":
                                    self.send_to_client(client_id, {
                                        "type": "heartbeat",
                                        "server_time": time.time()
                                    })
                                    logger.debug(f"收到心跳包,已回复 (客户端: {client_id})")
                                    continue
                                
                                # 处理Unity客户端直接发送的问题消息
                                if msg_type == "question":
                                    logger.info(f"收到Unity客户端直接发送的问题消息: {data}")
                                    # 将这种消息路由到task_new处理器
                                    if "task_new" in self.handlers:
                                        for handler in self.handlers["task_new"]:
                                            try:
                                                handler(client_id, data)
                                            except Exception as e:
                                                logger.error(f"处理question消息时出错: {e}")
                                                logger.error(traceback.format_exc())
                                                self.send_error(client_id, f"处理消息时出错: {str(e)}")
                                    else:
                                        logger.warning("未找到task_new处理器，无法处理question类型消息")
                                        self.send_error(client_id, "服务器未配置处理此类消息的处理器")
                                    continue
                                
                                # 调用对应的消息处理器
                                if msg_type in self.handlers:
                                    for handler in self.handlers[msg_type]:
                                        try:
                                            handler(client_id, data)
                                        except Exception as e:
                                            logger.error(f"处理消息时出错: {e}")
                                            logger.error(traceback.format_exc())
                                            self.send_error(client_id, f"处理消息时出错: {str(e)}")
                                else:
                                    logger.warning(f"未处理的消息类型: {msg_type}")
                                    self.send_error(client_id, f"未知的消息类型: {msg_type}")
                            else:
                                logger.warning(f"消息缺少类型字段: {data}")
                                self.send_error(client_id, "消息缺少类型字段")
                                
                        except json.JSONDecodeError as e:
                            # 如果JSON解析失败，可能是数据不完整，继续等待更多数据
                            if len(data_buffer) > self.max_message_size:
                                logger.error(f"消息太大或格式错误，清空缓冲区: {e}")
                                logger.error(f"缓冲区数据: {data_buffer[:100]}...")
                                data_buffer = b""
                                self.send_error(client_id, "消息格式错误或太大")
                        except UnicodeDecodeError as e:
                            logger.error(f"解码错误，清空缓冲区: {e}")
                            data_buffer = b""
                            self.send_error(client_id, "消息编码错误")
                        
                except Exception as e:
                    logger.error(f"处理客户端消息时出错: {e}")
                    logger.error(traceback.format_exc())
                    break
                    
        except Exception as e:
            logger.error(f"处理客户端连接时出错: {e}")
            logger.error(traceback.format_exc())
        finally:
            # 清理客户端连接
            self.remove_client(client_id, client_type)
    
    def remove_client(self, client_id: str, client_type: str = "unknown"):
        """安全地移除客户端连接
        
        Args:
            client_id: 客户端ID
            client_type: 客户端类型
        """
        with self.lock:
            if client_id in self.clients:
                try:
                    # 尝试优雅地关闭连接
                    self.clients[client_id].close()
                except Exception as e:
                    logger.debug(f"关闭连接时出错: {e}")
                    
                del self.clients[client_id]
                
            if client_id in self.client_types:
                del self.client_types[client_id]
                
            if client_id in self.client_last_seen:
                del self.client_last_seen[client_id]
                
        logger.info(f"客户端 {client_id} ({client_type}) 连接已清理")
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理函数，参数为(client_id, message)
        """
        with self.lock:
            if message_type not in self.handlers:
                self.handlers[message_type] = []
            
            self.handlers[message_type].append(handler)
        logger.info(f"已注册处理器用于消息类型 {message_type}")
    
    def send_to_client(self, client_id: str, message: Union[dict, str]) -> bool:
        """发送消息到特定客户端
        
        Args:
            client_id: 客户端ID
            message: 要发送的消息，字典会被转换为JSON
            
        Returns:
            bool: 是否成功发送
        """
        with self.lock:
            if client_id not in self.clients:
                logger.warning(f"客户端 {client_id} 不存在")
                return False
        
        try:
            if isinstance(message, dict):
                message = json.dumps(message, ensure_ascii=False)
            
            data = message.encode('utf-8')
            
            with self.lock:
                client_socket = self.clients.get(client_id)
                if not client_socket:
                    return False
                client_socket.sendall(data)
            
            logger.debug(f"已发送消息到客户端 {client_id}")
            return True
        except Exception as e:
            logger.error(f"发送消息到客户端 {client_id} 时出错: {e}")
            logger.error(traceback.format_exc())
            # 连接可能已关闭，移除客户端
            with self.lock:
                client_type = self.client_types.get(client_id, "unknown")
            self.remove_client(client_id, client_type)
            return False
    
    def broadcast(self, message: Union[dict, str], client_type: Optional[str] = None) -> int:
        """广播消息到所有客户端或特定类型的客户端
        
        Args:
            message: 要发送的消息，字典会被转换为JSON
            client_type: 可选，客户端类型
            
        Returns:
            int: 成功发送的客户端数量
        """
        sent_count = 0
        client_ids = []
        
        with self.lock:
            if client_type:
                # 广播到特定类型的客户端
                for cid, ctype in self.client_types.items():
                    if ctype == client_type:
                        client_ids.append(cid)
            else:
                # 广播到所有客户端
                client_ids = list(self.clients.keys())
        
        for client_id in client_ids:
            if self.send_to_client(client_id, message):
                sent_count += 1
        
        logger.info(f"广播消息到 {sent_count} 个客户端")
        return sent_count
    
    def heartbeat_sender(self):
        """发送心跳包线程"""
        while self.running:
            try:
                current_time = time.time()
                with self.lock:
                    for client_id in list(self.clients.keys()):
                        try:
                            # 发送心跳包
                            self.send_to_client(client_id, {
                                "type": "heartbeat",
                                "server_time": current_time
                            })
                        except Exception as e:
                            logger.error(f"发送心跳包到客户端 {client_id} 时出错: {e}")
            except Exception as e:
                logger.error(f"心跳发送器出错: {e}")
                logger.error(traceback.format_exc())
            
            # 等待下一次心跳
            time.sleep(self.heartbeat_interval)
    
    def connection_cleanup(self):
        """连接清理线程"""
        while self.running:
            try:
                current_time = time.time()
                clients_to_remove = []
                
                with self.lock:
                    # 检查超时的客户端
                    for client_id, last_seen in self.client_last_seen.items():
                        if current_time - last_seen > self.connection_timeout:
                            client_type = self.client_types.get(client_id, "unknown")
                            logger.info(f"客户端 {client_id} ({client_type}) 连接超时")
                            clients_to_remove.append((client_id, client_type))
                
                # 移除超时的客户端
                for client_id, client_type in clients_to_remove:
                    self.remove_client(client_id, client_type)
            except Exception as e:
                logger.error(f"连接清理器出错: {e}")
                logger.error(traceback.format_exc())
            
            # 等待下一次清理
            time.sleep(10)  # 每10秒检查一次
    
    def client_acceptor(self):
        """客户端接受线程"""
        self.server_socket.listen(5)
        logger.info(f"TCP服务器监听在 {self.host}:{self.port}")
        
        while self.running:
            try:
                # 等待新客户端连接
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"新客户端连接来自 {address}")
                    # 为每个客户端创建一个新线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # 超时继续循环
                    continue
                except Exception as e:
                    logger.error(f"接受客户端连接时出错: {e}")
                    if not self.running:
                        break
            except Exception as e:
                logger.error(f"客户端接受器出错: {e}")
                logger.error(traceback.format_exc())
                if not self.running:
                    break
    
    def start(self):
        """启动服务器"""
        if self.running:
            logger.warning("服务器已经在运行")
            return
        
        try:
            # 创建服务器socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # 设置超时以允许正常关闭
            self.server_socket.bind((self.host, self.port))
            
            self.running = True
            
            # 启动客户端接受线程
            self.client_thread = threading.Thread(target=self.client_acceptor)
            self.client_thread.daemon = True
            self.client_thread.start()
            
            # 启动心跳发送线程
            self.heartbeat_thread = threading.Thread(target=self.heartbeat_sender)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
            
            # 启动连接清理线程
            self.cleanup_thread = threading.Thread(target=self.connection_cleanup)
            self.cleanup_thread.daemon = True
            self.cleanup_thread.start()
            
            logger.info("TCP服务器已启动")
        except Exception as e:
            self.running = False
            logger.error(f"启动服务器时出错: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def stop(self):
        """停止服务器"""
        if not self.running:
            logger.warning("服务器已经停止")
            return
        
        self.running = False
        logger.info("正在停止TCP服务器...")
        
        try:
            # 关闭所有客户端连接
            with self.lock:
                for client_id, client_socket in list(self.clients.items()):
                    try:
                        client_socket.close()
                    except Exception as e:
                        logger.debug(f"关闭客户端 {client_id} 连接时出错: {e}")
                
                self.clients.clear()
                self.client_types.clear()
                self.client_last_seen.clear()
            
            # 关闭服务器socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            logger.info("TCP服务器已停止")
        except Exception as e:
            logger.error(f"停止服务器时出错: {e}")
            logger.error(traceback.format_exc())
    
    def send_error(self, client_id: str, error_message: str):
        """发送错误消息到客户端
        
        Args:
            client_id: 客户端ID
            error_message: 错误消息
        """
        error_data = {
            "type": "error",
            "error": error_message,
            "server_time": time.time()
        }
        self.send_to_client(client_id, error_data)

# 兼容性别名，保持API一致性
WebSocketServer = TCPServer

# 测试处理器
def echo_handler(client_id, message):
    """简单的回显处理器,用于测试"""
    print(f"Echo handler received from {client_id}: {message}")
    return message

# 如果直接运行此脚本,启动测试服务器
if __name__ == "__main__":
    print("启动TCP服务器测试...")
    server = TCPServer(host="127.0.0.1", port=12339)
    server.register_handler("echo", echo_handler)
    
    try:
        server.start()
        print("服务器已启动，按 Ctrl+C 停止")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("接收到中断信号，停止服务器")
    finally:
        server.stop()
        print("服务器已停止") 