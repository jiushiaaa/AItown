#coding=utf-8
"""
价格分析模块 - 负责分析产品价格敏感度和最优定价
"""

from collections import defaultdict

class PriceAnalyzer:
    """价格分析器，负责分析产品价格敏感度和最优定价点"""
    
    def __init__(self, data_provider):
        """
        初始化价格分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def analyze_price_sensitivity(self, product_name):
        """分析产品价格变化对销量的影响"""
        price_ranges = []
        sales_at_price = defaultdict(int)
        revenue_at_price = defaultdict(float)
        
        # 统计不同价格区间的销量
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            for purchase in purchases:
                if product_name in purchase.get('items', []):
                    # 计算单品均价
                    item_count = purchase.get('items', []).count(product_name)
                    total_amount = purchase.get('amount', 0)
                    
                    if item_count > 0 and total_amount > 0:
                        # 假设所有产品价格相同，这是简化处理
                        estimated_price = total_amount / len(purchase.get('items', []))
                        price_range = int(estimated_price / 50) * 50  # 按50元分段
                        price_ranges.append(price_range)
                        sales_at_price[price_range] += 1
                        revenue_at_price[price_range] += estimated_price
        
        # 计算最佳价格区间
        if price_ranges:
            # 找出销量最高的价格区间
            best_sales_price = max(sales_at_price.items(), key=lambda x: x[1])[0]
            
            # 找出收入最高的价格区间
            best_revenue_price = max(revenue_at_price.items(), key=lambda x: x[1])[0]
            
            # 计算价格弹性
            price_elasticity = self._calculate_price_elasticity(sales_at_price)
        else:
            best_sales_price = 0
            best_revenue_price = 0
            price_elasticity = 0
        
        # 获取产品在config中定义的成本
        cost = self.data_provider.PRODUCT_COSTS.get(product_name, {}).get('cost', 0)
        
        # 计算不同价格区间的毛利率
        gross_margin_by_price = {}
        for price_range, revenue in revenue_at_price.items():
            sales = sales_at_price[price_range]
            if sales > 0 and revenue > 0:
                total_cost = sales * cost
                margin = ((revenue - total_cost) / revenue * 100)
                gross_margin_by_price[price_range] = round(margin, 1)
            else:
                gross_margin_by_price[price_range] = 0
        
        # 计算最佳价格点（销量、收入和毛利率的综合考虑）
        price_scores = {}
        for price_range in sales_at_price.keys():
            # 归一化各指标
            max_sales = max(sales_at_price.values()) if sales_at_price else 1
            max_revenue = max(revenue_at_price.values()) if revenue_at_price else 1
            max_margin = max(gross_margin_by_price.values()) if gross_margin_by_price else 1
            
            sales_norm = sales_at_price[price_range] / max_sales
            revenue_norm = revenue_at_price[price_range] / max_revenue
            margin_norm = gross_margin_by_price.get(price_range, 0) / max(max_margin, 1)
            
            # 综合评分 (销量30%，收入40%，毛利率30%)
            price_scores[price_range] = sales_norm * 0.3 + revenue_norm * 0.4 + margin_norm * 0.3
        
        # 找出综合评分最高的价格
        optimal_price = max(price_scores.items(), key=lambda x: x[1])[0] if price_scores else 0
        
        return {
            'sales_by_price': dict(sorted(sales_at_price.items())),
            'revenue_by_price': dict(sorted({k: round(v, 2) for k, v in revenue_at_price.items()}.items())),
            'gross_margin_by_price': dict(sorted(gross_margin_by_price.items())),
            'best_sales_price': f"{best_sales_price}-{best_sales_price+50}",
            'best_revenue_price': f"{best_revenue_price}-{best_revenue_price+50}",
            'optimal_price_range': f"{optimal_price}-{optimal_price+50}",
            'price_elasticity': round(price_elasticity, 2),
            'price_sensitivity': "高" if price_elasticity > 1.5 else "中" if price_elasticity > 0.5 else "低"
        }
        
    def _calculate_price_elasticity(self, sales_at_price):
        """计算价格弹性"""
        if len(sales_at_price) < 2:
            return 0  # 至少需要两个价格点才能计算弹性
            
        # 对价格和销量数据排序
        price_sales = sorted(sales_at_price.items())
        
        # 计算各价格点间的弹性，取平均值
        elasticities = []
        for i in range(1, len(price_sales)):
            price1, sales1 = price_sales[i-1]
            price2, sales2 = price_sales[i]
            
            # 避免除零错误
            if price1 == 0 or price2 == 0 or sales1 == 0 or sales2 == 0:
                continue
                
            # 计算价格变化百分比
            price_change_pct = (price2 - price1) / price1
            
            # 计算销量变化百分比
            sales_change_pct = (sales2 - sales1) / sales1
            
            # 价格弹性 = 销量变化百分比 / 价格变化百分比
            if price_change_pct != 0:
                elasticity = abs(sales_change_pct / price_change_pct)
                elasticities.append(elasticity)
        
        # 返回平均弹性
        return sum(elasticities) / len(elasticities) if elasticities else 0 