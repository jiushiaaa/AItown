#coding=utf-8
"""
消费者分析模块 - 负责分析不同消费者类型的行为和偏好
"""

from collections import defaultdict

class ConsumerAnalyzer:
    """消费者分析器，负责分析消费者行为和产品匹配度"""
    
    def __init__(self, data_provider):
        """
        初始化消费者分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def get_consumer_insights(self, product_name):
        """获取特定产品的消费者洞察"""
        consumer_insights = {}
        
        # 统计购买该产品的消费者类型分布
        consumer_type_count = defaultdict(int)
        consumer_type_satisfaction = defaultdict(list)
        
        # 遍历所有顾客的购买记录
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            # 获取消费者类型
            consumer_type = self._get_customer_type(customer)
            if not consumer_type:
                continue
                
            # 检查是否购买过该产品
            has_purchased = False
            for purchase in purchases:
                if product_name in purchase.get('items', []):
                    has_purchased = True
                    consumer_type_count[consumer_type] += 1
                    
                    # 尝试找到对应的满意度评分
                    purchase_day = purchase.get('day', 0)
                    if purchase_day in self.data_provider.customer_interactions:
                        for interaction in self.data_provider.customer_interactions[purchase_day]:
                            if interaction.get('name') == customer and product_name in interaction.get('behavior', {}).get('items_purchased', []):
                                satisfaction = interaction.get('behavior', {}).get('satisfaction')
                                if satisfaction:
                                    consumer_type_satisfaction[consumer_type].append(satisfaction)
                    
                    break
        
        # 计算总购买量
        total_purchases = sum(consumer_type_count.values())
        
        # 计算每种消费者类型的占比和平均满意度
        for consumer_type, count in consumer_type_count.items():
            percentage = (count / total_purchases * 100) if total_purchases > 0 else 0
            satisfaction_scores = consumer_type_satisfaction[consumer_type]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            
            consumer_insights[consumer_type] = {
                'purchase_count': count,
                'percentage': round(percentage, 1),
                'avg_satisfaction': round(avg_satisfaction, 1)
            }
        
        # 找出最适合的消费者类型
        if consumer_insights:
            # 根据购买量和满意度的综合评分找出最适合的消费者类型
            best_consumer_type = max(
                consumer_insights.items(),
                key=lambda x: x[1]['purchase_count'] * (x[1]['avg_satisfaction'] / 5)
            )[0]
        else:
            best_consumer_type = None
        
        return {
            'consumer_distribution': consumer_insights,
            'best_consumer_type': best_consumer_type,
            'total_purchases': total_purchases
        }
    
    def analyze_consumer_product_match(self):
        """分析不同消费者类型与产品的匹配度"""
        # 统计每种消费者类型购买的产品数量
        consumer_preferences = defaultdict(lambda: defaultdict(int))
        consumer_satisfaction = defaultdict(lambda: defaultdict(list))
        
        # 遍历所有顾客的购买记录
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            # 获取消费者类型
            consumer_type = self._get_customer_type(customer)
            if not consumer_type:
                continue
                
            # 统计购买数量和满意度
            for purchase in purchases:
                purchase_day = purchase.get('day', 0)
                for item in purchase.get('items', []):
                    consumer_preferences[consumer_type][item] += 1
                    
                    # 尝试找到该购买对应的满意度评分
                    if purchase_day in self.data_provider.customer_interactions:
                        for interaction in self.data_provider.customer_interactions[purchase_day]:
                            if interaction.get('name') == customer and item in interaction.get('behavior', {}).get('items_purchased', []):
                                satisfaction = interaction.get('behavior', {}).get('satisfaction')
                                if satisfaction:
                                    consumer_satisfaction[consumer_type][item].append(satisfaction)
        
        # 计算每种消费者类型的最受欢迎产品
        consumer_product_match = {}
        for consumer_type, products in consumer_preferences.items():
            top_products = sorted(products.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # 计算每个产品的平均满意度
            product_details = []
            for product, count in top_products:
                satisfaction_scores = consumer_satisfaction[consumer_type][product]
                avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
                
                product_details.append({
                    'product': product,
                    'purchase_count': count,
                    'avg_satisfaction': round(avg_satisfaction, 1)
                })
            
            consumer_product_match[consumer_type] = product_details
        
        return consumer_product_match
    
    def _get_customer_type(self, customer_name):
        """获取顾客的消费者类型"""
        for consumer_type, names in self.data_provider.CONSUMER_TYPES_MAPPING.items():
            if customer_name in names:
                return consumer_type
        return None 