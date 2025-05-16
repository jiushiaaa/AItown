#coding=utf-8
"""
API客户端模块 - 封装与OpenAI兼容API的通信
"""

import re
import ast
import json
import datetime
import time
import random
import hashlib
from collections import OrderedDict
from openai import OpenAI
# --- MODIFIED: Change relative config import to absolute ---
# from ..config import (API_KEY, BASE_URL, MODEL_NAME, SYSTEM_PROMPT,
#                      REQUEST_TIMEOUT, REQUEST_INTERVAL, MAX_RETRIES, RETRY_INTERVAL,
#                      CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, MAX_RETRY_INTERVAL,
#                      RETRY_CODES, CACHE_ENABLED, CACHE_TIME, BATCH_SIZE, BATCH_COUNT,
#                      SIMPLIFIED_PROMPT)
# Assuming the config values are in erniebot/config_integration.py
from config_integration import (MODEL_API_KEY as API_KEY, BASE_URL, MODEL_NAME, SYSTEM_PROMPT, # Changed API_KEY to MODEL_API_KEY and aliased it
                                         REQUEST_TIMEOUT, REQUEST_INTERVAL, MAX_RETRIES, RETRY_INTERVAL,
                                         CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, MAX_RETRY_INTERVAL,
                                         RETRY_CODES, CACHE_ENABLED, CACHE_TIME, BATCH_SIZE, BATCH_COUNT,
                                         SIMPLIFIED_PROMPT)
# --- END MODIFIED ---
import requests

# 导入本地模块 (These relative imports should be fine)
from .cache import LRUCache
from .message_processor import MessageProcessor
from .api_connector import ApiConnector
from .simulation_handler import SimulationHandler
from .utils import extract_json, get_cache_key

