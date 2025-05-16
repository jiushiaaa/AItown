#coding=utf-8
"""
产品指标分析模块 - 负责计算和分析产品的各项销售指标
"""

from collections import defaultdict

class ProductMetricsAnalyzer:
    """产品指标分析器，负责计算产品的各类销售指标"""
    
    def __init__(self, data_provider):
        """
        初始化产品指标分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
        
    def calculate_product_metrics(self, product_name):
        """计算特定产品的销售指标"""
        sales_data = self.data_provider.daily_sales_by_product.get(product_name, [])
        revenue_data = self.data_provider.daily_revenue_by_product.get(product_name, [])
        
        if not sales_data:
            return self._get_empty_metrics()
        
        # 基础销售指标
        total_sales = sum(sales_data)
        first_week_sales = self._calculate_first_week_sales(sales_data)
        first_week_growth = self._calculate_first_week_growth(sales_data)
        
        # 复购相关指标
        first_purchases = self.data_provider.first_purchase_count.get(product_name, 0)
        repurchases = self.data_provider.repurchase_count.get(product_name, 0)
        repurchase_rate = (repurchases / first_purchases * 100) if first_purchases > 0 else 0
        
        # 库存相关指标
        initial_stock = self.data_provider.PRODUCT_COSTS.get(product_name, {}).get('initial_stock', 100)
        current_stock = self.data_provider.product_stock.get(product_name, initial_stock)
        stock_sold = initial_stock - current_stock
        inventory_turnover = (stock_sold / initial_stock * 100) if initial_stock > 0 else 0
        
        # 连带销售指标
        bundled_sales = self.data_provider.bundled_sales.get(product_name, 0)
        bundled_sales_ratio = (bundled_sales / total_sales * 100) if total_sales > 0 else 0
        
        # 毛利率计算
        cost = self.data_provider.PRODUCT_COSTS.get(product_name, {}).get('cost', 0)
        total_revenue = sum(revenue_data)
        total_cost = total_sales * cost
        gross_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
        
        # 库存风险评估
        stock_risk = self._evaluate_stock_risk(sales_data, current_stock)
        
        # 高级指标计算
        sales_trend = self._calculate_sales_trend(sales_data)
        market_position = self._analyze_market_position(product_name)
        social_score = self._calculate_social_score(product_name)
        consumer_fit = self._calculate_consumer_fit(product_name)
        
        # 转换为标准得分
        scores = self._calculate_standard_scores(
            total_sales, first_week_growth, repurchase_rate, 
            inventory_turnover, gross_margin, sales_trend,
            market_position, social_score, consumer_fit
        )
        
        # 综合评分
        popularity_score = self._calculate_popularity_score(scores)
        
        return {
            'total_sales': total_sales,
            'first_week_sales': first_week_sales,
            'first_week_growth': round(first_week_growth, 1),
            'repurchase_rate': round(repurchase_rate, 1),
            'inventory_turnover': round(inventory_turnover, 1),
            'bundled_sales_ratio': round(bundled_sales_ratio, 1),
            'gross_margin': round(gross_margin, 1),
            'stock_risk': stock_risk,
            'sales_trend': round(sales_trend, 1),
            'market_position': round(market_position, 1),
            'social_score': round(social_score, 1),
            'consumer_fit': round(consumer_fit, 1),
            'popularity_score': round(popularity_score, 1)
        }
    
    def _get_empty_metrics(self):
        """返回空的指标结果"""
        return {
            'total_sales': 0,
            'first_week_sales': 0,
            'first_week_growth': 0,
            'repurchase_rate': 0,
            'inventory_turnover': 0,
            'bundled_sales_ratio': 0,
            'gross_margin': 0,
            'stock_risk': 'high',
            'sales_trend': 0,
            'market_position': 0,
            'social_score': 0,
            'consumer_fit': 0,
            'popularity_score': 0
        }
        
    def _calculate_first_week_sales(self, sales_data):
        """计算首周销量"""
        return sum(sales_data[:min(7, len(sales_data))])
        
    def _calculate_first_week_growth(self, sales_data):
        """计算首周销售增长率"""
        if len(sales_data) >= 7 and sum(sales_data[:3]) > 0:
            first_days = sum(sales_data[:3])  # 前3天
            later_days = sum(sales_data[3:7])  # 第4-7天
            return (later_days - first_days) / first_days * 100 if first_days > 0 else 0
        return 0
        
    def _evaluate_stock_risk(self, sales_data, current_stock):
        """评估库存风险"""
        days_of_data = len(sales_data)
        if days_of_data > 0:
            avg_daily_sales = sum(sales_data) / days_of_data
            days_of_stock_left = current_stock / avg_daily_sales if avg_daily_sales > 0 else float('inf')
            
            if days_of_stock_left < 15:
                return 'low'  # 库存将在15天内售罄，风险低
            elif days_of_stock_left < 30:
                return 'medium'  # 库存将在30天内售罄，风险中等
            else:
                return 'high'  # 库存超过30天，风险高
        return 'high'
        
    def _calculate_standard_scores(self, total_sales, growth_rate, repurchase_rate, 
                                  inventory_turnover, gross_margin, sales_trend,
                                  market_position, social_score, consumer_fit):
        """计算各指标的标准得分"""
        sales_score = min(100, total_sales / 10)  # 基于总销量，每10件满分
        growth_score = min(100, max(0, growth_rate))  # 基于首周增长率
        repurchase_score = min(100, repurchase_rate * 2)  # 基于复购率，50%复购率满分
        turnover_score = min(100, inventory_turnover * 2)  # 基于库存周转，50%周转率满分
        margin_score = min(100, gross_margin * 2)  # 基于毛利率，50%毛利率满分
        
        return {
            'sales_score': sales_score,
            'growth_score': growth_score,
            'repurchase_score': repurchase_score,
            'turnover_score': turnover_score,
            'margin_score': margin_score,
            'sales_trend': sales_trend,
            'market_position': market_position,
            'social_score': social_score,
            'consumer_fit': consumer_fit
        }
        
    def _calculate_popularity_score(self, scores):
        """计算综合人气评分"""
        return (
            scores['sales_score'] * 0.25 +
            scores['growth_score'] * 0.15 +
            scores['repurchase_score'] * 0.15 +
            scores['turnover_score'] * 0.10 +
            scores['margin_score'] * 0.10 +
            scores['sales_trend'] * 0.10 +
            scores['market_position'] * 0.05 +
            scores['social_score'] * 0.05 +
            scores['consumer_fit'] * 0.05
        )
        
    def _calculate_sales_trend(self, sales_data):
        """计算销售趋势"""
        if len(sales_data) < 7:
            return 50  # 默认中等趋势

        # 计算后半段数据与前半段数据的比值
        mid_point = len(sales_data) // 2
        first_half = sum(sales_data[:mid_point])
        second_half = sum(sales_data[mid_point:])
        
        if first_half == 0:
            return 80 if second_half > 0 else 30  # 如果前半段没有销售，但后半段有，则趋势较好
            
        trend_ratio = (second_half / first_half) - 1
        
        # 转换为0-100的分数
        trend_score = 50 + trend_ratio * 50
        return min(100, max(0, trend_score))
        
    def _analyze_market_position(self, product_name):
        """分析产品的市场地位"""
        # 获取所有产品的总销量
        all_product_sales = {}
        for product, sales in self.data_provider.daily_sales_by_product.items():
            all_product_sales[product] = sum(sales)
            
        # 计算总销售量
        total_sales = sum(all_product_sales.values())
        if total_sales == 0:
            return 50  # 默认中等市场地位
            
        # 计算市场份额
        product_sales = all_product_sales.get(product_name, 0)
        market_share = product_sales / total_sales
        
        # 计算市场地位分数 (0-100)
        position_score = min(100, market_share * 300)  # 市场份额33%就可以得满分
        return position_score
        
    def _calculate_social_score(self, product_name):
        """计算社交媒体热度指数(模拟)"""
        # 在实际应用中，这可能与外部社交媒体API集成
        # 这里使用销售数据和复购率来模拟社交热度
        
        # 获取产品销售数据
        sales_data = self.data_provider.daily_sales_by_product.get(product_name, [])
        if not sales_data:
            return 50  # 默认中等热度
            
        # 使用销售波动性作为热度的一个指标
        if len(sales_data) < 3:
            volatility = 0
        else:
            # 计算销售数据的标准差/平均值作为波动系数
            mean_sales = sum(sales_data) / len(sales_data)
            if mean_sales == 0:
                volatility = 0
            else:
                squared_diffs = [(x - mean_sales) ** 2 for x in sales_data]
                std_dev = (sum(squared_diffs) / len(sales_data)) ** 0.5
                volatility = std_dev / mean_sales
        
        # 复购率作为流行度的另一个指标
        repurchases = self.data_provider.repurchase_count.get(product_name, 0)
        first_purchases = self.data_provider.first_purchase_count.get(product_name, 0)
        repurchase_rate = repurchases / first_purchases if first_purchases > 0 else 0
        
        # 结合波动性和复购率
        social_score = 50 + (volatility * 30) + (repurchase_rate * 30)
        return min(100, max(0, social_score))
        
    def _calculate_consumer_fit(self, product_name):
        """计算产品与目标消费者的契合度"""
        # 统计不同消费者类型购买该产品的次数
        consumer_type_count = defaultdict(int)
        consumer_type_total = defaultdict(int)
        
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            # 从名字猜测消费者类型 (在实际系统中应该有更好的方式)
            customer_type = None
            for type_name, names in self.data_provider.CONSUMER_TYPES_MAPPING.items():
                if customer in names:
                    customer_type = type_name
                    break
                    
            if not customer_type:
                continue
                
            # 统计该类型消费者的总购买次数
            consumer_type_total[customer_type] += len(purchases)
            
            # 统计该类型消费者购买该产品的次数
            for purchase in purchases:
                if product_name in purchase['items']:
                    consumer_type_count[customer_type] += 1
        
        # 计算产品在每个消费者类型中的渗透率
        penetration_rates = {}
        for consumer_type, total in consumer_type_total.items():
            if total > 0:
                penetration_rates[consumer_type] = consumer_type_count[consumer_type] / total
            else:
                penetration_rates[consumer_type] = 0
        
        # 计算最高渗透率和平均渗透率
        if penetration_rates:
            max_penetration = max(penetration_rates.values())
            avg_penetration = sum(penetration_rates.values()) / len(penetration_rates)
            
            # 如果产品有明确的目标群体，评分会更高
            consumer_fit_score = 50 + (max_penetration * 40) + (avg_penetration * 10)
        else:
            consumer_fit_score = 50  # 默认中等契合度
            
        return min(100, consumer_fit_score)
        
    def get_top_products(self, limit=5):
        """获取销量最高的产品"""
        product_total_sales = {}
        for product, sales in self.data_provider.daily_sales_by_product.items():
            product_total_sales[product] = sum(sales)
        
        return sorted(product_total_sales.items(), key=lambda x: x[1], reverse=True)[:limit] 