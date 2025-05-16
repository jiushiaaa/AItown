#coding=utf-8
"""
销售报告生成模块 - 负责生成综合销售报告
"""

from collections import defaultdict
import datetime

class ReportGenerator:
    """销售报告生成器，负责整合各类分析结果生成报告"""
    
    def __init__(self, data_provider):
        """
        初始化报告生成器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def generate_simulation_summary(self, all_data):
        """生成模拟总结报告"""
        try:
            total_days = len(all_data)
            if total_days == 0:
                return "没有可分析的数据"
                
            last_day_data = all_data[-1]
            
            # 统计不同消费者类型的总客流和销售额
            consumer_type_stats = defaultdict(lambda: {"visits": 0, "purchases": 0, "sales": 0, "avg_satisfaction": 0})
            consumer_type_visits = defaultdict(int)
            consumer_age_groups = {"25-35": 0, "36-45": 0, "46-55": 0, "56+": 0}
            
            # 统计促销日相关数据
            promo_days_count = 0
            promo_days_sales = 0
            normal_days_count = 0
            normal_days_sales = 0
            
            # 收集每天的数据
            for day_data in all_data:
                daily_stats = day_data.get('daily_stats', {})
                
                # 检查是否是促销日
                is_promo_day = daily_stats.get('is_promotion_day', False)
                if is_promo_day:
                    promo_days_count += 1
                    promo_days_sales += daily_stats.get('total_sales', 0)
                else:
                    normal_days_count += 1
                    normal_days_sales += daily_stats.get('total_sales', 0)
                
                # 分析消费者互动
                for interaction in day_data.get('customer_interactions', []):
                    consumer_type = interaction.get('type', '')
                    age = interaction.get('age', 0)
                    behavior = interaction.get('behavior', {})
                    
                    # 按年龄段统计
                    if age >= 56:
                        consumer_age_groups["56+"] += 1
                    elif age >= 46:
                        consumer_age_groups["46-55"] += 1
                    elif age >= 36:
                        consumer_age_groups["36-45"] += 1
                    else:
                        consumer_age_groups["25-35"] += 1
                    
                    if consumer_type:
                        consumer_type_visits[consumer_type] += 1
                        consumer_type_stats[consumer_type]["visits"] += 1
                        
                        if behavior.get('made_purchase', False):
                            consumer_type_stats[consumer_type]["purchases"] += 1
                            consumer_type_stats[consumer_type]["sales"] += behavior.get('amount_spent', 0)
                            
                            if behavior.get('satisfaction') is not None:
                                consumer_type_stats[consumer_type]["avg_satisfaction"] += behavior.get('satisfaction', 0)
            
            # 计算每种消费者类型的平均值
            for consumer_type, stats in consumer_type_stats.items():
                if stats["purchases"] > 0:
                    stats["avg_satisfaction"] = round(stats["avg_satisfaction"] / stats["purchases"], 1)
                    stats["conversion_rate"] = round((stats["purchases"] / stats["visits"]) * 100, 1)
                    stats["avg_expense"] = round(stats["sales"] / stats["purchases"])
                else:
                    stats["avg_satisfaction"] = 0
                    stats["conversion_rate"] = 0
                    stats["avg_expense"] = 0
            
            # 计算各类消费者的占比
            total_visits = sum(consumer_type_visits.values())
            consumer_type_percentages = {}
            
            for consumer_type, visits in consumer_type_visits.items():
                consumer_type_percentages[consumer_type] = round((visits / total_visits) * 100, 1) if total_visits > 0 else 0
            
            # 计算促销日的效果
            if promo_days_count > 0 and normal_days_count > 0:
                avg_promo_day_sales = promo_days_sales / promo_days_count
                avg_normal_day_sales = normal_days_sales / normal_days_count
                promo_effect = round(((avg_promo_day_sales / avg_normal_day_sales) - 1) * 100, 1) if avg_normal_day_sales > 0 else 0
            else:
                avg_promo_day_sales = 0
                avg_normal_day_sales = 0
                promo_effect = 0
            
            # 获取畅销产品
            top_products = self.data_provider.get_top_products(5)
            top_product_list = [{"name": product, "sales": sales} for product, sales in top_products]
            
            # 获取会员系统指标
            loyalty_metrics = self.data_provider.get_loyalty_program_metrics()
            
            # 特别分析年轻消费者
            young_consumer_stats = consumer_type_stats.get("年轻新贵", {})
            young_consumer_percentage = consumer_type_percentages.get("年轻新贵", 0)
            
            # 分析年轻人茶叶偏好
            young_consumer_products = []
            for day_data in all_data:
                for interaction in day_data.get('customer_interactions', []):
                    if interaction.get('type') == "年轻新贵" and interaction.get('behavior', {}).get('made_purchase', False):
                        young_consumer_products.extend(interaction.get('behavior', {}).get('items_purchased', []))
            
            # 统计产品频率
            product_frequency = defaultdict(int)
            for product in young_consumer_products:
                product_frequency[product] += 1
            
            # 获取年轻人前3喜爱的产品
            young_favorite_products = sorted(product_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            young_favorite_product_list = [{"name": product, "count": count} for product, count in young_favorite_products]
            
            # 生成总结报告
            summary = {
                "days_simulated": total_days,
                "final_stats": {
                    "total_customers": last_day_data.get('cumulative_stats', {}).get('total_customers', 0),
                    "unique_customers": last_day_data.get('cumulative_stats', {}).get('unique_customers', 0),
                    "total_revenue": last_day_data.get('cumulative_stats', {}).get('total_revenue', 0),
                    "customer_retention": last_day_data.get('cumulative_stats', {}).get('customer_retention', '0%')
                },
                "consumer_insights": {
                    "consumer_type_percentages": consumer_type_percentages,
                    "consumer_type_stats": {k: v for k, v in consumer_type_stats.items()},
                    "age_distribution": {k: round((v / total_visits) * 100, 1) if total_visits > 0 else 0 for k, v in consumer_age_groups.items()}
                },
                "product_insights": {
                    "top_products": top_product_list,
                    "inventory_turnover": self.data_provider._calculate_inventory_turnover()
                },
                "loyalty_program": loyalty_metrics,
                "promotion_effects": {
                    "promo_days_count": promo_days_count,
                    "promo_days_sales_avg": int(avg_promo_day_sales),
                    "normal_days_sales_avg": int(avg_normal_day_sales),
                    "sales_increase_percentage": promo_effect
                },
                "young_consumer_analysis": {
                    "percentage": young_consumer_percentage,
                    "conversion_rate": young_consumer_stats.get("conversion_rate", 0),
                    "avg_expense": young_consumer_stats.get("avg_expense", 0),
                    "favorite_products": young_favorite_product_list
                },
                "new_product_metrics": None
            }
            
            # 如果有新产品，添加新产品分析
            if self.data_provider.new_product_name:
                new_product_metrics = self.data_provider.calculate_product_metrics(self.data_provider.new_product_name)
                summary["new_product_metrics"] = {
                    "name": self.data_provider.new_product_name,
                    "total_sales": new_product_metrics.get('total_sales', 0),
                    "repurchase_rate": new_product_metrics.get('repurchase_rate', 0),
                    "popularity_score": new_product_metrics.get('popularity_score', 0)
                }
            
            return summary
        except Exception as e:
            print(f"生成模拟总结时出错: {str(e)}")
            return f"模拟总结生成失败：{str(e)}"
    
    def generate_comprehensive_product_report(self, product_name):
        """生成产品综合分析报告"""
        report = {}
        
        # 基本产品指标
        try:
            report['basic_metrics'] = self.data_provider.calculate_product_metrics(product_name)
        except Exception as e:
            report['basic_metrics'] = {'error': f"计算基本指标时出错: {str(e)}"}
        
        # 产品生命周期分析
        try:
            report['lifecycle_analysis'] = self.data_provider.get_product_lifecycle_analysis(product_name)
        except Exception as e:
            report['lifecycle_analysis'] = {'error': f"生命周期分析时出错: {str(e)}"}
        
        # 产品成熟度指数
        try:
            report['maturity_index'] = self.data_provider.get_product_maturity_index(product_name)
        except Exception as e:
            report['maturity_index'] = {'error': f"计算成熟度指数时出错: {str(e)}"}
        
        # 价格敏感度分析
        try:
            report['price_sensitivity'] = self.data_provider.analyze_price_sensitivity(product_name)
        except Exception as e:
            report['price_sensitivity'] = {'error': f"价格敏感度分析时出错: {str(e)}"}
        
        # 消费者洞察
        try:
            report['consumer_insights'] = self.data_provider.get_consumer_insights(product_name)
        except Exception as e:
            report['consumer_insights'] = {'error': f"获取消费者洞察时出错: {str(e)}"}
        
        # 产品关联分析
        try:
            report['product_associations'] = self.data_provider.analyze_product_associations()
        except Exception as e:
            report['product_associations'] = {'error': f"产品关联分析时出错: {str(e)}"}
        
        # 季节性分析
        try:
            report['seasonal_analysis'] = self.data_provider.analyze_seasonal_performance(product_name)
        except Exception as e:
            report['seasonal_analysis'] = {'error': f"季节性分析时出错: {str(e)}"}
        
        # 销售预测
        try:
            report['sales_forecast'] = self.data_provider.forecast_product_sales(product_name)
        except Exception as e:
            report['sales_forecast'] = {'error': f"销售预测时出错: {str(e)}"}
        
        # 添加报告生成时间
        report['generated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report['product_name'] = product_name
        
        return report 