#coding=utf-8
"""
工具类模块 - 提供各种工具函数
"""

import ast
import json
import hashlib

def extract_json(content, json_block_regex=None):
    """从API响应中提取JSON数据
    
    Args:
        content: API响应内容
        json_block_regex: 用于提取JSON代码块的正则表达式
        
    Returns:
        提取出的JSON字符串，如果没有找到则返回None
    """
    if not content:
        print("内容为空，无法提取JSON")
        return None
    
    # 首先尝试提取markdown代码块中的JSON
    if json_block_regex:
        json_blocks = json_block_regex.findall(content)
        if json_blocks:
            full_json = "\n".join(json_blocks)
            if full_json.startswith("json"):
                full_json = full_json[5:]
            return full_json
    
    # 如果没找到代码块，尝试直接找大括号
    try:
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if (start_idx != -1 and end_idx != -1 and start_idx < end_idx):
            potential_json = content[start_idx:end_idx+1]
            # 简单验证是否为有效JSON
            try:
                ast.literal_eval(potential_json)
                return potential_json
            except:
                pass
    except Exception as e:
        print(f"尝试直接提取JSON时出错: {str(e)}")
    
    print("未能在回复中找到有效JSON")
    return None

def get_cache_key(messages):
    """根据消息生成缓存键
    
    Args:
        messages: 消息列表
        
    Returns:
        生成的缓存键
    """
    # 将消息序列化为JSON字符串
    messages_str = json.dumps(messages, sort_keys=True)
    # 对消息进行哈希处理，作为缓存键
    return hashlib.md5(messages_str.encode('utf-8')).hexdigest() 