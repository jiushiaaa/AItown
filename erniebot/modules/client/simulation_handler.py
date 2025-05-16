#coding=utf-8
"""
模拟处理模块 - 处理消费者行为模拟
"""

import re
import time
import json
import random
from ..config import (BATCH_SIZE, BATCH_COUNT, SIMPLIFIED_PROMPT, 
                     REQUEST_INTERVAL, RETRY_INTERVAL)
from .utils import extract_json

class SimulationHandler:
    """模拟处理器类，处理消费者行为模拟"""
    
    def __init__(self, api_connector):
        """初始化模拟处理器
        
        Args:
            api_connector: API连接器实例
        """
        self.api_connector = api_connector
    
    def batch_process_simulation(self, messages, cache=None, stats_callback=None):
        """将消费者行为模拟分批处理，减少单次请求的复杂度
        
        Args:
            messages: 消息列表
            cache: 缓存对象，如果需要缓存
            stats_callback: 用于更新统计信息的回调函数
            
        Returns:
            合并后的模拟结果
        """
        print("开始分批处理模拟请求...")
        
        # 提取系统提示和用户输入
        system_msgs = [msg for msg in messages if msg.get("role") == "system"]
        system_content = "\n\n".join(msg.get("content", "") for msg in system_msgs)
        
        user_msg = next((msg for msg in messages if msg.get("role") == "user"), {"role": "user", "content": "请模拟下一天的消费者行为"})
        
        # 从系统提示中提取天数
        day_match = re.search(r"第(\d+)天", user_msg.get("content", ""))
        day_number = int(day_match.group(1)) if day_match else 1
        
        # 根据配置决定提示词复杂度
        if SIMPLIFIED_PROMPT:
            # 使用简化提示词，减少请求复杂度
            modified_prompt = f"""请模拟正山堂茶业的消费者行为数据，第{day_number}天。
            请只模拟{BATCH_SIZE}位消费者，确保包含不同类型（传统茶文化爱好者/品质生活追求者/商务人士/健康生活主义者/年轻新贵）。
            必须使用JSON格式，包含store_name、day、daily_stats、customer_interactions字段。
            请确保数据真实合理且结构完整。"""
        else:
            # 修改系统提示，每次只模拟少量消费者
            modified_prompt = system_content.replace("每一天至少要展现7-10位不同消费者的行为", f"每次请只模拟{BATCH_SIZE}位不同消费者的行为")
        
        # 分批处理的结果
        all_batches = []
        batch_count = BATCH_COUNT  # 使用配置中的批次数量
        
        for batch in range(batch_count):
            print(f"处理第 {batch+1}/{batch_count} 批消费者...")
            
            # 更新提示词，指定当前批次
            batch_prompt = f"{modified_prompt}\n\n注意：这是分批模拟的第{batch+1}批，请模拟{BATCH_SIZE}位不同类型的消费者，确保批次间消费者类型有多样性。"
            
            # 构建适用于文心一言API的消息格式
            batch_messages = [
                {"role": "user", "content": batch_prompt + "\n\n" + user_msg.get("content", "")}
            ]
            
            # 随机延迟0-2秒，错开请求
            time.sleep(random.uniform(0, 2))
            
            # 调用API
            batch_result = self.api_connector.call_api(batch_messages, None, None, stats_callback)
            
            # 提取JSON
            batch_json = extract_json(batch_result)
            if batch_json:
                all_batches.append(batch_json)
                print(f"批次 {batch+1} 成功获取JSON数据")
            else:
                print(f"批次 {batch+1} 未能提取有效JSON")
            
            # 成功后休息一下，避免频率限制
            time.sleep(REQUEST_INTERVAL)
        
        # 合并所有批次结果
        if all_batches:
            combined_result = self._combine_simulation_batches(all_batches)
            return combined_result
        else:
            return "所有批次处理均失败，请重试或减少模拟复杂度。"
    
    def _combine_simulation_batches(self, json_batches):
        """合并多个批次的模拟结果
        
        Args:
            json_batches: 多个批次的JSON结果
            
        Returns:
            合并后的JSON字符串
        """
        print("合并分批处理结果...")
        
        try:
            # 解析所有JSON
            parsed_batches = []
            for batch_json in json_batches:
                try:
                    if isinstance(batch_json, str):
                        batch_data = json.loads(batch_json)
                    else:
                        batch_data = batch_json
                    parsed_batches.append(batch_data)
                except Exception as e:
                    print(f"解析批次JSON出错: {e}")
                    continue
            
            if not parsed_batches:
                return "无法解析任何批次的JSON数据。"
            
            # 使用第一个批次作为基础
            result = parsed_batches[0]
            
            # 合并customer_interactions
            for batch in parsed_batches[1:]:
                if "customer_interactions" in batch:
                    result["customer_interactions"].extend(batch.get("customer_interactions", []))
            
            # 去重，确保名字不重复
            unique_interactions = {}
            for interaction in result["customer_interactions"]:
                name = interaction.get("name")
                if name and name not in unique_interactions:
                    unique_interactions[name] = interaction
            
            # 更新为去重后的交互
            result["customer_interactions"] = list(unique_interactions.values())
            
            # 调整统计数据
            if "daily_stats" in result:
                customer_flow = len(result["customer_interactions"])
                new_customers = sum(1 for interaction in result["customer_interactions"] if interaction.get("visit_count", 0) == 1)
                returning_customers = customer_flow - new_customers
                
                # 计算消费转化率
                purchases = sum(1 for interaction in result["customer_interactions"] 
                               if interaction.get("behavior", {}).get("made_purchase", False))
                conversion_rate = f"{int(purchases/customer_flow*100) if customer_flow > 0 else 0}%"
                
                # 计算总销售额
                total_sales = sum(interaction.get("behavior", {}).get("amount_spent", 0) 
                                 for interaction in result["customer_interactions"])
                
                # 计算人均消费
                avg_expense = int(total_sales / purchases) if purchases > 0 else 0
                
                # 统计产品销量
                product_counts = {}
                for interaction in result["customer_interactions"]:
                    for product in interaction.get("behavior", {}).get("items_purchased", []):
                        product_counts[product] = product_counts.get(product, 0) + 1
                
                best_sellers = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
                best_seller_names = [product for product, _ in best_sellers[:3]] if best_sellers else []
                
                # 更新统计数据
                result["daily_stats"].update({
                    "customer_flow": customer_flow,
                    "new_customers": new_customers,
                    "returning_customers": returning_customers,
                    "conversion_rate": conversion_rate,
                    "total_sales": total_sales,
                    "avg_expense": avg_expense,
                    "best_sellers": best_seller_names[:3] if best_seller_names else ['金骏眉', '正山小种']
                })
            
            # 转回JSON字符串
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"合并批次时出错: {str(e)}")
            # 如果合并失败，返回第一个批次的结果
            return json_batches[0] if json_batches else "合并批次失败，无有效数据。" 