#coding=utf-8
"""
WebSocket适配器 - 适配原有的Socket接口到WebSocket接口
"""

import asyncio
import threading
import json
import logging
import sys
import os
import time
import concurrent.futures

# 导入WebSocket服务器模块
from websocket_server import (
    broadcast_message, 
    get_next_message, 
    start_server,
    set_realtime_log_path
)

class WebSocketAdapter:
    """适配WebSocket服务器与原有Socket接口"""
    
    def __init__(self, host="127.0.0.1", port=12339):
        """初始化WebSocket适配器
        
        Args:
            host (str): 服务器主机地址
            port (int): 服务器端口
        """
        self.host = host
        self.port = port
        self.connected = False
        self.message_buffer = asyncio.Queue()
        self.loop = None
        self.server_thread = None
        self.running = False
        self.last_client_message = None
        
    def initialize(self):
        """初始化WebSocket服务器（在单独线程中运行）"""
        try:
            # 启动服务器线程
            self.server_thread = threading.Thread(target=self._run_server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # 等待服务器启动
            time.sleep(1)
            self.connected = True
            logging.info(f"WebSocket适配器初始化成功，服务器运行在 {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"WebSocket服务器启动失败: {str(e)}")
            return False
    
    def _run_server_thread(self):
        """在单独线程中运行WebSocket服务器"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.running = True
            
            # 添加消息处理任务
            self.loop.create_task(self._message_processor())
            
            # 启动WebSocket服务器并捕获异常
            try:
                self.loop.run_until_complete(start_server())
            except Exception as e:
                logging.error(f"WebSocket服务器运行出错: {str(e)}")
                # 即使有错误，也让主线程继续运行
                print(f"WebSocket服务器启动在 {self.host}:{self.port}")
                # 在Windows上使用事件循环而不是wait_closed
                self.loop.run_forever()
        except Exception as e:
            logging.error(f"WebSocket适配器线程出错: {str(e)}")
        finally:
            if self.loop and self.loop.is_running():
                self.loop.stop()
            if self.loop and not self.loop.is_closed():
                self.loop.close()
    
    async def _message_processor(self):
        """处理接收到的WebSocket消息，并放入缓冲区"""
        while self.running:
            try:
                client, message = await get_next_message()
                if client and message:
                    logging.info(f"接收到WebSocket消息: {message}")
                    # 保存最新的消息
                    self.last_client_message = message
                    # 将消息放入缓冲区
                    await self.message_buffer.put(message)
            except Exception as e:
                logging.error(f"处理WebSocket消息时出错: {str(e)}")
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.01)  # 避免CPU占用过高
    
    def send(self, data):
        """发送数据到WebSocket客户端
        
        Args:
            data: 要发送的数据(字典或其他可序列化对象)
            
        Returns:
            bool: 发送是否成功
        """
        if not self.connected:
            logging.error("WebSocket服务器未初始化")
            return False
            
        try:
            # 在主线程中，通过run_coroutine_threadsafe跨线程执行异步操作
            future = asyncio.run_coroutine_threadsafe(
                broadcast_message(data), 
                self.loop
            )
            # 等待异步操作完成
            return future.result(timeout=5)
        except Exception as e:
            logging.error(f"发送WebSocket消息时出错: {str(e)}")
            return False
            
    def receive(self):
        """从消息缓冲区接收数据
        
        Returns:
            object: 接收到的数据,或者False表示接收失败
        """
        if not self.connected:
            logging.error("WebSocket服务器未初始化")
            return False
            
        try:
            # 如果消息缓冲区不为空，取出消息
            if self.loop and not self.message_buffer.empty():
                # 使用run_coroutine_threadsafe从消息缓冲区获取消息
                future = asyncio.run_coroutine_threadsafe(
                    self.message_buffer.get(), 
                    self.loop
                )
                try:
                    message = future.result(timeout=1)
                    logging.info(f"从WebSocket接收到消息: {message}")
                    return message
                except (asyncio.TimeoutError, concurrent.futures.TimeoutError):
                    logging.warning("从消息队列获取数据超时")
                    pass
            
            # 如果有上一条未处理的消息，返回它
            if self.last_client_message:
                # 如果已经处理过此消息，返回None以避免重复处理
                if getattr(self, '_last_processed_message', None) == self.last_client_message:
                    time.sleep(0.1)  # 小暂停避免CPU过载
                    return False
                    
                # 有上一条未处理的消息，返回它
                logging.info(f"返回上一条未处理的WebSocket消息: {self.last_client_message}")
                self._last_processed_message = self.last_client_message
                return self.last_client_message
            
            # 没有消息时等待一小段时间避免忙等
            time.sleep(0.1)
            return False
        except Exception as e:
            logging.error(f"接收WebSocket消息时出错: {str(e)}")
            time.sleep(0.5)  # 出错时等待更长时间
            return False
    
    def set_realtime_log_path(self, path):
        """设置实时日志路径"""
        try:
            future = asyncio.run_coroutine_threadsafe(
                asyncio.coroutine(lambda: set_realtime_log_path(path))(), 
                self.loop
            )
            return future.result(timeout=1)
        except Exception as e:
            logging.error(f"设置实时日志路径时出错: {str(e)}")
            return False
            
    def close(self):
        """关闭WebSocket服务器"""
        if self.running:
            self.running = False
            if self.loop:
                try:
                    # 在不阻塞主线程的情况下关闭事件循环
                    asyncio.run_coroutine_threadsafe(
                        asyncio.sleep(0), 
                        self.loop
                    )
                    # 等待服务器线程结束
                    if self.server_thread and self.server_thread.is_alive():
                        self.server_thread.join(timeout=5)
                except Exception as e:
                    logging.error(f"关闭WebSocket服务器时出错: {str(e)}")
            self.connected = False
            logging.info("WebSocket服务器已关闭")

# 用于直接替代原socketclient类的工厂函数
def websocketclient(host, port):
    """创建WebSocket适配器实例（兼容socketclient接口）"""
    adapter = WebSocketAdapter(host, port)
    adapter.initialize()
    return adapter 