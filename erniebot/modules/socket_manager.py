#coding=utf-8
"""
Socket通信管理模块 - 负责与Socket客户端的通信
"""

import json
import time
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from socketplus import socketclient
import logging
from .config import VALID_LOCATIONS  # 导入config中定义的场所

class SocketManager:
    """Socket通信管理类"""
    
    def __init__(self, host="127.0.0.1", port=12339):
        """初始化Socket管理器
        
        Args:
            host (str): 服务器主机地址
            port (int): 服务器端口
        """
        self.host = host
        self.port = port
        self.socket_client = None
        self.max_retries = 3
        self.connected = False
        self.realtime_log_path = None
        logging.info(f"SocketManager初始化: {self.host}:{self.port}")
        
    def initialize(self):
        """初始化Socket连接"""
        try:
            logging.info(f"正在连接到Socket服务器: {self.host}:{self.port}")
            self.socket_client = socketclient(self.host, self.port)
            self.connected = True
            return True
        except Exception as e:
            logging.error(f"Socket连接失败: {e}")
            return False
    
    def reconnect(self):
        """重新连接Socket"""
        if self.socket_client:
            try:
                self.socket_client.close()
            except:
                pass
        self.socket_client = None
        self.connected = False
        return self.initialize()
    
    def send(self, data):
        """发送数据到客户端
        
        Args:
            data: 要发送的数据(字典或其他可序列化对象)
            
        Returns:
            bool: 发送是否成功
        """
        if self.socket_client is None:
            logging.error("尚未初始化Socket连接")
            return False
            
        try:
            return self.socket_client.send(data)
        except Exception as e:
            logging.error(f"发送数据失败: {e}")
            return False
            
    def receive(self):
        """从客户端接收数据
        
        Returns:
            object: 接收到的数据,或者False表示接收失败
        """
        if self.socket_client is None:
            logging.error("尚未初始化Socket连接")
            return False
            
        try:
            return self.socket_client.recv()
        except Exception as e:
            logging.error(f"接收数据失败: {e}")
            return False
    
    def set_realtime_log_path(self, path):
        """设置实时日志路径"""
        self.realtime_log_path = path
        print(f"已设置实时日志文件路径: {path}")
        return True
            
    def send_product_generated_message(self):
        """发送产品生成成功的消息"""
        result = {
            'resultType': 'product_generated', 
            'message': '已生成品牌建议，请复制到任务框'
        }
        return self.send(result)
    
    def send_simulation_data(self, day, json_data):
        """发送模拟数据到客户端并选择性地写入实时日志"""
        # 创建一个干净的数据结构
        result_data = {
            'resultType': 'task',
            'task': f"第{day}天消费者模拟",  # 任务描述
            'process': day,                # 当前进度
            'time': 30,                    # 总天数
            'tasks': []                    # 任务列表
        }
        
        # 详细记录输入的JSON数据
        logging.info(f"Day {day}: 发送模拟数据, 原始JSON数据: {json.dumps(json_data, ensure_ascii=False)}")
        
        # 使用config.py中定义的有效位置名称
        # 如果位置不匹配，使用默认位置
        default_location = VALID_LOCATIONS[0] if VALID_LOCATIONS else "茶艺体验区"
        
        # 打印所有有效位置，便于调试
        logging.info(f"有效的位置名称: {VALID_LOCATIONS}")
        
        # 为Unity导航系统准备数据：将customer_interactions中的location字段复制到to字段
        if 'customer_interactions' in json_data:
            logging.info(f"Day {day}: 找到 {len(json_data['customer_interactions'])} 个消费者交互数据")
            for customer in json_data['customer_interactions']:
                if 'location' in customer:
                    # 检查location是否有效，如果无效则使用默认位置
                    if customer['location'] not in VALID_LOCATIONS:
                        logging.warning(f"Day {day}: 位置 '{customer['location']}' 无效，使用默认位置 '{default_location}'")
                        customer['location'] = default_location
                    
                    # 添加任务（包含名称、位置映射等信息）
                    task = {
                        'name': customer.get('name', ''),
                        'position': customer.get('location', ''), # 当前位置
                        'to': customer.get('location', ''),       # 目标位置（与location相同）
                        'do_': customer.get('comments', '无'),     # 动作描述
                        'emoji': customer.get('emoji', '👍')       # 表情
                    }
                    result_data['tasks'].append(task)
                    logging.info(f"Day {day}: 添加消费者任务 - 名称: {task['name']}, 位置: {task['position']}, 目标: {task['to']}")
                else:
                    logging.warning(f"Day {day}: 消费者数据缺少location字段: {json.dumps(customer, ensure_ascii=False)}")
        else:
            logging.error(f"Day {day}: JSON数据缺少customer_interactions字段")
        
        # 记录要发送的数据
        logging.info(f"Day {day}: 即将发送任务数据: {json.dumps(result_data, ensure_ascii=False)}")
        
        # 记录数据到实时日志文件(如果已设置)
        if self.realtime_log_path and os.path.exists(self.realtime_log_path):
            try:
                # 读取当前日志
                with open(self.realtime_log_path, "r", encoding="utf-8") as f:
                    realtime_log = json.load(f)
                
                # 添加当天数据
                day_data = {
                    "day": day,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": json_data,
                    "sent_to_client": True
                }
                
                # 检查是否已存在该天的数据，如果存在则更新
                day_exists = False
                for i, existing_day in enumerate(realtime_log.get("days", [])):
                    if existing_day.get("day") == day:
                        realtime_log["days"][i] = day_data
                        day_exists = True
                        break
                
                if not day_exists:
                    # 如果不存在该天的数据，则添加
                    if "days" not in realtime_log:
                        realtime_log["days"] = []
                    realtime_log["days"].append(day_data)
                
                # 写回文件
                with open(self.realtime_log_path, "w", encoding="utf-8") as f:
                    json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                
                print(f"已将第{day}天的模拟数据实时记录到日志文件")
            except Exception as e:
                print(f"实时记录第{day}天的模拟数据时出错: {str(e)}")
        
        # 不再合并原始json_data，仅发送Unity需要的数据
        return self.send(result_data)
    
    def send_simulation_summary(self, summary, prev_cumulative, popularity_score=None):
        """发送模拟总结到客户端"""
        result = {
            'resultType': 'simulationComplete',
            'simulationSummary': summary,
            'totalDays': 30,
            'totalCustomers': prev_cumulative.get('total_customers', 0),
            'totalRevenue': prev_cumulative.get('total_revenue', 0),
            'loyalCustomers': prev_cumulative.get('loyal_customers', 0),
            'productPopularityScore': popularity_score,
        }
        
        # 记录总结到实时日志文件(如果已设置)
        if self.realtime_log_path and os.path.exists(self.realtime_log_path):
            try:
                # 读取当前日志
                with open(self.realtime_log_path, "r", encoding="utf-8") as f:
                    realtime_log = json.load(f)
                
                # 添加总结数据
                realtime_log["simulation_complete"] = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "summary": summary,
                    "totalDays": 30,
                    "totalCustomers": prev_cumulative.get('total_customers', 0),
                    "totalRevenue": prev_cumulative.get('total_revenue', 0),
                    "loyalCustomers": prev_cumulative.get('loyal_customers', 0),
                    "productPopularityScore": popularity_score,
                }
                
                # 写回文件
                with open(self.realtime_log_path, "w", encoding="utf-8") as f:
                    json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                
                print("已将模拟总结记录到实时日志文件")
            except Exception as e:
                print(f"记录模拟总结到实时日志文件时出错: {str(e)}")
        
        return self.send(result)
        
    def wait_for_continue(self):
        """等待用户确认继续"""
        print("等待用户确认继续...")
        retries = 0
        max_retries = 10  # 最多等待10次
        
        while retries < max_retries:
            recv_data = self.receive()
            if recv_data == False:
                retries += 1
                print(f"等待确认失败，尝试重新接收 ({retries}/{max_retries})")
                if retries >= max_retries:
                    print("等待确认超过最大尝试次数，自动继续")
                    return True
                time.sleep(1)  # 等待1秒后重试
                continue
                
            try:
                type_flag, res = False, False
                
                if isinstance(recv_data, dict):
                    if "type" in recv_data:
                        if recv_data["type"] == "response" and "response" in recv_data:
                            type_flag, res = False, recv_data["response"]
                
                if type_flag == False and res == True:
                    print("用户确认继续")
                    return True
            except Exception as e:
                print(f"处理用户确认时出错: {str(e)}")
                continue
        
        return True  # 如果超过最大重试次数，也返回True以继续 