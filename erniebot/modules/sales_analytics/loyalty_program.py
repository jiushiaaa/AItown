#coding=utf-8
"""
会员积分分析模块 - 负责分析会员积分系统的运营和效果
"""

class LoyaltyProgramAnalyzer:
    """会员积分分析器，负责分析会员积分系统的运营和效果"""
    
    def __init__(self, data_provider):
        """
        初始化会员积分分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def get_loyalty_program_metrics(self):
        """获取会员积分系统的各项指标"""
        total_customers = len(self.data_provider.customer_purchase_history)
        if total_customers == 0:
            return {
                'points_redemption_rate': 0,
                'average_points_per_customer': 0,
                'redemption_count': 0,
                'point_usage_ratio': 0,
                'member_tier_distribution': {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
            }
        
        # 计算会员等级分布
        member_tiers = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        for tier in self.data_provider.loyalty_tier.values():
            if tier in member_tiers:
                member_tiers[tier] += 1
        
        # 计算人均积分
        average_points = sum(self.data_provider.customer_points.values()) / total_customers
        
        # 计算积分使用率
        customers_with_redemptions = len([c for c in self.data_provider.points_usage_history if self.data_provider.points_usage_history[c]])
        redemption_rate = customers_with_redemptions / total_customers if total_customers > 0 else 0
        
        # 计算积分使用比例
        points_usage_ratio = self.data_provider.points_used_total / self.data_provider.points_earned_total if self.data_provider.points_earned_total > 0 else 0
        
        return {
            'points_redemption_rate': round(redemption_rate * 100, 1),  # 百分比
            'average_points_per_customer': int(average_points),
            'redemption_count': self.data_provider.points_redemption_count,
            'point_usage_ratio': round(points_usage_ratio * 100, 1),  # 百分比
            'member_tier_distribution': member_tiers
        }
    
    def analyze_loyalty_tier_spending(self):
        """分析不同会员等级的消费情况"""
        tier_spending = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        tier_customer_count = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        tier_purchase_count = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        
        # 统计各等级会员的消费总额和消费次数
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            tier = self.data_provider.loyalty_tier.get(customer, '普通会员')
            
            tier_customer_count[tier] += 1
            tier_purchase_count[tier] += len(purchases)
            
            for purchase in purchases:
                tier_spending[tier] += purchase.get('amount', 0)
        
        # 计算平均值
        tier_avg_spending = {}
        tier_avg_purchase_frequency = {}
        
        for tier in tier_spending.keys():
            if tier_customer_count[tier] > 0:
                tier_avg_spending[tier] = round(tier_spending[tier] / tier_customer_count[tier], 2)
                tier_avg_purchase_frequency[tier] = round(tier_purchase_count[tier] / tier_customer_count[tier], 2)
            else:
                tier_avg_spending[tier] = 0
                tier_avg_purchase_frequency[tier] = 0
        
        return {
            'tier_total_spending': tier_spending,
            'tier_customer_count': tier_customer_count,
            'tier_purchase_count': tier_purchase_count,
            'tier_avg_spending': tier_avg_spending,
            'tier_avg_purchase_frequency': tier_avg_purchase_frequency
        }
    
    def analyze_points_redemption_patterns(self):
        """分析积分兑换模式"""
        # 统计各种兑换物品的频率
        redemption_items = {}
        redemption_by_tier = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        redemption_points_by_tier = {'普通会员': 0, '银卡会员': 0, '金卡会员': 0, '钻石会员': 0}
        
        for customer, usages in self.data_provider.points_usage_history.items():
            tier = self.data_provider.loyalty_tier.get(customer, '普通会员')
            
            for usage in usages:
                items = usage.get('items_redeemed', [])
                points_used = usage.get('points_used', 0)
                
                redemption_by_tier[tier] += 1
                redemption_points_by_tier[tier] += points_used
                
                for item in items:
                    if item in redemption_items:
                        redemption_items[item] += 1
                    else:
                        redemption_items[item] = 1
        
        # 计算各等级会员的平均兑换积分
        avg_points_per_redemption = {}
        for tier, count in redemption_by_tier.items():
            if count > 0:
                avg_points_per_redemption[tier] = round(redemption_points_by_tier[tier] / count)
            else:
                avg_points_per_redemption[tier] = 0
        
        # 按兑换频率排序兑换物品
        sorted_redemption_items = sorted(redemption_items.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'popular_redemption_items': sorted_redemption_items,
            'redemption_count_by_tier': redemption_by_tier,
            'total_points_redeemed_by_tier': redemption_points_by_tier,
            'avg_points_per_redemption': avg_points_per_redemption
        }
    
    def calculate_program_roi(self):
        """计算会员积分系统的投资回报率"""
        # 假设每个积分的成本为0.1元
        points_cost_factor = 0.1
        
        # 计算积分发放成本
        total_points_cost = self.data_provider.points_earned_total * points_cost_factor
        
        # 估算会员系统带来的额外销售额 (假设)
        # 1. 假设每次使用积分的顾客在下次消费会增加20%
        additional_sales_from_redemption = 0
        
        for customer, usages in self.data_provider.points_usage_history.items():
            purchases = self.data_provider.customer_purchase_history.get(customer, [])
            
            for usage in usages:
                usage_day = usage.get('day', 0)
                
                # 查找积分使用后的购买
                post_redemption_purchases = [p for p in purchases if p.get('day', 0) > usage_day]
                
                if post_redemption_purchases:
                    # 计算积分使用前的平均消费
                    pre_redemption_purchases = [p for p in purchases if p.get('day', 0) < usage_day]
                    pre_avg = sum(p.get('amount', 0) for p in pre_redemption_purchases) / max(1, len(pre_redemption_purchases))
                    
                    # 计算积分使用后的消费总额
                    post_total = sum(p.get('amount', 0) for p in post_redemption_purchases)
                    
                    # 估计由于积分激励带来的额外销售
                    expected_without_points = pre_avg * len(post_redemption_purchases)
                    additional_sales = max(0, post_total - expected_without_points)
                    additional_sales_from_redemption += additional_sales
        
        # 计算投资回报率
        if total_points_cost > 0:
            roi = (additional_sales_from_redemption - total_points_cost) / total_points_cost * 100
        else:
            roi = 0
        
        return {
            'total_points_cost': round(total_points_cost, 2),
            'estimated_additional_sales': round(additional_sales_from_redemption, 2),
            'program_roi': round(roi, 2),
            'is_profitable': roi > 0
        } 