#coding=utf-8
"""
产品管理模块 - 处理产品生成、识别和品牌信息
"""

import re
import os
import random
from datetime import datetime
from .config import get_file_path

def is_product_generation_request(question):
    """识别是否为产品设计/生成/开发请求"""
    if not question or not isinstance(question, str):
        return False
    
    # 定义产品生成相关的关键词组合
    product_keywords = ["产品", "茶饮", "饮品", "饮料", "品牌", "店铺"]
    action_keywords = ["生成", "设计", "开发", "创建", "制作", "构思", "研发", "创新", "打造", "推出"]
    
    # 检查关键词组合
    question_lower = question.lower()
    
    # 检查明确的指令，如"生成产品"
    if "生成产品" in question_lower:
        return True
    
    # 检查"为X群体"开头的产品生成请求
    if question_lower.startswith(("为", "给", "帮")) and any(keyword in question_lower for keyword in product_keywords):
        return True
    
    # 检查动词+产品的组合
    for action in action_keywords:
        for product in product_keywords:
            if action + product in question_lower:
                return True
            # 处理可能的词序变化，如"产品设计"而非"设计产品"
            if product + action in question_lower:
                return True
    
    # 处理更复杂的表达
    if ("帮我" in question_lower or "请" in question_lower) and \
       any(action in question_lower for action in action_keywords) and \
       any(product in question_lower for product in product_keywords):
        return True
    
    return False

def extract_consumer_type(message):
    """从用户消息中提取目标消费群体类型"""
    if not message or not isinstance(message, str):
        return None
        
    # 定义可能的消费群体关键词及其标准化映射
    consumer_types = {
        "年轻": "年轻消费者",
        "白领": "年轻白领",
        "学生": "学生族",
        "传统": "传统茶文化爱好者",
        "茶文化": "传统茶文化爱好者",
        "精致": "精致生活族",
        "健康": "健康生活追求者",
        "中老年": "中老年消费者",
        "老年": "中老年消费者",
        "长辈": "中老年消费者",
        "儿童": "儿童消费者",
        "孩子": "儿童消费者",
        "男性": "男性消费者",
        "女性": "女性消费者"
    }
    
    message = message.lower()
    for keyword, consumer_type in consumer_types.items():
        if keyword in message:
            return consumer_type
            
    return None

