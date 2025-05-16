#coding=utf-8
"""
通用工具函数模块
"""

import json
import logging

def string_to_dict(dict_string):
    """将字符串转换为字典"""
    try:
        # 使用json模块替代ast.literal_eval
        dictionary = json.loads(dict_string)
        return dictionary
    except json.JSONDecodeError as e:
        logging.error(f"转换字符串为字典时出错: {e}")
        return None

def percentage_to_number(s):
    """将百分比字符串转换为数字"""
    if isinstance(s, int):
        return s
    no_percent = s.replace('%', '')
    return int(no_percent)

def to_number(s):
    """将字符串转换为数字，保留默认值"""
    if isinstance(s, int):
        return s
    if s and isinstance(s, str):
        return int(s)
    return 1  # 默认值

def check_completed(response):
    """检查模拟是否已经完成30天"""
    try:
        if response.get("day", 0) >= 30:
            return True
        else:
            return False
    except:
        return False

def clean_emoji_field(json_data):
    """清理emoji字段，保留表情符号但删除文本描述"""
    if 'customer_interactions' not in json_data:
        return json_data
        
    for customer in json_data['customer_interactions']:
        if 'emoji' in customer:
            # 只保留表情符号，删除文字
            emoji_chars = ''.join(char for char in customer['emoji'] if not char.isalpha() and not char.isspace())
            if emoji_chars:
                customer['emoji'] = emoji_chars[:5]  # 限制最多5个表情字符
            else:
                customer['emoji'] = '👍✨'  # 默认表情
        else:
            customer['emoji'] = '👍✨'  # 默认表情

    return json_data 