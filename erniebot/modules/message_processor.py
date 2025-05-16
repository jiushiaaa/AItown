#coding=utf-8
"""
消息处理模块 - 处理消息格式和历史记录
"""

import re

class MessageProcessor:
    """消息处理类，处理消息格式和历史"""
    
    def __init__(self):
        """初始化消息处理器"""
        self.day_pattern = re.compile(r"第(\d+)天")
    
    def process_messages_for_erniebot(self, messages):
        """处理消息格式以适应文心一言API的要求
        
        文心一言API不支持system角色，需要将system消息合并到user消息中
        
        Args:
            messages: 原始消息列表
            
        Returns:
            处理后的消息列表
        """
        if not messages:
            return []
            
        # 复制消息以避免修改原始消息
        processed = []
        system_content = ""
        
        # 找出所有system消息并合并其内容
        for msg in messages:
            if msg.get("role") == "system":
                system_content += msg.get("content", "") + "\n\n"
            else:
                processed.append(msg.copy())
        
        # 如果有system消息，将其内容添加到第一个user消息前面
        if system_content and processed:
            for i, msg in enumerate(processed):
                if msg.get("role") == "user":
                    processed[i]["content"] = system_content + msg.get("content", "")
                    break
            # 如果没有user消息，创建一个
            if not any(msg.get("role") == "user" for msg in processed):
                processed.insert(0, {"role": "user", "content": system_content.strip()})
        
        # 确保第一个消息是用户消息（文心一言要求）
        if processed and processed[0].get("role") != "user":
            # 如果第一个消息不是user，插入一个空的user消息
            processed.insert(0, {"role": "user", "content": "请生成下一天的消费者行为数据"})
        
        # 确保消息列表中没有system角色
        processed = [msg for msg in processed if msg.get("role") != "system"]
        
        # 输出处理后的消息格式供调试
        print(f"处理后的消息格式: {len(processed)}条消息，角色顺序: {[msg.get('role') for msg in processed]}")
        
        return processed
    
    def trim_message_history(self, messages, aggressive=False):
        """裁剪消息历史以减少令牌数
        
        Args:
            messages: 消息历史列表
            aggressive: 是否使用激进的裁剪策略
            
        Returns:
            无直接返回值，直接修改messages列表
        """
        if len(messages) <= 4:  # 保留最少的几条消息
            return
            
        print(f"裁剪前消息数量: {len(messages)}")
        
        # 始终保留第一条系统消息
        keep_first = None
        if messages[0]["role"] == "user" and "消费者行为模拟系统" in messages[0]["content"]:
            keep_first = messages[0]
            
        # 始终保留最近几轮对话
        recent_count = 6 if not aggressive else 4
        recent_messages = messages[-recent_count:] if len(messages) > recent_count else messages
        
        # 根据策略选择保留的消息
        if aggressive:
            # 激进策略：只保留第一条系统消息和最近几轮对话
            new_messages = []
            if keep_first:
                new_messages.append(keep_first)
            
            # 可能需要添加一个产品信息的消息（如果存在）
            for msg in messages[:10]:  # 只在前面几条消息中寻找
                if msg["role"] == "user" and ("产品信息" in msg["content"] or "金骏眉" in msg["content"]):
                    if msg not in new_messages:
                        new_messages.append(msg)
                    break
                    
            # 保留最近的交互
            for msg in recent_messages:
                if msg not in new_messages:
                    new_messages.append(msg)
        else:
            # 保守策略：保留第一条系统消息、产品信息和模拟天数信息，去除中间的部分历史
            new_messages = []
            if keep_first:
                new_messages.append(keep_first)
                
            # 尝试保留产品信息
            product_msg = None
            for msg in messages[:15]:
                if msg["role"] == "user" and ("产品信息" in msg["content"] or "金骏眉" in msg["content"]):
                    product_msg = msg
                    break
                    
            if product_msg and product_msg not in new_messages:
                new_messages.append(product_msg)
                
            # 保留每隔几天的模拟结果（只保留部分天数的数据）
            days_to_keep = set()
            
            # 查找所有天数
            for i, msg in enumerate(messages):
                if msg["role"] == "user" and "继续" in msg["content"]:
                    # 找下一条消息中的天数
                    if i+1 < len(messages) and messages[i+1]["role"] == "assistant":
                        day_match = self.day_pattern.search(messages[i+1]["content"])
                        if day_match:
                            day = int(day_match.group(1))
                            if day % 5 == 0 or day == 1:  # 保留第1天和每5天的数据
                                days_to_keep.add(day)
            
            # 根据要保留的天数选择消息
            current_day = None
            keep_next = False
            
            for i, msg in enumerate(messages):
                # 如果是用户请求继续，检查是否是要保留的天数
                if msg["role"] == "user" and "继续" in msg["content"] and i+1 < len(messages):
                    day_match = self.day_pattern.search(messages[i+1]["content"])
                    if day_match:
                        current_day = int(day_match.group(1))
                        keep_next = current_day in days_to_keep
                
                # 如果当前消息需要保留
                if keep_next and msg not in new_messages:
                    new_messages.append(msg)
                    
                # 一组对话后重置标志
                if keep_next and msg["role"] == "assistant":
                    keep_next = False
            
            # 保留最近几轮对话
            for msg in recent_messages:
                if msg not in new_messages:
                    new_messages.append(msg)
        
        # 更新消息列表
        messages.clear()
        messages.extend(new_messages)
        print(f"裁剪后消息数量: {len(messages)}")
    
    def generate_prompt(self, history, consumer_data=None, system_prompt=None):
        """生成提示词
        
        Args:
            history: 历史消息列表
            consumer_data: 消费者数据，如果有的话
            system_prompt: 系统提示词
            
        Returns:
            生成的提示词消息列表
        """
        # 生成系统提示词
        if not system_prompt:
            system_prompt = "请模拟红茶消费者行为。"
        
        # 如果提供了消费者数据，将其添加到系统提示词中
        if consumer_data:
            # 添加地域分布信息
            region_text = """当模拟消费者行为时，请确保按以下地域分布生成消费者：
            - 一线城市（北京、上海、广州、深圳）：约占25%的消费者
            - 新一线城市（成都、杭州、武汉、西安等）：约占35%的消费者
            - 二线城市（沈阳、厦门、福州、济南等）：约占30%的消费者
            - 三四线城市及以下：约占10%的消费者"""
            
            # 添加消费心理特征信息
            traits_text = """请在生成的JSON数据中添加consumer_traits字段，包含以下消费心理特征：
            - 价格敏感度：表示消费者对价格变化的敏感程度（高/中高/中/中低/低）
            - 品牌忠诚度：表示消费者对品牌的忠诚程度（高/中高/中/中低/低）
            
            不同类型消费者的特征不同：
            - 传统茶文化爱好者：价格敏感度低，品牌忠诚度高，注重品质
            - 品质生活追求者：价格敏感度中，品牌忠诚度中高，注重口感与体验
            - 商务人士：价格敏感度低，品牌忠诚度中，注重品牌形象
            - 健康生活主义者：价格敏感度中，品牌忠诚度中，注重健康功效
            - 年轻新贵：价格敏感度中高，品牌忠诚度低，注重社交价值"""
            
            # 添加区域信息字段提示
            region_field_text = """在JSON的customer_interactions中，为每个消费者添加region字段，格式如下：
            'region': {
                '地区': '华东/华南/华北/华中/西南/西北/东北',
                '城市类型': '一线城市/新一线城市/二线城市/三四线城市/县城/农村',
                '城市': '具体城市名称'
            }"""
            
            # 将新的提示内容添加到系统提示词中
            system_prompt += "\n\n" + region_text + "\n\n" + traits_text + "\n\n" + region_field_text
        
        # 构建提示词
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息
        for msg in history:
            messages.append(msg)
        
        return messages 