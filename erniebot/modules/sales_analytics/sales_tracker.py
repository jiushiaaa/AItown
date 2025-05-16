#coding=utf-8
"""
销售跟踪核心模块 - 用于记录和协调销售数据分析
"""

from collections import defaultdict
from ..config import PRODUCT_COSTS, SEASONS, SEASONAL_PREFERENCES, CONSUMER_SEASONAL_PREFERENCES, CONSUMER_TYPES_MAPPING
import random

from .product_metrics import ProductMetricsAnalyzer
from .product_lifecycle import ProductLifecycleAnalyzer
from .consumer_analysis import ConsumerAnalyzer
from .price_analysis import PriceAnalyzer
from .product_association import ProductAssociationAnalyzer
from .seasonal_analysis import SeasonalAnalyzer
from .loyalty_program import LoyaltyProgramAnalyzer
from .report_generator import ReportGenerator

class SalesTracker:
    """销售跟踪器类，用于记录和分析销售数据"""
    
    def __init__(self):
        """初始化销售跟踪器"""
        # 初始化基础数据存储
        self.daily_sales_by_product = defaultdict(list)  # 记录每个产品每天的销量
        self.daily_revenue_by_product = defaultdict(list)  # 记录每个产品每天的收入
        self.customer_purchase_history = defaultdict(list)  # 记录每个顾客的购买历史
        self.product_stock = {p: data["initial_stock"] for p, data in PRODUCT_COSTS.items()}
        self.repurchase_count = defaultdict(int)  # 记录产品的复购次数
        self.first_purchase_count = defaultdict(int)  # 记录产品的首次购买次数
        self.daily_marketing_cost = []  # 每日营销成本
        self.daily_operational_cost = []  # 每日运营成本
        self.bundled_sales = defaultdict(int)  # 连带销售次数
        self.new_product_name = ""  # 新产品名称，用于特别跟踪
        
        # 会员积分系统相关数据
        self.customer_points = defaultdict(int)  # 每个顾客的积分
        self.points_usage_history = defaultdict(list)  # 积分使用历史
        self.points_earned_history = defaultdict(list)  # 积分获取历史
        self.loyalty_tier = defaultdict(str)  # 会员等级：普通、银卡、金卡、钻石
        self.points_redemption_count = 0  # 积分兑换次数
        self.points_earned_total = 0  # 总获取积分数
        self.points_used_total = 0  # 总使用积分数
        
        # 为分析器提供常量
        self.PRODUCT_COSTS = PRODUCT_COSTS
        self.SEASONS = SEASONS
        self.SEASONAL_PREFERENCES = SEASONAL_PREFERENCES
        self.CONSUMER_SEASONAL_PREFERENCES = CONSUMER_SEASONAL_PREFERENCES
        self.CONSUMER_TYPES_MAPPING = CONSUMER_TYPES_MAPPING
        
        # 初始化各个分析器
        self._init_analyzers()
        
    def _init_analyzers(self):
        """初始化各个分析器"""
        self.product_metrics = ProductMetricsAnalyzer(self)
        self.lifecycle_analyzer = ProductLifecycleAnalyzer(self)
        self.consumer_analyzer = ConsumerAnalyzer(self)
        self.price_analyzer = PriceAnalyzer(self)
        self.association_analyzer = ProductAssociationAnalyzer(self)
        self.seasonal_analyzer = SeasonalAnalyzer(self)
        self.loyalty_analyzer = LoyaltyProgramAnalyzer(self)
        self.report_generator = ReportGenerator(self)
        
    def record_daily_sales(self, day, daily_interactions, daily_stats):
        """记录每日销售数据"""
        # 初始化当天各产品销量为0
        daily_product_sales = defaultdict(int)
        daily_product_revenue = defaultdict(float)
        
        # 营销和运营成本（根据客流量和销售额估算）
        customer_flow = daily_stats.get('customer_flow', 0)
        total_sales = daily_stats.get('total_sales', 0)
        
        # 基础营销成本 + 随客流量增加的部分
        marketing_cost = 500 + (customer_flow * 5)  # 基础500元 + 每位顾客5元营销成本
        operational_cost = 1000 + (total_sales * 0.1)  # 基础1000元 + 销售额10%的运营成本
        
        self.daily_marketing_cost.append(marketing_cost)
        self.daily_operational_cost.append(operational_cost)
        
        # 分析每次交互
        customers_today = set()  # 记录当天的顾客
        
        # 检查是否有积分兑换活动
        is_promotion_day = daily_stats.get('is_promotion_day', False)
        points_bonus_day = is_promotion_day or random.random() < 0.15  # 促销日或随机15%的几率有积分加倍
        points_multiplier = 2 if points_bonus_day else 1  # 积分倍数
        
        # 存储当天的客户交互，供分析器使用
        self.customer_interactions = defaultdict(list)
        self.customer_interactions[day] = daily_interactions
        
        for interaction in daily_interactions:
            customer_name = interaction.get('name', '')
            if not customer_name:
                continue
                
            customers_today.add(customer_name)
            behavior = interaction.get('behavior', {})
            
            if behavior.get('made_purchase', False):
                items = behavior.get('items_purchased', [])
                
                # 如果只购买了一个产品，不计为连带销售
                if len(items) > 1:
                    for item in items:
                        self.bundled_sales[item] += 1
                
                # 记录顾客购买历史
                amount_spent = behavior.get('amount_spent', 0)
                purchase_record = {
                    'day': day,
                    'items': items,
                    'amount': amount_spent
                }
                self.customer_purchase_history[customer_name].append(purchase_record)
                
                # 检查是否存在复购行为
                previous_purchases = [
                    record for record in self.customer_purchase_history[customer_name][:-1]
                ]
                
                # 会员积分计算：每消费1元获得1积分，促销日获得双倍积分
                points_earned = amount_spent * points_multiplier
                self.customer_points[customer_name] += points_earned
                self.points_earned_total += points_earned
                
                # 记录积分获得历史
                self.points_earned_history[customer_name].append({
                    'day': day,
                    'points': points_earned,
                    'reason': '购物消费',
                    'amount': amount_spent
                })
                
                # 更新会员等级
                total_points = self.customer_points[customer_name]
                if total_points > 10000:
                    self.loyalty_tier[customer_name] = '钻石会员'
                elif total_points > 5000:
                    self.loyalty_tier[customer_name] = '金卡会员'
                elif total_points > 2000:
                    self.loyalty_tier[customer_name] = '银卡会员'
                else:
                    self.loyalty_tier[customer_name] = '普通会员'
                
                for item in items:
                    # 记录产品销量和收入
                    daily_product_sales[item] += 1
                    
                    # 计算单个产品的收入（平均分配总消费金额）
                    item_revenue = amount_spent / len(items)
                    daily_product_revenue[item] += item_revenue
                    
                    # 更新库存
                    if item in self.product_stock:
                        self.product_stock[item] = max(0, self.product_stock[item] - 1)
                    
                    # 判断是否为复购
                    is_repurchase = False
                    for prev_record in previous_purchases:
                        if item in prev_record['items']:
                            is_repurchase = True
                            self.repurchase_count[item] += 1
                            break
                    
                    if not is_repurchase:
                        self.first_purchase_count[item] += 1
            
            # 会员积分兑换模拟
            self._simulate_points_redemption(interaction, customer_name, day, is_promotion_day)
        
        # 更新每日销售数据
        for product, sales in daily_product_sales.items():
            self.daily_sales_by_product[product].append(sales)
        
        for product, revenue in daily_product_revenue.items():
            self.daily_revenue_by_product[product].append(revenue)
            
        # 为没有销售的产品添加0记录，保证数据连续性
        for product in PRODUCT_COSTS.keys():
            if product not in daily_product_sales:
                self.daily_sales_by_product[product].append(0)
            if product not in daily_product_revenue:
                self.daily_revenue_by_product[product].append(0)
    
    def _simulate_points_redemption(self, interaction, customer_name, day, is_promotion_day):
        """模拟会员积分兑换行为"""
        # 在会员服务区，且有一定积分的顾客有概率使用积分
        location = interaction.get('location', '')
        visit_count = interaction.get('visit_count', 1)
        available_points = self.customer_points[customer_name]
        
        if location == '会员服务区' and available_points >= 300 and visit_count > 1:
            # 积分兑换概率随着积分数量和会员等级提高
            redemption_chance = min(0.8, (available_points / 8000) + (visit_count / 15))
            
            # 促销日增加积分兑换概率
            if is_promotion_day:
                redemption_chance += 0.3
            
            if random.random() < redemption_chance:
                # 决定兑换的积分数量
                redemption_amount = min(available_points, random.choice([500, 800, 1000, 1500]))
                
                # 更新积分
                self.customer_points[customer_name] -= redemption_amount
                self.points_used_total += redemption_amount
                self.points_redemption_count += 1
                
                # 记录兑换历史
                redemption_items = []
                if redemption_amount >= 1000:
                    redemption_items = ["礼品茶叶"]
                elif redemption_amount >= 800:
                    redemption_items = ["精美茶具"]
                else:
                    redemption_items = ["店铺优惠券"]
                    
                self.points_usage_history[customer_name].append({
                    'day': day,
                    'points_used': redemption_amount,
                    'items_redeemed': redemption_items
                })
                
                # 如果顾客有评论，添加兑换相关信息
                if 'comments' in interaction and '积分' in interaction['comments']:
                    interaction['comments'] = f"用{redemption_amount}积分兑换了{redemption_items[0]}，服务很贴心，积分兑换很实惠。"
    
    # 以下是对各个分析器的委托方法
    def calculate_product_metrics(self, product_name):
        """计算特定产品的销售指标"""
        return self.product_metrics.calculate_product_metrics(product_name)
    
    def get_top_products(self, limit=5):
        """获取销量最高的产品"""
        return self.product_metrics.get_top_products(limit)
    
    def analyze_new_product_performance(self):
        """分析新产品的表现"""
        if not self.new_product_name:
            return None
            
        metrics = self.calculate_product_metrics(self.new_product_name)
        top_products = self.get_top_products()
        
        # 确认新产品在畅销产品中的排名
        new_product_rank = None
        for rank, (product, _) in enumerate(top_products):
            if product == self.new_product_name:
                new_product_rank = rank + 1
                break
        
        # 调用生命周期分析器获取更详细的分析
        lifecycle_analysis = self.lifecycle_analyzer.analyze_product_lifecycle(self.new_product_name)
        
        # 计算市场份额
        all_sales = sum(sum(sales) for sales in self.daily_sales_by_product.values())
        new_product_sales = sum(self.daily_sales_by_product.get(self.new_product_name, [0]))
        market_share = (new_product_sales / all_sales * 100) if all_sales > 0 else 0
        
        # 判断爆款潜力
        score = metrics['popularity_score']
        if score >= 80:
            potential = "极高"
            conclusion = "该产品很可能成为爆款，各项指标表现优异"
        elif score >= 65:
            potential = "较高"
            conclusion = "该产品有望成为爆款，主要指标表现良好"
        elif score >= 50:
            potential = "中等"
            conclusion = "该产品有一定爆款潜力，但需优化部分指标"
        elif score >= 35:
            potential = "较低"
            conclusion = "该产品成为爆款的可能性不大，多项指标表现欠佳"
        else:
            potential = "极低"
            conclusion = "该产品难以成为爆款，需要全面重新评估产品定位"
        
        # 制定改进建议
        suggestions = []
        if metrics['repurchase_rate'] < 30:
            suggestions.append("提高产品质量和口感，增强顾客复购意愿")
        if metrics['bundled_sales_ratio'] < 20:
            suggestions.append("优化产品组合销售策略，增加连带销售机会")
        if metrics['gross_margin'] < 40:
            suggestions.append("优化成本结构或调整定价策略，提升毛利率")
        if metrics['inventory_turnover'] < 30:
            suggestions.append("调整库存管理，避免积压")
        if metrics['first_week_growth'] < 20:
            suggestions.append("加强新品推广和营销力度，提高初期增长率")
        
        return {
            'metrics': metrics,
            'market_share': round(market_share, 1),
            'rank': new_product_rank,
            'potential': potential,
            'conclusion': conclusion,
            'suggestions': suggestions,
            'lifecycle_stage': lifecycle_analysis.get('stage', '引入期')
        }
        
    def generate_simulation_summary(self, all_data):
        """生成模拟总结报告"""
        return self.report_generator.generate_simulation_summary(all_data)
        
    def _calculate_inventory_turnover(self):
        """计算库存周转率"""
        total_stock_used = 0
        total_initial_stock = 0
        
        for product, initial_stock in self.product_stock.items():
            initial = PRODUCT_COSTS.get(product, {}).get('initial_stock', 0)
            current = self.product_stock.get(product, 0)
            total_initial_stock += initial
            total_stock_used += (initial - current)
        
        if total_initial_stock > 0:
            return round((total_stock_used / total_initial_stock) * 100, 1)
        return 0
        
    # 会员积分系统分析委托
    def get_loyalty_program_metrics(self):
        """获取会员积分系统的各项指标"""
        return self.loyalty_analyzer.get_loyalty_program_metrics()
    
    # 产品生命周期分析委托
    def get_product_lifecycle_analysis(self, product_name):
        """获取产品生命周期分析结果"""
        return self.lifecycle_analyzer.analyze_product_lifecycle(product_name)
    
    def get_product_maturity_index(self, product_name):
        """获取产品成熟度指数"""
        return self.lifecycle_analyzer.calculate_product_maturity_index(product_name)
    
    def forecast_product_sales(self, product_name, days=30):
        """预测产品未来销售趋势"""
        return self.lifecycle_analyzer.forecast_sales_trend(product_name, days)
    
    # 价格分析委托
    def analyze_price_sensitivity(self, product_name):
        """分析产品价格变化对销量的影响"""
        return self.price_analyzer.analyze_price_sensitivity(product_name)
    
    # 消费者分析委托
    def get_consumer_insights(self, product_name):
        """获取特定产品的消费者洞察"""
        return self.consumer_analyzer.get_consumer_insights(product_name)
    
    def analyze_consumer_product_match(self):
        """分析不同消费者类型与产品的匹配度"""
        return self.consumer_analyzer.analyze_consumer_product_match()
    
    # 产品关联分析委托
    def analyze_product_associations(self, product_name=None):
        """分析产品间关联性，找出经常一起购买的产品组合"""
        return self.association_analyzer.analyze_product_associations(product_name)
    
    def find_related_products(self, product_name, relation_type='complementary'):
        """查找与指定产品相关的产品"""
        return self.association_analyzer.find_related_products(product_name, relation_type)
    
    # 季节性分析委托
    def analyze_seasonal_performance(self, product_name):
        """分析产品在不同季节的表现"""
        return self.seasonal_analyzer.analyze_seasonal_performance(product_name)
    
    def get_current_season(self, day):
        """根据天数获取当前季节"""
        return self.seasonal_analyzer.get_current_season(day)
    
    def recommend_seasonal_products(self, day, consumer_type=None):
        """根据当前季节和消费者类型推荐产品"""
        return self.seasonal_analyzer.recommend_seasonal_products(day, consumer_type)
    
    # 综合报告生成委托
    def generate_comprehensive_product_report(self, product_name):
        """生成产品综合分析报告"""
        return self.report_generator.generate_comprehensive_product_report(product_name)
    
    def analyze_regional_distribution(self):
        """分析产品在不同地域的销售分布"""
        # 创建一个简单的地域分析结果
        regions = ["华东", "华南", "华北", "西南", "西北", "东北", "华中"]
        distribution = {}
        
        # 生成模拟的地域分布数据
        total = 100.0
        remaining = total
        for region in regions[:-1]:
            value = round(remaining * (0.1 + 0.2 * random.random()), 1)
            distribution[region] = value
            remaining -= value
        
        # 最后一个地区分配剩余比例
        distribution[regions[-1]] = round(remaining, 1)
        
        # 返回分析结果
        return {
            "region_distribution": distribution,
            "primary_regions": [regions[0], regions[1]],  # 主要区域
            "growth_regions": [regions[3], regions[4]],   # 增长区域
            "recommendation": "建议加强在西南和西北地区的市场推广"
        }
    
    def analyze_consumer_psychology(self):
        """分析消费者心理特征"""
        # 创建一个简单的消费者心理分析结果
        psychology_factors = {
            "品质驱动": random.uniform(7.5, 9.5),
            "价格敏感": random.uniform(4.0, 7.0),
            "品牌忠诚": random.uniform(6.0, 8.5),
            "社交影响": random.uniform(5.0, 8.0),
            "健康意识": random.uniform(7.0, 9.0),
            "文化认同": random.uniform(6.5, 9.0),
            "新鲜感追求": random.uniform(3.0, 7.0)
        }
        
        # 找出主要驱动因素和次要驱动因素
        sorted_factors = sorted(psychology_factors.items(), key=lambda x: x[1], reverse=True)
        primary_factors = [factor[0] for factor in sorted_factors[:2]]
        secondary_factors = [factor[0] for factor in sorted_factors[2:4]]
        
        # 返回分析结果
        return {
            "psychology_factors": psychology_factors,
            "primary_drivers": primary_factors,
            "secondary_drivers": secondary_factors,
            "recommendation": "营销策略应突出产品品质和文化价值，增强消费者认同感"
        } 