class ApiClient:
    """API客户端类，负责与AI服务通信"""
    
    def __init__(self):
        """初始化API客户端"""
        # 初始化连接器
        self.connector = ApiConnector(API_KEY, BASE_URL, MODEL_NAME)
        
        # 初始化对话历史
        self.messages = [
            {
                "role": "user",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "assistant",
                "content": "我可以帮您模拟正山堂茶业消费者的真实消费行为。请提供您想要测试的新品红茶信息，包括茶品名称、特色、价格定位、包装形式、口感特点等关键信息。\n\n您也可以：\n1. 输入\"生成产品\"，我会帮您创建一个符合正山堂品牌调性的创新红茶产品建议\n2. 输入\"为商务人士生成产品\"、\"为传统茶文化爱好者生成产品\"等，我会为特定消费群体创建产品\n\n之后您可以直接使用或修改我的建议，开始消费者行为模拟测试。"
            }
        ]
        
        # 初始化处理器
        self.message_processor = MessageProcessor()
        self.simulator = SimulationHandler(self.connector)
        
        self.json_block_regex = re.compile(r"```(.*?)```", re.DOTALL)
        self.last_request_time = 0  # 记录上次请求时间
        self.request_stats = {
            "total": 0,
            "success": 0,
            "failures": 0,
            "timeouts": 0,
            "avg_response_time": 0
        }
        
        # 初始化缓存
        self.cache = LRUCache(100)
    
    def chat(self, message):
        """发送消息到AI API并获取响应"""
        if isinstance(message, str):
            message = {"role": "user", "content": message}
        self.messages.append(message)
        
        # 消息历史管理 - 如果历史过长，清理非重要消息
        if len(self.messages) > 40:
            self.message_processor.trim_message_history(self.messages)
        
        # 确保请求间隔
        self._ensure_request_interval()
        
        # 处理消息格式，文心一言不支持system角色
        processed_messages = self.message_processor.process_messages_for_erniebot(self.messages)
        
        # 尝试从缓存获取结果
        cache_key = get_cache_key(processed_messages)
        if CACHE_ENABLED:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                print("使用缓存结果")
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": cached_result,
                    }
                )
                return cached_result
        
        # 调用API获取结果
        result = self.connector.call_api(
            processed_messages, 
            self.cache if CACHE_ENABLED else None,
            cache_key,
            self._update_stats
        )
        
        # 更新消息历史
        if result and not result.startswith("调用AI服务时出错"):
            self.messages.append({
                "role": "assistant",
                "content": result,
            })
            # 记录成功请求时间，用于下次间隔
            self.last_request_time = time.time()
            
        return result
            
    def chat_with_messages(self, messages):
        """使用提供的完整消息列表调用API，不修改内部历史"""
        # 确保请求间隔
        self._ensure_request_interval()
        
        # 处理消息格式，文心一言不支持system角色
        processed_messages = self.message_processor.process_messages_for_erniebot(messages)
        
        # 尝试从缓存获取结果
        cache_key = get_cache_key(processed_messages)
        if CACHE_ENABLED:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                print("使用缓存结果")
                
                # 将交互添加到历史中
                for msg in messages:
                    if msg not in self.messages:
                        self.messages.append(msg)
                
                # 添加响应到历史
                self.messages.append({
                    "role": "assistant",
                    "content": cached_result,
                })
                
                return cached_result
        
        # 检查是否有模拟消费者行为的系统提示，如有则可能需要分批处理
        is_simulation_prompt = any("消费者行为模拟" in msg.get("content", "") 
                                 for msg in messages if msg.get("role") == "system")
        
        if is_simulation_prompt and len(messages) > 2:
            print("检测到消费者行为模拟请求，使用分批处理...")
            result = self.simulator.batch_process_simulation(
                messages, 
                self.cache if CACHE_ENABLED else None,
                self._update_stats
            )
        else:
            # 调用API获取结果
            result = self.connector.call_api(
                processed_messages, 
                self.cache if CACHE_ENABLED else None,
                cache_key,
                self._update_stats
            )
        
        # 更新消息历史
        if result and not result.startswith("调用AI服务时出错"):
            # 将交互添加到历史中
            for msg in messages:
                if msg not in self.messages:
                    self.messages.append(msg)
            
            # 添加响应到历史
            self.messages.append({
                "role": "assistant",
                "content": result,
            })
            
            # 记录成功请求时间
            self.last_request_time = time.time()
            
        return result

    def _ensure_request_interval(self):
        """确保请求之间有足够的间隔时间"""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            
            # 根据消息数量动态调整请求间隔
            base_interval = REQUEST_INTERVAL
            if len(self.messages) > 30:
                # 消息量大时增加等待时间
                messages_factor = min(len(self.messages) / 10, 3)  # 最多增加3倍
                dynamic_interval = base_interval * (1 + messages_factor * 0.5)
                required_interval = max(base_interval, dynamic_interval)
            else:
                required_interval = base_interval
                
            if elapsed < required_interval:
                wait_time = required_interval - elapsed
                print(f"等待 {wait_time:.2f} 秒以避免请求过于频繁...")
                time.sleep(wait_time)
                
            # 如果已经收到过频率限制错误，增加额外等待时间
            if self.request_stats.get("rate_limits", 0) > 0:
                extra_wait = min(self.request_stats.get("rate_limits", 0) * 2, 30)
                print(f"由于之前的频率限制，额外等待 {extra_wait} 秒...")
                time.sleep(extra_wait)
    
    def _update_stats(self, success, duration, error_type=None):
        """更新请求统计信息"""
        self.request_stats["total"] += 1
        if success:
            self.request_stats["success"] += 1
        else:
            self.request_stats["failures"] += 1
            if error_type == "timeout":
                self.request_stats["timeouts"] = self.request_stats.get("timeouts", 0) + 1
            elif error_type == "rate_limit" or error_type == "tpm_limit":
                self.request_stats["rate_limits"] = self.request_stats.get("rate_limits", 0) + 1
        
        # 更新平均响应时间
        self.request_stats["avg_response_time"] = (
            (self.request_stats["avg_response_time"] * (self.request_stats["total"]-1) + duration) 
            / self.request_stats["total"]
        )
        
        # 输出当前统计信息
        print(f"API请求统计: 总请求:{self.request_stats['total']} 成功:{self.request_stats['success']} " 
              f"失败:{self.request_stats['failures']} 超时:{self.request_stats.get('timeouts', 0)} " 
              f"频率限制:{self.request_stats.get('rate_limits', 0)} "
              f"平均响应时间:{self.request_stats['avg_response_time']:.2f}秒")

    def generate_tea_product(self, target_consumers=None):
        """生成一个符合正山堂品牌调性的红茶产品建议
        
        Args:
            target_consumers: 目标消费群体，如"商务人士"、"传统茶文化爱好者"等
        """
        return self.connector.generate_tea_product(target_consumers, self.cache, self._update_stats)

    def extract_json(self, content):
        """从API响应中提取JSON数据"""
        return extract_json(content, self.json_block_regex)

    def extract_info(self, json_str):
        """提取请求类型和内容"""
        try:
            if not isinstance(json_str, dict):
                print(f"extract_info收到非字典类型数据: {type(json_str)}")
                return False, False
                
            if "type" not in json_str:
                print("json_str中没有'type'字段")
                return False, False
                
            if json_str["type"] == "question":
                if "question" not in json_str:
                    return False, False
                return True, json_str["question"]
                
            if json_str["type"] == "response":
                if "response" not in json_str:
                    return False, False
                return False, json_str["response"]
                
            return False, False
        except Exception as e:
            print(f"提取信息时出错: {str(e)}")
            return False, False

    def generate_prompt(self, history, consumer_data=None):
        """生成提示词"""
        return self.message_processor.generate_prompt(history, consumer_data, SYSTEM_PROMPT)

    def get_system_prompt(self):
        """获取系统提示词"""
        return SYSTEM_PROMPT