#coding=utf-8
"""
WebSocket服务器 - 为WebGL客户端提供连接服务
"""

import asyncio
import websockets
import json
import logging
import signal
import time
from datetime import datetime
import sys
import os

# 获取当前脚本的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 将父目录添加到sys.path
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

# 导入配置
from config_integration import HOST, PORT, DEBUG

# 配置日志
logging.basicConfig(level=logging.WARNING if not DEBUG else logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# WebSocket连接状态
connected_clients = set()
message_queue = asyncio.Queue()
realtime_log_path = None

async def handle_client(websocket, path):
    """处理WebSocket客户端连接"""
    global connected_clients
    
    client_id = id(websocket)
    logging.info(f"新的WebSocket客户端连接: {client_id}")
    connected_clients.add(websocket)
    
    # 发送连接确认消息
    confirmation = {
        "type": "question",
        "question": "Unity客户端已连接"
    }
    await websocket.send(json.dumps(confirmation, ensure_ascii=False))
    
    try:
        async for message in websocket:
            try:
                # 解析收到的消息
                data = json.loads(message)
                logging.info(f"收到消息: {data}")
                
                # 将消息放入队列供主程序处理
                await message_queue.put((websocket, data))
                
            except json.JSONDecodeError:
                logging.error(f"无法解析JSON消息: {message}")
                # 尝试发送错误消息
                error_msg = {
                    "type": "error",
                    "message": "无效的JSON格式"
                }
                await websocket.send(json.dumps(error_msg, ensure_ascii=False))
                
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"客户端断开连接: {client_id}")
    finally:
        connected_clients.remove(websocket)

async def broadcast_message(message):
    """向所有连接的客户端广播消息"""
    if not connected_clients:
        logging.warning("没有连接的客户端，无法发送消息")
        return False
    
    # 将消息记录到日志
    if isinstance(message, dict):
        logging.info(f"广播消息: {json.dumps(message, ensure_ascii=False)[:200]}...")
    else:
        logging.info(f"广播消息: {message[:200]}...")
    
    # 记录到实时日志文件(如果已设置)
    if realtime_log_path and os.path.exists(realtime_log_path):
        try:
            # 读取当前日志
            with open(realtime_log_path, "r", encoding="utf-8") as f:
                realtime_log = json.load(f)
            
            # 添加消息记录
            if "messages" not in realtime_log:
                realtime_log["messages"] = []
            
            message_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "direction": "outgoing",
                "message": message
            }
            realtime_log["messages"].append(message_record)
            
            # 写回文件
            with open(realtime_log_path, "w", encoding="utf-8") as f:
                json.dump(realtime_log, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logging.error(f"记录消息到日志文件失败: {e}")
    
    # 发送消息给所有客户端
    if connected_clients:
        message_json = json.dumps(message, ensure_ascii=False)
        await asyncio.gather(
            *[client.send(message_json) for client in connected_clients],
            return_exceptions=True
        )
        return True
    return False

async def get_next_message():
    """从消息队列获取下一条消息"""
    try:
        return await asyncio.wait_for(message_queue.get(), timeout=0.1)
    except asyncio.TimeoutError:
        return None, None

def set_realtime_log_path(path):
    """设置实时日志路径"""
    global realtime_log_path
    realtime_log_path = path
    logging.info(f"已设置WebSocket实时日志路径: {path}")
    return True

async def start_server():
    """启动WebSocket服务器"""
    server = await websockets.serve(
        handle_client, 
        HOST, 
        PORT,
        ping_interval=30,  # 30秒发送一次ping以保持连接
        ping_timeout=10    # 10秒内没有收到pong则认为连接断开
    )
    
    logging.info(f"WebSocket服务器启动在 {HOST}:{PORT}")
    
    # 确保优雅关闭
    loop = asyncio.get_event_loop()
    
    try:
        await server.wait_closed()
    finally:
        logging.info("WebSocket服务器已关闭")

async def shutdown(server):
    """优雅关闭服务器"""
    logging.info("正在关闭WebSocket服务器...")
    server.close()
    await server.wait_closed()
    # 通知所有任务退出
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()

# 示例: 如果直接运行此文件
if __name__ == "__main__":
    logging.info("WebSocket服务器独立运行模式")
    asyncio.run(start_server()) 