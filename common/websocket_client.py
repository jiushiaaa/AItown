#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一WebSocket客户端模块 - 用于Python客户端
"""

import asyncio
import json
import logging
import time
import random
import sys
from typing import Dict, List, Any, Callable, Optional, Union, Awaitable
from contextlib import suppress

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('websocket_client')

class WebSocketClient:
    """统一WebSocket客户端实现"""
    
    def __init__(self, 
                 url: str = "ws://127.0.0.1:8765",
                 client_type: str = "generic",
                 auto_reconnect: bool = True,
                 reconnect_interval: int = 3,
                 max_reconnect_attempts: int = 15,  # 增加重连次数
                 heartbeat_interval: int = 20,  # 减少心跳间隔
                 connection_timeout: int = 40,
                 send_timeout: int = 10,
                 max_message_size: int = 2 * 1024 * 1024,  # 增加到2MB
                 ping_interval: int = 15,  # ping间隔
                 ping_timeout: int = 10,  # ping超时
                 close_timeout: int = 5):  # 关闭超时
        """初始化WebSocket客户端
        
        Args:
            url: WebSocket服务器URL
            client_type: 客户端类型标识符
            auto_reconnect: 是否自动重连
            reconnect_interval: 重连间隔基础值（秒）
            max_reconnect_attempts: 最大重连尝试次数
            heartbeat_interval: 心跳间隔（秒）
            connection_timeout: 连接超时时间（秒）
            send_timeout: 发送消息超时时间（秒）
            max_message_size: 最大消息大小（字节）
            ping_interval: websocket ping间隔（秒）
            ping_timeout: ping超时时间（秒）
            close_timeout: 关闭连接超时时间（秒）
        """
        self.url = url
        self.client_type = client_type
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        self.send_timeout = send_timeout
        self.max_message_size = max_message_size
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.close_timeout = close_timeout
        
        self.ws: Optional[WebSocketClientProtocol] = None
        self.client_id: Optional[str] = None
        self.connected = False
        self.reconnect_count = 0
        self.reconnecting = False
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self.message_queue: List[Dict] = []
        self.connect_lock = asyncio.Lock()
        
        # 心跳相关
        self.last_heartbeat_sent = 0
        self.last_heartbeat_received = 0
        self.heartbeat_task = None
        self.connection_check_task = None
        self.listen_task = None
        self.heartbeat_miss_count = 0
        self.max_heartbeat_miss = 3  # 允许连续丢失的心跳次数
        
        # 任务清理
        self.tasks = []
        
        # 统计数据
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connection_attempts": 0,
            "successful_connections": 0,
            "connection_errors": 0,
            "last_error": None,
            "last_connection_time": 0,
            "total_uptime": 0
        }
    
    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理函数，参数为 message
        """
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        
        self.handlers[message_type].append(handler)
        logger.info(f"已注册处理器用于消息类型 {message_type}")
    
    async def connect(self) -> bool:
        """连接到WebSocket服务器
        
        Returns:
            bool: 是否成功连接
        """
        # 使用锁防止多个并发连接尝试
        async with self.connect_lock:
            if self.connected and self.ws and not self.ws.closed:
                return True
            
            self.stats["connection_attempts"] += 1
            
            try:
                # 关闭现有连接（如果有）
                await self._close_connection()
                
                logger.info(f"正在连接到WebSocket服务器: {self.url}")
                
                # 使用更多选项增强连接的稳定性
                self.ws = await asyncio.wait_for(
                    websockets.connect(
                        self.url,
                        ping_interval=self.ping_interval,
                        ping_timeout=self.ping_timeout,
                        close_timeout=self.close_timeout,
                        max_size=self.max_message_size,
                        max_queue=64,  # 增大消息队列
                        compression=None,  # 禁用压缩以减少CPU使用
                        open_timeout=15,  # 连接尝试超时时间
                    ),
                    timeout=20  # 比open_timeout稍长，包括DNS解析等全过程
                )
                
                self.connected = True
                self.reconnect_count = 0
                self.heartbeat_miss_count = 0
                current_time = time.time()
                self.last_heartbeat_received = current_time
                self.last_heartbeat_sent = current_time
                self.stats["last_connection_time"] = current_time
                self.stats["successful_connections"] += 1
                
                # 发送客户端类型标识
                await self._send_client_type()
                
                # 启动心跳任务
                self._start_heartbeat_task()
                
                # 启动连接检查任务
                self._start_connection_check_task()
                
                # 启动监听任务
                self._start_listen_task()
                
                logger.info(f"已成功连接到WebSocket服务器: {self.url}")
                return True
                
            except asyncio.TimeoutError:
                error_msg = "连接到WebSocket服务器超时"
                self.stats["connection_errors"] += 1
                self.stats["last_error"] = error_msg
                logger.error(error_msg)
                self.connected = False
                await self._close_connection()
                return False
            except Exception as e:
                error_msg = f"连接到WebSocket服务器失败: {e}"
                self.stats["connection_errors"] += 1
                self.stats["last_error"] = error_msg
                logger.error(error_msg)
                self.connected = False
                await self._close_connection()
                return False
    
    async def _send_client_type(self):
        """发送客户端类型标识"""
        try:
            # 发送客户端类型标识
            await self.send({
                "client_type": self.client_type,
                "timestamp": time.time(),
                "version": "2.1",  # 更新版本信息
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            })
            logger.info(f"已发送客户端类型标识: {self.client_type}")
        except Exception as e:
            logger.error(f"发送客户端类型标识失败: {e}")
    
    def _start_heartbeat_task(self):
        """启动心跳任务"""
        if self.heartbeat_task is None or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.tasks.append(self.heartbeat_task)
            
    def _start_connection_check_task(self):
        """启动连接检查任务"""
        if self.connection_check_task is None or self.connection_check_task.done():
            self.connection_check_task = asyncio.create_task(self._check_connection())
            self.tasks.append(self.connection_check_task)
            
    def _start_listen_task(self):
        """启动监听任务"""
        if self.listen_task is None or self.listen_task.done():
            self.listen_task = asyncio.create_task(self._listen_impl())
            self.tasks.append(self.listen_task)
    
    async def reconnect(self) -> bool:
        """重新连接到WebSocket服务器
        
        Returns:
            bool: 是否成功重连
        """
        # 防止多个重连尝试同时进行
        if self.reconnecting:
            logger.debug("已有重连进程在进行中")
            return False
            
        self.reconnecting = True
        
        try:
            if not self.auto_reconnect:
                logger.info("自动重连已禁用")
                return False
                
            if self.reconnect_count >= self.max_reconnect_attempts:
                logger.error(f"达到最大重连尝试次数({self.max_reconnect_attempts})，停止重连")
                return False
            
            # 确保先前的连接已关闭
            await self._close_connection()
                
            self.connected = False
            self.reconnect_count += 1
            
            # 使用指数退避策略和随机抖动计算等待时间
            backoff = min(self.reconnect_interval * (2 ** (self.reconnect_count - 1)), 60)
            jitter = random.uniform(0, backoff * 0.2)  # 增加随机抖动，避免重连风暴
            wait_time = backoff + jitter
            
            logger.info(f"尝试重连 ({self.reconnect_count}/{self.max_reconnect_attempts})，等待 {wait_time:.2f} 秒...")
            
            # 等待指定时间后重连
            await asyncio.sleep(wait_time)
            
            # 尝试重新连接
            result = await self.connect()
            
            # 如果重连成功且有排队的消息，尝试发送
            if result and self.message_queue:
                # 连接建立后可能需要一些时间才能发送消息
                await asyncio.sleep(0.5)
                await self._process_message_queue()
                
            return result
            
        finally:
            self.reconnecting = False
    
    async def send(self, message: Union[dict, str]) -> bool:
        """发送消息到服务器
        
        Args:
            message: 要发送的消息，字典会被转换为JSON
            
        Returns:
            bool: 是否成功发送
        """
        if not self.connected or not self.ws or self.ws.closed:
            logger.warning("发送失败: 未连接到服务器")
            
            # 将消息加入队列，等待重连后发送
            if isinstance(message, dict) and message.get("type") != "heartbeat":
                # 不将心跳消息加入队列
                if len(self.message_queue) < 100:  # 限制队列大小，防止内存溢出
                    self.message_queue.append(message)
                    logger.info(f"消息已加入队列，当前队列长度: {len(self.message_queue)}")
                else:
                    logger.warning(f"消息队列已满({len(self.message_queue)})，丢弃消息")
            
            # 尝试重连
            if self.auto_reconnect and not self.reconnecting:
                asyncio.create_task(self.reconnect())
                
            return False
        
        try:
            # 处理消息大小限制
            if isinstance(message, dict):
                json_message = json.dumps(message)
                message_size = len(json_message.encode('utf-8'))  # 获取实际字节大小
                if message_size > self.max_message_size:
                    logger.error(f"消息大小超出限制: {message_size} > {self.max_message_size}")
                    return False
            elif isinstance(message, str):
                message_size = len(message.encode('utf-8'))  # 获取实际字节大小
                if message_size > self.max_message_size:
                    logger.error(f"消息大小超出限制: {message_size} > {self.max_message_size}")
                    return False
                
            # 准备发送的消息
            if isinstance(message, dict):
                send_message = json.dumps(message)
            else:
                send_message = message
            
            # 设置发送超时
            try:
                await asyncio.wait_for(self.ws.send(send_message), timeout=self.send_timeout)
                
                # 更新统计数据
                self.stats["messages_sent"] += 1
                
                # 只有心跳消息更新发送时间
                if isinstance(message, dict) and message.get("type") == "heartbeat":
                    self.last_heartbeat_sent = time.time()
                    
                return True
            except asyncio.TimeoutError:
                error_msg = f"发送消息超时: {message.get('type') if isinstance(message, dict) else 'text'}"
                self.stats["last_error"] = error_msg
                logger.error(error_msg)
                self.connected = False
                await self._handle_connection_lost("发送超时")
                return False
                
        except ConnectionClosedError as e:
            error_msg = f"发送消息失败，连接异常关闭: {e}"
            self.stats["last_error"] = error_msg
            logger.error(error_msg)
            self.connected = False
            await self._handle_connection_lost(f"连接异常关闭: {e}")
            return False
        except ConnectionClosedOK as e:
            error_msg = f"发送消息失败，连接已正常关闭: {e}"
            self.stats["last_error"] = error_msg
            logger.info(error_msg)
            self.connected = False
            await self._handle_connection_lost("连接已正常关闭")
            return False
        except Exception as e:
            error_msg = f"发送消息失败: {e}"
            self.stats["last_error"] = error_msg
            logger.error(error_msg)
            self.connected = False
            await self._handle_connection_lost(f"未知错误: {e}")
            return False
    
    async def _process_message_queue(self):
        """处理消息队列中的消息"""
        if not self.message_queue:
            return
            
        logger.info(f"开始处理队列中的 {len(self.message_queue)} 条消息")
        
        # 创建队列的副本，避免处理过程中的修改
        messages_to_send = list(self.message_queue)
        self.message_queue.clear()
        
        # 逐条发送队列中的消息
        sent_count = 0
        for queued_msg in messages_to_send:
            if not await self.send(queued_msg):
                # 如果发送失败，将剩余消息重新加入队列
                remaining = messages_to_send[messages_to_send.index(queued_msg):]
                if len(remaining) + len(self.message_queue) <= 100:  # 保持队列大小限制
                    self.message_queue = remaining + self.message_queue
                    logger.warning(f"队列消息发送失败，{len(remaining)}条消息重新加入队列")
                else:
                    discard_count = len(remaining) + len(self.message_queue) - 100
                    self.message_queue = remaining[:len(remaining)-discard_count] + self.message_queue
                    logger.warning(f"队列消息发送失败，由于队列大小限制，丢弃{discard_count}条消息")
                break
            
            sent_count += 1
            # 每条消息之间稍微暂停，避免消息风暴
            await asyncio.sleep(0.1)
            
        logger.info(f"队列处理完成，成功发送{sent_count}条消息")
    
    async def _handle_connection_lost(self, reason: str = "未知原因"):
        """处理连接丢失情况
        
        Args:
            reason: 连接丢失的原因
        """
        if not self.connected:
            # 已经处于断开状态，避免重复处理
            return
            
        self.connected = False
        logger.warning(f"连接丢失: {reason}")
        
        # 更新统计数据
        current_time = time.time()
        if self.stats["last_connection_time"] > 0:
            self.stats["total_uptime"] += current_time - self.stats["last_connection_time"]
        
        # 取消所有相关任务
        await self._cancel_tasks()
        
        # 尝试重连
        if self.auto_reconnect and not self.reconnecting:
            asyncio.create_task(self.reconnect())
    
    async def _heartbeat_loop(self):
        """心跳循环，定期发送心跳消息"""
        while self.running and not self.reconnecting:
            try:
                if self.connected and self.ws and not self.ws.closed:
                    # 发送心跳
                    await self.send({
                        "type": "heartbeat",
                        "timestamp": time.time(),
                        "client_id": self.client_id
                    })
                    logger.debug("已发送心跳")
                
                # 等待下一次心跳
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                logger.debug("心跳任务被取消")
                break
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                await asyncio.sleep(1)  # 失败后短暂等待
    
    async def _check_connection(self):
        """检查连接状态，处理心跳超时和连接问题"""
        while self.running and not self.reconnecting:
            try:
                if not self.connected:
                    await asyncio.sleep(2)
                    continue
                    
                current_time = time.time()
                
                # 检查心跳响应超时
                if (self.last_heartbeat_received > 0 and 
                    current_time - self.last_heartbeat_received > self.connection_timeout):
                    logger.warning(f"超过 {self.connection_timeout} 秒未收到心跳响应，认为连接已断开")
                    await self._handle_connection_lost("心跳响应超时")
                
                # 检查心跳发送超时（确保心跳任务正常运行）
                if (self.last_heartbeat_sent > 0 and
                    current_time - self.last_heartbeat_sent > self.heartbeat_interval * 2):
                    logger.warning(f"心跳发送异常，尝试重启心跳任务")
                    self._start_heartbeat_task()
                
                # 检查WebSocket连接状态
                if self.ws and self.ws.closed:
                    logger.warning("WebSocket连接已关闭，但状态仍为连接中")
                    await self._handle_connection_lost("WebSocket连接已关闭")
                
                # 执行连接健康检查
                try:
                    if self.ws and not self.ws.closed:
                        # 尝试发送ping来检查连接
                        pong_waiter = await self.ws.ping()
                        await asyncio.wait_for(pong_waiter, timeout=self.ping_timeout)
                except Exception as e:
                    logger.warning(f"连接健康检查失败: {e}")
                    await self._handle_connection_lost(f"连接健康检查失败: {e}")
                
                # 检查间隔
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.debug("连接检查任务被取消")
                break
            except Exception as e:
                logger.error(f"连接检查异常: {e}")
                await asyncio.sleep(5)
    
    async def _listen_impl(self):
        """内部监听实现"""
        if not self.connected or not self.ws or self.ws.closed:
            logger.warning("无法监听: 未连接到服务器")
            return
        
        try:
            async for message in self.ws:
                try:
                    # 更新最后一次收到消息的时间
                    self.last_heartbeat_received = time.time()
                    self.heartbeat_miss_count = 0  # 重置心跳丢失计数
                    
                    # 检查消息大小
                    message_size = len(message if isinstance(message, bytes) else message.encode('utf-8'))
                    if message_size > self.max_message_size:
                        logger.warning(f"收到超大消息: {message_size} 字节，已截断")
                        message = message[:self.max_message_size]
                    
                    # 更新统计数据
                    self.stats["messages_received"] += 1
                    
                    # 处理接收到的消息
                    await self._process_message(message)
                        
                except json.JSONDecodeError:
                    logger.error(f"无效的JSON消息: {message[:200]}...")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        
        except ConnectionClosedOK:
            logger.info("连接正常关闭")
            self.connected = False
            await self._handle_connection_lost("连接正常关闭")
        
        except ConnectionClosedError as e:
            logger.warning(f"连接异常关闭: {e}")
            self.connected = False
            await self._handle_connection_lost(f"连接异常关闭: {e}")
        
        except Exception as e:
            logger.error(f"监听过程中出错: {e}")
            self.connected = False
            await self._handle_connection_lost(f"监听错误: {e}")
    
    async def _process_message(self, message: str):
        """处理接收到的消息
        
        Args:
            message: 接收到的消息
        """
        try:
            data = json.loads(message)
            
            # 处理心跳响应
            if data.get('type') == 'heartbeat':
                logger.debug("收到心跳响应")
                return
            
            # 检查是否是连接确认消息
            if data.get('type') == 'connection_established':
                self.client_id = data.get('client_id')
                logger.info(f"连接已确认，客户端ID: {self.client_id}")
                
                # 发送队列中的消息
                if self.message_queue:
                    await self._process_message_queue()
                
                return
            
            # 处理错误消息
            if data.get('type') == 'error':
                error_msg = data.get('message', '未知错误')
                logger.error(f"收到服务器错误: {error_msg}")
                self.stats["last_error"] = f"服务器错误: {error_msg}"
                return
            
            # 处理消息类型
            if 'type' in data:
                msg_type = data['type']
                
                # 调用对应的消息处理器
                if msg_type in self.handlers:
                    for handler in self.handlers[msg_type]:
                        try:
                            # 检查是否是协程函数
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)
                        except Exception as e:
                            logger.error(f"执行处理器时出错: {e}")
                else:
                    logger.warning(f"未处理的消息类型: {msg_type}")
            else:
                logger.warning(f"消息缺少类型字段: {data}")
        except json.JSONDecodeError:
            # 尝试处理非JSON格式的消息
            logger.warning(f"收到非JSON格式消息: {message[:100]}...")
            
            # 调用特殊处理器（如果存在）
            if "raw_message" in self.handlers:
                for handler in self.handlers["raw_message"]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        logger.error(f"执行原始消息处理器时出错: {e}")
    
    async def listen(self):
        """监听接收的消息"""
        while self.running:
            try:
                if self.connected and self.ws and not self.ws.closed:
                    # 使用独立的实现函数
                    await self._listen_impl()
                    
                # 如果监听循环退出，但客户端仍在运行，尝试重连
                if self.running and self.auto_reconnect and not self.reconnecting:
                    logger.info("监听循环退出，尝试重连")
                    await asyncio.sleep(1)  # 短暂暂停，避免立即重连
                    await self.reconnect()
                else:
                    # 如果不需要重连，等待一会再检查
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                logger.debug("监听任务被取消")
                break
            except Exception as e:
                logger.error(f"监听任务异常: {e}")
                await asyncio.sleep(2)  # 出错后短暂等待
    
    async def _close_connection(self):
        """关闭现有连接"""
        if self.ws:
            try:
                # 取消所有相关任务
                await self._cancel_tasks()
                
                # 关闭WebSocket连接
                if not self.ws.closed:
                    await asyncio.wait_for(self.ws.close(), timeout=self.close_timeout)
            except asyncio.TimeoutError:
                logger.warning("关闭WebSocket连接超时")
            except Exception as e:
                logger.debug(f"关闭WebSocket连接时出错: {e}")
            finally:
                self.ws = None
    
    async def _cancel_tasks(self):
        """取消所有任务"""
        for task in self.tasks:
            if task and not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
                    
        self.tasks.clear()
        self.heartbeat_task = None
        self.connection_check_task = None
        self.listen_task = None
    
    async def start(self):
        """启动客户端"""
        self.running = True
        
        # 先连接到服务器
        if await self.connect():
            # 然后开始监听消息
            await self.listen()
    
    async def stop(self):
        """停止客户端"""
        logger.info("正在停止WebSocket客户端...")
        self.running = False
        
        # 取消所有任务
        await self._cancel_tasks()
        
        # 关闭连接
        await self._close_connection()
        
        self.connected = False
        
        # 更新统计数据
        current_time = time.time()
        if self.stats["last_connection_time"] > 0:
            self.stats["total_uptime"] += current_time - self.stats["last_connection_time"]
            
        logger.info("WebSocket客户端已停止")
    
    def get_stats(self) -> Dict:
        """获取客户端统计数据
        
        Returns:
            Dict: 客户端统计数据
        """
        # 如果客户端仍在连接，更新累计在线时间
        if self.connected and self.stats["last_connection_time"] > 0:
            current_uptime = time.time() - self.stats["last_connection_time"]
            total_uptime = self.stats["total_uptime"] + current_uptime
        else:
            total_uptime = self.stats["total_uptime"]
            
        return {
            **self.stats,
            "current_uptime": time.time() - self.stats["last_connection_time"] if self.connected else 0,
            "total_uptime": total_uptime,
            "connection_status": "connected" if self.connected else "disconnected",
            "reconnect_count": self.reconnect_count,
            "message_queue_size": len(self.message_queue),
            "client_id": self.client_id
        }
    
    def run_forever(self):
        """同步方式运行客户端，直到被中断"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logger.info("客户端被用户中断")
        except Exception as e:
            logger.error(f"客户端运行异常: {e}")
        finally:
            if self.connected or self.running:
                loop.run_until_complete(self.stop())
                
            # 取消所有剩余任务
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
                
            # 运行事件循环直到所有任务取消
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
            loop.close()

# 消息处理器示例
def message_handler(message):
    """示例消息处理器"""
    logger.info(f"收到消息: {message}")

# 测试客户端
if __name__ == "__main__":
    client = WebSocketClient(
        client_type="test_client",
        heartbeat_interval=10,  # 更频繁的心跳用于测试
        connection_timeout=30,  # 较短的超时时间用于测试
    )
    client.register_handler("echo_response", message_handler)
    
    # 发送测试消息的协程
    async def send_test_messages(client):
        # 等待连接成功
        await asyncio.sleep(1)
        
        # 发送测试消息
        await client.send({
            "type": "echo",
            "message": "Hello, WebSocket!",
            "timestamp": time.time()
        })
    
    # 运行测试
    loop = asyncio.get_event_loop()
    try:
        # 启动客户端
        client_task = loop.create_task(client.start())
        
        # 发送测试消息
        loop.create_task(send_test_messages(client))
        
        # 运行直到被中断
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    finally:
        # 停止客户端
        loop.run_until_complete(client.stop())
        loop.close() 