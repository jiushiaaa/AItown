#coding=utf-8
"""
客户互动相关函数模块
"""

import random
import math
import logging
from typing import Dict, Any, List
import json
import os
from datetime import datetime

from ..config import (
    CONSUMER_TYPES_MAPPING, VALID_LOCATIONS, 
    EMOJIS, AGE_RANGES, get_product_info, get_valid_names,
    POSITIVE_COMMENTS, NEUTRAL_COMMENTS, NEGATIVE_COMMENTS, BROWSING_COMMENTS,
    CONSUMER_REGIONS, CONSUMER_REGION_TYPES, CONSUMER_REGION_DISTRIBUTION, CONSUMER_PSYCHOLOGICAL_TRAITS
)

# 加载真实消费者名称
def load_consumer_names():
    """加载消费者类型和名称"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config')
        consumer_types_file = os.path.join(config_dir, 'consumer_types.json')
        
        if os.path.exists(consumer_types_file):
            with open(consumer_types_file, 'r', encoding='utf-8') as f:
                consumer_types = json.load(f)
                
            # 提取所有消费者名称
            all_names = []
            for type_names in consumer_types.values():
                all_names.extend(type_names)
            
            return all_names
        else:
            print(f"警告: 消费者类型文件不存在 {consumer_types_file}")
            return []
    except Exception as e:
        print(f"加载消费者名称时出错: {e}")
        return []

# 缓存消费者名称，避免重复加载
_CONSUMER_NAMES = None

def get_consumer_names():
    """获取消费者名称列表（带缓存）"""
    global _CONSUMER_NAMES
    if _CONSUMER_NAMES is None:
        _CONSUMER_NAMES = load_consumer_names()
        # 如果加载失败，使用默认名称
        if not _CONSUMER_NAMES:
            _CONSUMER_NAMES = ["张三", "李四", "王五", "赵六", "刘一", "陈二", "郑十"]
    return _CONSUMER_NAMES

def generate_default_customer_interactions(day: int) -> List[Dict[str, Any]]:
    """生成默认的客户互动数据"""
    # 优先使用consumer_types.json中加载的真实消费者名称
    real_consumer_names = get_consumer_names()
    
    if real_consumer_names:
        logging.info(f"使用consumer_types.json中的真实消费者名称生成互动数据，共有 {len(real_consumer_names)} 个名称")
        # 使用真实消费者名称
        all_names = real_consumer_names
        # 为每个名称随机分配消费者类型
        all_consumer_types = []
        for name in all_names:
            # 根据名称查找其所属类型
            found_type = None
            for consumer_type, names in CONSUMER_TYPES_MAPPING.items():
                if name in names:
                    found_type = consumer_type
                    break
            
            # 如果找不到类型，随机分配一个
            if not found_type:
                found_type = random.choice(list(CONSUMER_TYPES_MAPPING.keys()))
                
            all_consumer_types.append(found_type)
    else:
        # 扩展消费者类型和名称列表，更新为正山堂的消费者类型
        all_consumer_types = []
        all_names = []
        
        for consumer_type, names in CONSUMER_TYPES_MAPPING.items():
            for name in names:
                all_consumer_types.append(consumer_type)
                all_names.append(name)
    
    # 调整消费者类型分布，增加年轻群体占比
    consumer_type_weights = {
        "传统茶文化爱好者": 0.15,  # 从20%降低到15%
        "品质生活追求者": 0.20,  # 从25%降低到20%
        "商务人士": 0.15,  # 从20%降低到15%
        "健康生活主义者": 0.15,  # 保持15%
        "年轻新贵": 0.35   # 从20%提高到35%
    }
    
    products = get_product_info()
    
    # 产品列表（仅名称）
    product_names = list(products.keys())
    
    # 随机选择7-10个消费者
    num_customers = random.randint(7, min(10, len(all_names)))
    
    # 使用加权选择算法选择消费者类型
    selected_indices = []
    for _ in range(num_customers):
        # 创建基于权重的消费者类型选择
        chosen_type = random.choices(
            list(consumer_type_weights.keys()),
            weights=list(consumer_type_weights.values()),
            k=1
        )[0]
        
        # 从该类型中随机选择一个名字
        available_names = [i for i, t in enumerate(all_consumer_types) if t == chosen_type 
                         and i not in selected_indices]
        if available_names:
            selected_indices.append(random.choice(available_names))
        else:
            # 如果该类型名字已用完，随机选择其他类型
            available_indices = [i for i in range(len(all_names)) if i not in selected_indices]
            if available_indices:
                selected_indices.append(random.choice(available_indices))
    
    # 判断当天是否有促销活动
    is_promotion_day = random.random() < 0.25  # 25%的概率是促销日
    is_weekend = day % 7 == 0 or day % 7 == 6  # 判断是否为周末
    
    # 节假日列表 (春节、清明、五一、中秋、国庆等重要节日)
    holiday_days = [3, 8, 15, 22, 28]  # 模拟重要节日天数
    is_holiday = day in holiday_days
    
    # 促销活动类型
    promotion_types = [
        "会员积分双倍日", 
        "新品上市特惠", 
        "节日礼盒优惠", 
        "茶艺体验免费日",
        "限时折扣", 
        "买赠活动", 
        "VIP专享日"
    ]
    
    # 促销日判断 - 25%的概率是促销日，节假日必定是促销日
    is_promotion_day = is_holiday or day % 4 == 0 or random.random() < 0.15
    # 选择促销类型
    promotion_type = random.choice(promotion_types) if is_promotion_day else None
    
    # 基于日期和促销活动调整转化率
    base_purchase_probability = 0.40  # 基础购买概率从0.60降低到0.40
    if is_promotion_day:
        base_purchase_probability += 0.15  # 促销日提高购买概率
    if is_weekend:
        base_purchase_probability += 0.10  # 周末提高购买概率
    
    interactions = []
    for idx, i in enumerate(selected_indices):
        # 获取消费者类型和名称
        consumer_type = all_consumer_types[i]
        name = all_names[i]
        
        # 基于消费者类型设置相应的年龄
        min_age, max_age = AGE_RANGES.get(consumer_type, (30, 50))
        
        # 首次访问概率降低，随天数增加
        is_first_visit = random.random() > min(0.7, day / 50)
        visit_count = 1 if is_first_visit else random.randint(2, min(day, 8))
        
        # 客户进店率和购买转化率更真实化
        consumer_type_enter_probability = {
            "传统茶文化爱好者": 0.90,  # 非常高的进店率
            "品质生活追求者": 0.85,
            "商务人士": 0.80,
            "健康生活主义者": 0.75,
            "年轻新贵": 0.65  # 较低的进店率
        }
        
        consumer_type_purchase_probability = {
            "传统茶文化爱好者": base_purchase_probability + 0.10,
            "品质生活追求者": base_purchase_probability + 0.05,
            "商务人士": base_purchase_probability + 0.08,
            "健康生活主义者": base_purchase_probability,
            "年轻新贵": base_purchase_probability - 0.15  # 年轻人更喜欢逛而不买
        }
        
        entered_store = random.random() < consumer_type_enter_probability.get(consumer_type, 0.75)
        
        # 考虑客户重复访问时的购买概率增加
        visit_modifier = min(0.05 * (visit_count - 1), 0.15)  # 每次访问增加5%的购买概率，最多增加15%
        
        made_purchase = (random.random() < consumer_type_purchase_probability.get(consumer_type, 0.60) + visit_modifier) if entered_store else False
        
        # 根据消费者类型设置产品偏好
        preferred_products = []
        if consumer_type == "传统茶文化爱好者":
            # 偏好传统、高端红茶
            preferred_products = [
                "金骏眉特级", "金骏眉典藏", "金骏眉珍藏", "正山小种特级", "正山小种野茶", 
                "源起1568特级", "百年原生老枞", "宋风雅韵礼盒", "经典马口罐礼盒",
                "正山韵·传世金红", "正山小种·古法", "金骏眉·大师款"
            ]
        elif consumer_type == "商务人士":
            # 偏好礼盒和高端产品，用于送礼
            preferred_products = [
                "金骏眉珍藏", "宋风雅韵礼盒", "秘境寻踪礼盒", "全家福组合礼盒", 
                "经典马口罐礼盒", "茗品尊享礼盒", "红茶品鉴小样礼盒", "企业定制茶礼",
                "定制礼盒", "百年老枞·臻藏", "奇韵藏珍限定", "节日限定礼盒"
            ]
        elif consumer_type == "健康生活主义者":
            # 偏好有机和地域特色茶
            preferred_products = [
                "普安红", "巴东红", "信阳红", "白沙红", "古丈红", "会稽红",
                "正山小种野茶", "白毫银针", "察隅红", "广元红", "黔楚野枞礼盒",
                "轻尝·红茶", "初味红茶"
            ]
        elif consumer_type == "年轻新贵":
            # 偏好新潮、特色和入门级产品
            preferred_products = [
                "妃子笑", "银骏眉", "骏眉红茶", "广元红", "察隅红", 
                "铁观音", "秘境寻踪礼盒", "茶缘·晨曦", "茶缘·春韵", "茶语·小红",
                "新客体验装", "会员特惠礼盒"
            ]
        else:  # 品质生活追求者
            # 偏好高品质、多样化产品及个人定制
            preferred_products = [
                "金骏眉特级", "妃子笑", "银骏眉", "正山小种特级", 
                "广元红", "大红袍", "铁观音", "定制款金骏眉",
                "茗品尊享礼盒", "白毫银针", "武夷秘传·1986", "金芽·珍藏版"
            ]
        
        # 生成购买行为
        items_purchased = []
        amount_spent = 0
        
        # 促销活动时的购买量增加
        max_items = 2
        if is_promotion_day:
            if consumer_type == "商务人士":
                max_items = 3
            else:
                max_items = random.randint(1, 3)
        else:
            if consumer_type == "商务人士":
                max_items = random.randint(1, 3)
            else:
                max_items = random.randint(1, 2)
        
        # 变量初始化
        has_custom_service = False
        custom_service_modifier = 1.0
        
        if made_purchase:
            # 从偏好产品中随机选择
            available_preferred = [p for p in preferred_products if p in product_names]
            if not available_preferred:
                available_preferred = product_names
                
            num_items = random.randint(1, max_items)
            
            # 如果有有机产品偏好，优先考虑有机产品
            has_organic_preference = False
            if consumer_type == "健康生活主义者":
                has_organic_preference = True
            
            # 选择剩余产品
            remaining_items = num_items - len(items_purchased)
            if remaining_items > 0:
                remaining_products = [p for p in available_preferred if p not in items_purchased]
                items_purchased.extend(random.sample(remaining_products, min(remaining_items, len(remaining_products))))
            
            # 计算消费金额，促销日有折扣
            for item in items_purchased:
                min_price, max_price = products[item]["price_range"]
                # 如果是礼盒或高端产品，价格往上取
                if "礼盒" in item or "高端" in item:
                    price = random.randint(int(min_price * 0.8), max_price)
                else:
                    price = random.randint(min_price, max_price)
                
                # 促销日折扣
                if is_promotion_day:
                    price = int(price * random.uniform(0.8, 0.95))
                
                # 应用定制服务溢价
                if has_custom_service and custom_service_modifier > 1.0:
                    price = int(price * custom_service_modifier)
                    
                amount_spent += price
        
        # 更真实的客户满意度分布
        if made_purchase:
            # 使用更真实的分布: 5% 给1分, 10% 给2分, 20% 给3分, 35% 给4分, 30% 给5分
            satisfaction_choices = [1, 2, 3, 4, 5]
            satisfaction_weights = [0.05, 0.10, 0.20, 0.35, 0.30]
            satisfaction = random.choices(satisfaction_choices, satisfaction_weights)[0]
        else:
            satisfaction = None
            
        # 基于满意度和消费者类型决定回访意愿
        if entered_store:
            if made_purchase:
                will_return_prob = {
                    2: 0.2,  # 2分满意度只有20%会回访
                    3: 0.5,  # 3分满意度有50%会回访
                    4: 0.8,  # 4分满意度有80%会回访
                    5: 0.95  # 5分满意度有95%会回访
                }.get(satisfaction, 0.75)
            else:
                # 未购买顾客的回访意愿较低
                will_return_prob = 0.35
                
            # 不同消费者类型有不同的忠诚度
            type_loyalty_mod = {
                "传统茶文化爱好者": 0.15,  # 更忠诚
                "品质生活追求者": 0.05,
                "商务人士": 0.10,
                "健康生活主义者": 0,
                "年轻新贵": -0.15  # 不太忠诚
            }.get(consumer_type, 0)
            
            will_return = random.random() < (will_return_prob + type_loyalty_mod)
        else:
            will_return = False
            
        # 决定是否会推荐
        if satisfaction and satisfaction >= 4:
            will_recommend = random.random() < 0.7  # 较高满意度有70%会推荐
        elif satisfaction and satisfaction == 3:
            will_recommend = random.random() < 0.3  # 中等满意度有30%会推荐
        else:
            will_recommend = random.random() < 0.1  # 低满意度或未购买有10%会推荐
        
        # 确保消费者分布在不同位置
        location_idx = idx % len(VALID_LOCATIONS)
        location = VALID_LOCATIONS[location_idx]
        
        # 不同的评论类型
        if made_purchase:
            if satisfaction >= 4:
                base_comments = POSITIVE_COMMENTS
            elif satisfaction == 3:
                base_comments = NEUTRAL_COMMENTS
            else:
                base_comments = NEGATIVE_COMMENTS
        else:
            base_comments = BROWSING_COMMENTS
            
        # 默认评论
        comments = ""
        if made_purchase and items_purchased:
            item = items_purchased[0]
            template = random.choice(base_comments)
            comments = template.format(product=item)
        else:
            comments = random.choice(BROWSING_COMMENTS) if entered_store else "路过，未进店"
        
        # 根据满意度选择表情
        # 定义表情符号组
        positive_emojis = ['👍', '👏', '😊', '😄', '❤️', '👌', '💯', '🏆', '😍', '🙌', '✨', '😎', '🤩', '😉']
        neutral_emojis = ['🍵', '🫖', '🌿', '🍃', '🛍️', '🌟', '📚', '😌']
        negative_emojis = ['🤔', '🧐', '😐', '🤨', '🙄']
        
        if satisfaction is None:
            emoji = ''.join(random.sample(neutral_emojis, random.randint(1, 2)))
        elif satisfaction >= 4:
            emoji = ''.join(random.sample(positive_emojis, random.randint(1, 2)))
        elif satisfaction == 3:
            emoji = ''.join(random.sample(neutral_emojis, random.randint(1, 2)))
        else:
            emoji = ''.join(random.sample(negative_emojis, random.randint(1, 2)))
        
        # 顾客进店后，考虑不同场景的购买行为差异
        location = random.choice(VALID_LOCATIONS)
        
        # 不同场景的停留时间有差异
        browsed_minutes = random.randint(10, 35)
        
        # 有机产品和定制服务区的特殊处理
        has_organic_preference = False
        has_custom_service = False
        organic_product_bonus = 0
        custom_service_modifier = 1.0
        
        # 有机认证区和健康生活主义者更关注有机产品
        if location == "有机认证区" or consumer_type == "健康生活主义者":
            has_organic_preference = True
            organic_product_bonus = 0.15  # 提高有机产品购买概率
            # 增加停留时间
            browsed_minutes += random.randint(5, 15)
            
        # 个人定制区特殊处理
        if location == "个人定制区":
            has_custom_service = True
            # 增加停留时间
            browsed_minutes += random.randint(10, 20)
            # 不同消费者类型对定制服务的接受度不同
            if consumer_type in ["传统茶文化爱好者", "商务人士", "品质生活追求者"]:
                # 这些类型的消费者更容易接受定制服务
                custom_service_modifier = 1.3  # 定制溢价30%
                if made_purchase and random.random() < 0.6:  # 60%的概率接受定制服务
                    custom_service_type = random.choice(["个人定制包装", "私人口味调配", "定制礼盒", "专属联名款"])
                    # 添加定制评论
                    # Update the comments variable directly
                    comments = f"选择了{custom_service_type}服务，很满意定制效果，值得额外的费用。"
        
        # 茶艺体验区和文化传承区特殊处理
        if location in ["茶艺体验区", "文化传承区"]:
            # 这些区域停留时间普遍较长
            browsed_minutes += random.randint(15, 30)
            
            # 长时间停留提高购买概率
            if browsed_minutes > 30 and not made_purchase:
                # 重新计算是否购买
                extra_purchase_chance = min(0.5, browsed_minutes / 100)  # 最多提高50%的购买概率
                if random.random() < extra_purchase_chance:
                    made_purchase = True
                    # 生成购买产品
                    if preferred_products:
                        items_purchased = [random.choice(preferred_products)]
                        # 计算金额
                        item = items_purchased[0]
                        if item in product_names:
                            min_price, max_price = products[item]["price_range"]
                            amount_spent = random.randint(min_price, max_price)
            
            # 添加特殊评论
            if location == "茶艺体验区" and made_purchase and items_purchased:
                culture_comments = [
                    f"茶艺师的表演让我对{items_purchased[0]}有了全新的认识，忍不住买了一份带回家",
                    "亲眼见证茶艺师的冲泡技巧，品到了平时喝不到的茶香，决定买一份",
                    "茶艺表演很有意境，在这种氛围下品茶更有味道，很值得"
                ]
                comments = random.choice(culture_comments)
            elif location == "文化传承区" and made_purchase and items_purchased:
                culture_comments = [
                    f"了解了正山堂的历史和{items_purchased[0]}的由来，对这个品牌更信任了",
                    "茶文化底蕴深厚，听了讲解后对传统工艺更加敬佩，买一份支持传统文化",
                    "这里的文化展示让人感受到匠心传承，打动我买了几款经典茶"
                ]
                comments = random.choice(culture_comments)
        
        # 节假日和促销活动特殊评论        
        if (is_holiday or is_promotion_day) and made_purchase and items_purchased:
            promo_comments = [
                f"趁着促销活动买了几款想试的茶，价格很优惠",
                "今天的活动很划算，买到就是赚到",
                "节日促销力度大，买了比平时更多的茶",
                "促销日的体验很好，店员服务更加热情，也买得更多",
                "积分翻倍活动太吸引人了，专门来囤货攒积分",
                "限时折扣很给力，比平时便宜不少"
            ]
            # 50%的概率使用促销评论
            if random.random() < 0.5:
                comments = random.choice(promo_comments)
        
        interaction = {
            'name': name,
            'type': consumer_type,
            'age': random.randint(min_age, max_age),
            'location': location,
            'visit_count': visit_count,
            'behavior': {
                'entered_store': entered_store,
                'browsed_minutes': browsed_minutes,
                'made_purchase': made_purchase,
                'items_purchased': items_purchased,
                'amount_spent': amount_spent if made_purchase else 0,
                'satisfaction': satisfaction,
                'will_return': will_return,
                'will_recommend': will_recommend
            },
            'comments': comments,
            'emoji': emoji
        }
        
        # 为消费者添加地域信息和消费心理特征
        interaction = add_consumer_details(interaction)
        
        interactions.append(interaction)
    
    return interactions

def add_consumer_details(interaction: Dict[str, Any]) -> Dict[str, Any]:
    """添加消费者的地域信息和消费心理特征"""
    consumer_type = interaction.get('type')
    if not consumer_type or consumer_type not in CONSUMER_PSYCHOLOGICAL_TRAITS:
        return interaction
            
    # 添加消费心理特征
    psychological_traits = CONSUMER_PSYCHOLOGICAL_TRAITS.get(consumer_type, {})
    interaction['consumer_traits'] = {
        "价格敏感度": psychological_traits.get("价格敏感度", "中"),
        "品牌忠诚度": psychological_traits.get("品牌忠诚度", "中")
    }
    
    # 添加地域信息 - 根据消费者类型的地域分布概率选择
    region_dist = CONSUMER_REGION_DISTRIBUTION.get(consumer_type, {})
    if region_dist:
        # 根据概率选择地域类型
        region_types = list(region_dist.keys())
        region_probs = list(region_dist.values())
        selected_region_type = random.choices(region_types, weights=region_probs, k=1)[0]
        
        # 根据地域类型选择具体城市
        if selected_region_type in ["一线城市", "新一线城市", "二线城市"]:
            cities = CONSUMER_REGION_TYPES.get(selected_region_type, [])
            if cities:
                city = random.choice(cities)
                region = next((r for r, provinces in CONSUMER_REGIONS.items() 
                            for province in provinces if city in province or province == city), "其他")
            else:
                region = random.choice(list(CONSUMER_REGIONS.keys()))
                city = "未指定城市"
        else:
            region = random.choice(list(CONSUMER_REGIONS.keys()))
            city = "未指定城市"
            
        interaction['region'] = {
            "地区": region,
            "城市类型": selected_region_type,
            "城市": city
        }
    
    return interaction 