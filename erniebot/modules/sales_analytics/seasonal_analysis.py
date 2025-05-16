#coding=utf-8
"""
季节性分析模块 - 负责分析产品在不同季节的表现及季节性推荐
"""

class SeasonalAnalyzer:
    """季节性分析器，负责分析产品在不同季节的表现及季节性推荐"""
    
    def __init__(self, data_provider):
        """
        初始化季节性分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def analyze_seasonal_performance(self, product_name):
        """分析产品在不同季节的表现"""
        seasonal_sales = {season: 0 for season in self.data_provider.SEASONS.keys()}
        seasonal_revenue = {season: 0 for season in self.data_provider.SEASONS.keys()}
        
        # 遍历销售数据，按季节统计
        for day, sales in enumerate(self.data_provider.daily_sales_by_product.get(product_name, [])):
            day_number = day + 1  # 天数从1开始
            for season, days in self.data_provider.SEASONS.items():
                if day_number in days:
                    seasonal_sales[season] += sales
                    # 如果有收入数据也按季节统计
                    if day < len(self.data_provider.daily_revenue_by_product.get(product_name, [])):
                        seasonal_revenue[season] += self.data_provider.daily_revenue_by_product[product_name][day]
                    break
        
        # 计算总销量和总收入
        total_sales = sum(seasonal_sales.values())
        total_revenue = sum(seasonal_revenue.values())
        
        # 计算每个季节的销售占比
        seasonal_sales_percentage = {}
        for season, sales in seasonal_sales.items():
            percentage = (sales / total_sales * 100) if total_sales > 0 else 0
            seasonal_sales_percentage[season] = round(percentage, 1)
        
        # 找出最佳销售季节
        best_season = max(seasonal_sales.items(), key=lambda x: x[1])[0] if total_sales > 0 else None
        
        # 检查产品是否在季节性推荐列表中
        is_seasonal_fit = {}
        for season, products in self.data_provider.SEASONAL_PREFERENCES.items():
            is_seasonal_fit[season] = product_name in products
        
        # 计算不同消费者群体在各季节对该产品的购买倾向
        consumer_seasonal_interest = {}
        for consumer_type, seasonal_prefs in self.data_provider.CONSUMER_SEASONAL_PREFERENCES.items():
            consumer_seasonal_interest[consumer_type] = {}
            for season, preferred_products in seasonal_prefs.items():
                # 如果产品在该消费者群体的季节性偏好列表中，标记为高兴趣
                interest_level = "高" if product_name in preferred_products else "中" if season == best_season else "低"
                consumer_seasonal_interest[consumer_type][season] = interest_level
        
        # 季节性销售趋势（比较相邻季节的销售变化）
        seasonal_trend = {}
        seasons_list = list(self.data_provider.SEASONS.keys())
        for i in range(len(seasons_list)):
            current_season = seasons_list[i]
            next_season = seasons_list[(i + 1) % len(seasons_list)]
            current_sales = seasonal_sales[current_season]
            next_sales = seasonal_sales[next_season]
            
            if current_sales > 0:
                change_percentage = ((next_sales - current_sales) / current_sales * 100)
                trend = "上升" if change_percentage > 10 else "稳定" if change_percentage >= -10 else "下降"
            else:
                trend = "未知" if next_sales == 0 else "上升"
                
            seasonal_trend[f"{current_season}到{next_season}"] = {
                "变化": trend,
                "变化百分比": round(((next_sales - current_sales) / max(1, current_sales) * 100), 1)
            }
        
        return {
            'seasonal_sales': seasonal_sales,
            'seasonal_sales_percentage': seasonal_sales_percentage,
            'seasonal_revenue': seasonal_revenue,
            'best_season': best_season,
            'seasonal_fit': is_seasonal_fit,
            'consumer_seasonal_interest': consumer_seasonal_interest,
            'seasonal_trend': seasonal_trend
        }
        
    def get_current_season(self, day):
        """根据天数获取当前季节"""
        for season, days in self.data_provider.SEASONS.items():
            if day in days:
                return season
        return "未知"
        
    def recommend_seasonal_products(self, day, consumer_type=None):
        """根据当前季节和消费者类型推荐产品"""
        current_season = self.get_current_season(day)
        
        # 如果指定了消费者类型，使用该类型的季节性偏好
        if consumer_type and consumer_type in self.data_provider.CONSUMER_SEASONAL_PREFERENCES:
            if current_season in self.data_provider.CONSUMER_SEASONAL_PREFERENCES[consumer_type]:
                return {
                    'season': current_season,
                    'recommended_products': self.data_provider.CONSUMER_SEASONAL_PREFERENCES[consumer_type][current_season]
                }
        
        # 否则使用一般季节性偏好
        if current_season in self.data_provider.SEASONAL_PREFERENCES:
            return {
                'season': current_season,
                'recommended_products': self.data_provider.SEASONAL_PREFERENCES[current_season]
            }
            
        # 如果没有季节数据，返回空列表
        return {
            'season': current_season,
            'recommended_products': []
        } 