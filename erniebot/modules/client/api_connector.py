#coding=utf-8
"""
API连接器模块 - 处理与API的通信
"""

import time
import hashlib
import json
import datetime
import math
import requests  # 添加到顶层导入
from openai import OpenAI
import logging
import sys # Import sys for logging configuration
from ..config import (
    CACHE_TIME, MAX_RETRIES, RETRY_INTERVAL, 
    MAX_RETRY_INTERVAL, RETRY_CODES
)

class ApiConnector:
    """API连接器类，处理与API的基本通信"""
    
    def __init__(self, api_key, base_url, model_name):
        """初始化API连接器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model_name: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        
        # 配置自定义请求头
        self.headers = {
            "Content-Type": "application/json",
            "Date": self._get_gmt_time(),
        }
        
        # 直接使用requests库发送请求，而不是OpenAI
        self.use_direct_requests = True
        
        # 保留OpenAI客户端作为备选方案
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=self.headers
        )
    
    def _get_gmt_time(self):
        """生成GMT格式的时间字符串，用于请求头"""
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
    
    def call_api(self, messages, cache=None, cache_key=None, stats_callback=None):
        """调用API，处理错误和重试
        
        Args:
            messages: 处理后的消息列表
            cache: 缓存对象，如果需要缓存
            cache_key: 缓存键
            stats_callback: 用于更新统计信息的回调函数
            
        Returns:
            API响应结果
        """
        start_time = time.time()
        success = False
        error_type = None
        
        for retry in range(MAX_RETRIES):
            try:
                # 更新时间头，确保每次请求都有最新的时间
                self.headers["Date"] = self._get_gmt_time()
                
                if self.use_direct_requests:
                    # 使用requests库直接发送请求
                    # 构建请求体
                    request_data = {
                        "model": self.model_name,
                        "messages": messages,
                        "top_p": 0.01,
                    }
                    
                    # 添加认证头
                    headers = self.headers.copy()
                    headers["Authorization"] = f"Bearer {self.api_key}"
                    
                    # 发送POST请求 - 增加超时时间
                    endpoint = f"{self.base_url}/chat/completions"
                    # print(f"直接调用API: {endpoint}") # Replaced by logging
                    logging.info(f"Attempting API call (Retry {retry+1}/{MAX_RETRIES}) to endpoint: {endpoint}")
                    logging.debug(f"Request Headers: {headers}")
                    logging.debug(f"Request Body Size: {len(json.dumps(request_data))} bytes")
                    
                    call_start_time = time.time()
                    # 修改超时设置：连接超时20秒，读取超时120秒
                    response = requests.post(
                        endpoint,
                        json=request_data, 
                        headers=headers,
                        allow_redirects=True,
                        timeout=(20, 300)  # 增加超时时间：(连接超时, 读取超时 300s)
                    )
                    call_duration = time.time() - call_start_time
                    logging.info(f"API call completed in {call_duration:.2f} seconds with status code: {response.status_code}")
                    
                    # 检查状态码
                    if response.status_code != 200:
                        # Log detailed error before raising exception
                        logging.error(f"API Error: Status Code {response.status_code}, Response: {response.text}")
                        raise Exception(f"API返回非200状态码: {response.status_code}, 响应: {response.text}")
                    
                    # 解析JSON响应
                    response_data = response.json()
                    result = response_data['choices'][0]['message']['content']
                else:
                    # 使用OpenAI客户端 - 增加超时设置
                    logging.info(f"Attempting API call via OpenAI client (Retry {retry+1}/{MAX_RETRIES})")
                    logging.debug(f"Request Headers (OpenAI): {self.headers}")
                    call_start_time = time.time()
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        top_p=0.01,
                        extra_headers=self.headers,
                        timeout=300  # 增加超时时间到300秒
                    )
                    call_duration = time.time() - call_start_time
                    logging.info(f"OpenAI API call completed in {call_duration:.2f} seconds.")
                    result = response.choices[0].message.content

                # 缓存结果
                if cache and cache_key:
                    cache.put(cache_key, result, CACHE_TIME)
                
                success = True
                return result
            except Exception as e:
                error_str = str(e)
                # print(f"API调用错误 (重试 {retry+1}/{MAX_RETRIES}): {error_str}") # Replaced by logging
                logging.warning(f"API call failed (Retry {retry+1}/{MAX_RETRIES}): {error_str}", exc_info=True) # Log exception info
                
                # 如果是OpenAI客户端模式失败，尝试切换到requests直接请求模式
                if not self.use_direct_requests and "302" in error_str or "redirect" in error_str.lower():
                    print("检测到重定向错误，切换到直接请求模式...")
                    self.use_direct_requests = True
                    continue
                
                # 日期头问题特殊处理
                if "date" in error_str.lower() or "x-bce-date" in error_str.lower():
                    print("检测到日期头错误，更新请求头...")
                    # 重建客户端并更新时间头
                    self.headers["Date"] = self._get_gmt_time()
                    self.headers["X-BCE-Date"] = self._get_gmt_time()
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        default_headers=self.headers
                    )
                    # 短暂等待后重试
                    time.sleep(2)
                    continue
                
                # 使用指数退避策略计算等待时间
                # 基础等待时间随重试次数指数增长
                base_wait_time = RETRY_INTERVAL * (2 ** retry)
                # 添加随机抖动以避免多个客户端同时重试
                jitter = 0.1 * base_wait_time * (0.5 - 0.5 * math.cos(retry))
                wait_time = min(base_wait_time + jitter, MAX_RETRY_INTERVAL)
                
                # 特殊处理TPM速率限制
                if "tpm_rate_limit_exceeded" in error_str or "Rate limit reached for TPM" in error_str:
                    error_type = "tpm_limit"
                    wait_time = max(wait_time, 30 + retry * 30)
                    # print(f"⚠️ TPM速率限制，需要等待 {wait_time:.2f} 秒后重试...") # Replaced by logging
                    logging.warning(f"TPM rate limit exceeded. Waiting {wait_time:.2f} seconds before retry...")
                # 对连接错误进行特殊处理
                elif "Connection error" in error_str or "ConnectionError" in error_str:
                    error_type = "connection"
                    # print(f"网络连接错误，等待 {wait_time:.2f} 秒后重试...") # Replaced by logging
                    logging.warning(f"Connection error detected. Waiting {wait_time:.2f} seconds before retry...")
                    # 尝试重置客户端
                    if retry > 1:
                        print("尝试重置API客户端连接...")
                        self.headers["Date"] = self._get_gmt_time()
                        self.client = OpenAI(
                            api_key=self.api_key,
                            base_url=self.base_url,
                            default_headers=self.headers
                        )
                # 如果是访问频率错误或服务器错误
                elif "429" in error_str or "too many requests" in error_str.lower() or any(str(code) in error_str for code in RETRY_CODES):
                    error_type = "rate_limit"
                    wait_time = max(wait_time, 15 + retry * 15)
                    # print(f"⚠️ 请求频率限制，等待 {wait_time:.2f} 秒...") # Replaced by logging
                    logging.warning(f"Rate limit or server error detected. Waiting {wait_time:.2f} seconds before retry...")
                elif "timeout" in error_str.lower():
                    error_type = "timeout"
                    # Increase wait time specifically for timeouts
                    wait_time = max(wait_time, 10 + retry * 10) # Ensure at least 10s wait, increasing
                    # print(f"请求超时，等待 {wait_time:.2f} 秒后重试...") # Replaced by logging
                    logging.warning(f"Request timed out. Waiting {wait_time:.2f} seconds before retry...")
                else:
                    # print(f"其他API错误，等待 {wait_time:.2f} 秒后重试...") # Replaced by logging
                    logging.warning(f"Other API error occurred. Waiting {wait_time:.2f} seconds before retry...")
                
                # 执行等待
                time.sleep(wait_time)
                
                # 最后一次重试
                if retry == MAX_RETRIES - 1:
                    error_type = "other" if error_type is None else error_type
                    result = f"调用AI服务时出错: {error_str}"
        
        # 更新统计信息
        logging.info(f"API call sequence finished. Success: {success}, Total time: {time.time() - start_time:.2f}s, Error Type: {error_type}")
        if stats_callback:
            stats_callback(success, time.time() - start_time, error_type)
        
        return result
    
    def generate_tea_product(self, target_consumers=None, cache=None, stats_callback=None):
        """生成一个符合正山堂品牌调性的红茶产品建议
        
        Args:
            target_consumers: 目标消费群体，如"商务人士"、"传统茶文化爱好者"等
            cache: 缓存对象，如果需要缓存
            stats_callback: 用于更新统计信息的回调函数
            
        Returns:
            生成的产品建议
        """
        if target_consumers:
            prompt = f"""请创建一个符合正山堂品牌调性的创新红茶产品构想，特别适合{target_consumers}群体，包括以下要素：
            1. 产品名称：符合正山堂高端红茶品牌形象的产品名
            2. 产品定位：在正山堂现有产品线中的定位，与金骏眉、正山小种、骏眉红等产品的关系
            3. 茶叶选材：使用的原料、产地（如武夷山桐木关、或全国十三大茶产区之一）、等级和采摘标准
            4. 工艺特点：制茶工艺的创新点或传承特色，参考正山堂400年红茶工艺
            5. 口感描述：香气（花香、果香、蜜香等）、滋味、汤色、回甘等特点
            6. 包装设计：符合正山堂品牌调性的包装形式（如马口铁罐、礼盒等）和设计理念
            7. 价格定位：符合正山堂高端茶品的价格策略（建议零售价格，参考金骏眉50g罐装200-500元、高端礼盒1000-2000元等）
            8. 目标消费群体：详细说明为何特别适合{target_consumers}，考虑其消费习惯与偏好
            9. 场景应用：适合的饮用场景、送礼场合、商务用途等
            10. 文化内涵：如何体现正山堂"源起1568"、"正山精神"等文化价值
            
            最后，请用简洁的2-3句话总结这个产品，这段总结可以直接被复制用于开始模拟测试。
            
            请确保产品构思既有创新性，又能体现正山堂作为中国高端红茶品牌的核心价值。"""
        else:
            prompt = """请创建一个符合正山堂品牌调性的创新红茶产品构想，包括以下要素：
            1. 产品名称：符合正山堂高端红茶品牌形象的产品名
            2. 产品定位：在正山堂现有产品线中的定位，与金骏眉、正山小种、骏眉红等产品的关系
            3. 茶叶选材：使用的原料、产地（如武夷山桐木关、或全国十三大茶产区之一）、等级和采摘标准
            4. 工艺特点：制茶工艺的创新点或传承特色，参考正山堂400年红茶工艺
            5. 口感描述：香气（花香、果香、蜜香等）、滋味、汤色、回甘等特点
            6. 包装设计：符合正山堂品牌调性的包装形式（如马口铁罐、礼盒等）和设计理念
            7. 价格定位：符合正山堂高端茶品的价格策略（建议零售价格，参考金骏眉50g罐装200-500元、高端礼盒1000-2000元等）
            8. 目标消费群体：主要针对哪类消费者，考虑其消费习惯与偏好
            9. 场景应用：适合的饮用场景、送礼场合、商务用途等
            10. 文化内涵：如何体现正山堂"源起1568"、"正山精神"等文化价值
            
            最后，请用简洁的2-3句话总结这个产品，这段总结可以直接被复制用于开始模拟测试。
            
            请确保产品构思既有创新性，又能体现正山堂作为中国高端红茶品牌的核心价值。"""
        
        # 尝试从缓存获取结果
        cache_key = None
        if cache:
            cache_key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
            cached_result = cache.get(cache_key)
            if cached_result:
                print("使用缓存的产品生成结果")
                return cached_result
        
        # 调用API
        messages = [{"role": "user", "content": prompt}]
        return self.call_api(messages, cache, cache_key, stats_callback)
    
    def check_api_connection(self):
        """检查API连接状态
        
        Returns:
            tuple: (bool, str) 连接是否成功，以及可能的错误信息
        """
        try:
            # 构建一个简单的API请求
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {self.api_key}"
            
            # 发送一个OPTIONS请求检查连接状态
            endpoint = f"{self.base_url}/chat/completions"
            response = requests.options(
                endpoint,
                headers=headers,
                timeout=(10, 10)  # 较短的超时时间，只是检查连接
            )
            
            # 也可以发送一个最小的POST请求
            simple_message = [{"role": "user", "content": "Hello"}]
            test_request = {
                "model": self.model_name,
                "messages": simple_message,
                "max_tokens": 5  # 限制token数以加快响应
            }
            
            response = requests.post(
                endpoint,
                json=test_request,
                headers=headers,
                timeout=(10, 20)
            )
            
            # 检查响应
            if response.status_code == 200:
                return True, "API连接正常"
            else:
                return False, f"API连接状态异常: HTTP {response.status_code}, 响应: {response.text[:200]}"
                
        except Exception as e:
            return False, f"API连接检查出错: {str(e)}"