def extract_brand_summary(suggestion_text):
    """提取茶饮品牌的简洁总结"""
    lines = suggestion_text.split('\n')
    brand_name = "未找到品牌名称"
    
    # 查找品牌名称
    for line in lines:
        name_patterns = [
            r"品牌名称[：:]\s*[「\"\']?(.+?)[」\"\']?[\n\r]",
            r"[「\"\'](.+?)[」\"\']", 
            r"品牌名称[：:]\s*(.+?)[\n\r]"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, line)
            if match:
                brand_name = match.group(1).strip()
                brand_name = brand_name.replace('*', '').strip()
                print(f"提取到品牌名称: {brand_name}")
                break
        
        if brand_name != "未找到品牌名称":
            break
    
    # 如果仍未找到品牌名称，尝试直接搜索
    if brand_name == "未找到品牌名称":
        full_text = '\n'.join(lines)
        name_match = re.search(r'[「\"\'](.+?)[」\"\']', full_text)
        if name_match:
            brand_name = name_match.group(1).strip()
            print(f"从引号内容提取品牌名称: {brand_name}")
    
    # 新增: 如果仍未找到品牌名称，尝试从文本中识别频繁出现的潜在品牌名
    if brand_name == "未找到品牌名称":
        full_text = ' '.join(lines)
        
        # 寻找常见品牌标识模式
        brand_indicators = [
            r"(\w+)(?:公司|品牌|集团|茶叶|茶业|茶行|店)",
            r"(\w+堂)(?:产品|标志|品牌|系列|传统)",
            r"(?:传承|创立)(?:了)?(\w+)(?:的|品牌|传统|文化)",
            r"(\w+(?:堂|斋|轩|阁|茗|坊|家|号|庄|铺|轩|阁))(?:\d+年|\w*历史)"
        ]
        
        potential_brands = []
        for pattern in brand_indicators:
            matches = re.findall(pattern, full_text)
            if matches:
                potential_brands.extend(matches)
        
        # 统计品牌名称出现频率
        if potential_brands:
            from collections import Counter
            brand_counts = Counter(potential_brands)
            most_common_brand = brand_counts.most_common(1)[0][0]
            
            brand_name = most_common_brand
            print(f"从文本分析提取品牌名称: {brand_name}")
    
    # 特别分析产品定位和文化内涵部分，这两部分通常会包含品牌信息
    if brand_name == "未找到品牌名称":
        positioning_section = ""
        culture_section = ""
        
        in_positioning = False
        in_culture = False
        
        for line in lines:
            if "产品定位" in line:
                in_positioning = True
                in_culture = False
                continue
            elif "文化内涵" in line:
                in_culture = True
                in_positioning = False
                continue
            elif any(section in line for section in ["茶叶选材", "工艺特点", "口感描述", "包装设计", "价格定位", "目标消费群体", "场景应用", "总结"]):
                in_positioning = False
                in_culture = False
                continue
                
            if in_positioning:
                positioning_section += line + " "
            elif in_culture:
                culture_section += line + " "
        
        # 分析产品定位部分
        if positioning_section:
            position_brands = re.findall(r'(\w+(?:堂|斋|轩|阁|茗|坊|家|号|庄|铺|轩|阁))(?:产品|品牌|系列)', positioning_section)
            if position_brands:
                brand_name = position_brands[0]
                print(f"从产品定位部分提取品牌名称: {brand_name}")
        
        # 分析文化内涵部分
        if brand_name == "未找到品牌名称" and culture_section:
            culture_brands = re.findall(r'(\w+(?:堂|斋|轩|阁|茗|坊|家|号|庄|铺|轩|阁))[^，。,\.]*(?:文化|传统|精神|理念|历史|品牌)', culture_section)
            if culture_brands:
                brand_name = culture_brands[0]
                print(f"从文化内涵部分提取品牌名称: {brand_name}")
    
    # 如果仍未找到品牌名称，查找产品名中可能的品牌名部分
    if brand_name == "未找到品牌名称":
        product_name = ""
        for line in lines:
            if "产品名称" in line or "**" in line:
                product_match = re.search(r'\*\*(.+?)\*\*', line)
                if product_match:
                    product_name = product_match.group(1)
                    break
        
        if product_name:
            # 从产品名称中提取可能的品牌名
            parts = re.split(r'[·•\-–—]', product_name)
            if len(parts) > 1 and len(parts[0]) >= 2:
                brand_name = parts[0].strip()
                print(f"从产品名称提取品牌名称: {brand_name}")
    
    # 最后尝试查找常见的品牌特征
    if brand_name == "未找到品牌名称":
        # 搜索文本中所有可能的品牌名（2-4个字的名称+特征后缀）
        all_text = ' '.join(lines)
        possible_brands = re.findall(r'([\u4e00-\u9fa5]{2,4}(?:堂|斋|轩|阁|茗|坊|家|号|庄|铺|轩|阁))', all_text)
        if possible_brands:
            from collections import Counter
            brand_counts = Counter(possible_brands)
            if brand_counts:
                brand_name = brand_counts.most_common(1)[0][0]
                print(f"从品牌特征提取品牌名称: {brand_name}")
    
    # 针对特定品牌的直接检测
    if brand_name == "未找到品牌名称":
        known_brands = ["正山堂", "茶颜悦色", "奈雪的茶", "喜茶", "一点点", "沪上阿姨", "蜜雪冰城", "茶百道"]
        all_text = ' '.join(lines)
        for known_brand in known_brands:
            if known_brand in all_text:
                brand_name = known_brand
                print(f"直接识别到已知品牌: {brand_name}")
                break
    
    # 查找总结部分
    summary_indicators = ["总结", "简述", "总览", "概述", "可直接用于", "可用于"]
    summary_section = ""
    
    # 检查是否有明确的总结部分
    for i, line in enumerate(lines):
        for indicator in summary_indicators:
            if indicator in line:
                summary_lines = []
                for j in range(i, min(i+4, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith(("--", "=")):
                        summary_lines.append(lines[j].strip())
                summary_section = " ".join(summary_lines)
                break
        if summary_section:
            break
    
    # 如果没找到明确的总结，尝试找最后几行非空内容
    if not summary_section:
        non_empty_lines = [line.strip() for line in lines if line.strip() 
                          and not line.strip().startswith(("--", "="))
                          and not any(indicator in line for indicator in ["请复制", "输入到", "任务框"])]
        if non_empty_lines:
            summary_section = " ".join(non_empty_lines[-3:])
    
    # 如果仍然没有总结，则创建一个基于品牌名称的简单描述
    if not summary_section or len(summary_section) < 10:
        brand_features = []
        for line in lines:
            feature_keywords = ["特色", "主打", "风格", "氛围", "理念"]
            if any(keyword in line for keyword in feature_keywords):
                if ":" in line or "：" in line:
                    feature = line.split(":", 1)[-1] if ":" in line else line.split("：", 1)[-1]
                    brand_features.append(feature.strip())
        
        feature_text = ""
        if brand_features:
            feature_text = "，".join(brand_features[:2])
        
        summary_section = f"{brand_name}是一家创新茶饮品牌，{feature_text}，欢迎体验。"
    
    # 清理总结文本
    summary_section = summary_section.replace("###", "").replace("总结：", "").replace("总结:", "")
    summary_section = summary_section.strip()
    
    return brand_name, summary_section

def save_brand_info_to_file(brand_info, brand_name):
    """将品牌信息保存到单独的文件中"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 确保品牌名称不为空
        if brand_name == "未找到品牌名称" or not brand_name.strip():
            # 尝试再次提取品牌名称
            brand_name, _ = extract_brand_summary(brand_info)
        
        sanitized_brand_name = ''.join(c for c in brand_name if c.isalnum() or c in [' ', '_', '-']).strip()
        if not sanitized_brand_name:
            sanitized_brand_name = "未命名品牌"
            
        filename = f"茶饮品牌_{sanitized_brand_name}_{timestamp}.txt"
        filepath = get_file_path(filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {sanitized_brand_name} - 品牌信息\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(brand_info)
            
        print(f"品牌信息已保存到: {filepath}")
        return True, filepath
    except Exception as e:
        print(f"保存品牌信息文件时出错: {str(e)}")
        return False, None

def save_simulation_data_to_file(simulation_data, brand_name):
    """将模拟数据保存到JSON文件中"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_brand_name = ''.join(c for c in brand_name if c.isalnum() or c in [' ', '_', '-']).strip()
        if not sanitized_brand_name:
            sanitized_brand_name = "未命名品牌"
            
        filename = f"模拟数据_{sanitized_brand_name}_{timestamp}.json"
        filepath = get_file_path(filename)
        
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(simulation_data, f, ensure_ascii=False, indent=2)
            
        print(f"模拟数据已保存到: {filepath}")
        return True, filepath
    except Exception as e:
        print(f"保存模拟数据文件时出错: {str(e)}")
        return False, None 