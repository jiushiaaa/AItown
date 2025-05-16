#coding=utf-8
"""
产品生命周期分析模块 - 分析产品所处的生命周期阶段及趋势
"""

class ProductLifecycleAnalyzer:
    """产品生命周期分析器，负责分析产品处于哪个生命周期阶段及趋势预测"""
    
    def __init__(self, data_provider):
        """
        初始化产品生命周期分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
        
    def analyze_product_lifecycle(self, product_name):
        """分析产品所处的生命周期阶段"""
        sales_data = self.data_provider.daily_sales_by_product.get(product_name, [])
        
        if not sales_data or len(sales_data) < 7:
            return {
                'stage': '引入期',
                'growth_rate': 0,
                'sales_stability': '不稳定',
                'market_share': 0,
                'recommendations': ['加大宣传力度', '提高产品知名度', '吸引早期采用者']
            }
            
        # 计算增长率
        first_week = sum(sales_data[:min(7, len(sales_data))])
        last_week = sum(sales_data[-7:]) if len(sales_data) >= 14 else sum(sales_data)
        
        if first_week > 0:
            growth_rate = (last_week - first_week) / first_week * 100
        else:
            growth_rate = 100 if last_week > 0 else 0
            
        # 计算市场份额
        total_market_sales = 0
        for product, sales in self.data_provider.daily_sales_by_product.items():
            total_market_sales += sum(sales)
            
        product_sales = sum(sales_data)
        market_share = (product_sales / total_market_sales * 100) if total_market_sales > 0 else 0
        
        # 计算销售稳定性（使用变异系数）
        sales_stability = self._calculate_sales_stability(sales_data)
        
        # 判断生命周期阶段
        stage, recommendations = self._determine_lifecycle_stage(sales_data, growth_rate, sales_stability)
            
        return {
            'stage': stage,
            'growth_rate': round(growth_rate, 1),
            'sales_stability': sales_stability,
            'market_share': round(market_share, 1),
            'total_sales': product_sales,
            'recommendations': recommendations
        }
    
    def _calculate_sales_stability(self, sales_data):
        """计算销售稳定性"""
        if len(sales_data) >= 7 and sum(sales_data) > 0:
            mean_sales = sum(sales_data) / len(sales_data)
            if mean_sales > 0:
                variance = sum((x - mean_sales) ** 2 for x in sales_data) / len(sales_data)
                std_deviation = variance ** 0.5
                coef_of_variation = std_deviation / mean_sales
                
                if coef_of_variation < 0.2:
                    return '非常稳定'
                elif coef_of_variation < 0.4:
                    return '稳定'
                elif coef_of_variation < 0.6:
                    return '一般'
                else:
                    return '不稳定'
            else:
                return '不稳定'
        else:
            return '数据不足'
    
    def _determine_lifecycle_stage(self, sales_data, growth_rate, sales_stability):
        """确定产品所处的生命周期阶段及推荐策略"""
        product_sales = sum(sales_data)
        
        if len(sales_data) < 7 or product_sales < 10:
            stage = '引入期'
            recommendations = ['加大宣传力度', '提高产品知名度', '吸引早期采用者']
        elif growth_rate > 30 and sales_stability in ['不稳定', '一般']:
            stage = '成长期'
            recommendations = ['扩大产品分销渠道', '考虑适当提价', '强化品牌认知']
        elif growth_rate > 5 or (growth_rate > -10 and sales_stability in ['稳定', '非常稳定']):
            stage = '成熟期'
            recommendations = ['推出产品变体', '强化客户忠诚度', '优化成本结构']
        elif growth_rate > -10 and sales_stability in ['不稳定', '一般']:
            stage = '饱和期'
            recommendations = ['考虑产品更新', '开发新客户群', '差异化营销']
        else:
            stage = '衰退期'
            recommendations = ['计划产品淘汰', '降价清理库存', '开发替代产品']
        
        return stage, recommendations
    
    def calculate_product_maturity_index(self, product_name):
        """计算产品成熟度指数 (0-100)"""
        lifecycle_analysis = self.analyze_product_lifecycle(product_name)
        stage = lifecycle_analysis.get('stage', '引入期')
        
        # 基础成熟度分数
        base_scores = {
            '引入期': 20,
            '成长期': 40,
            '成熟期': 80,
            '饱和期': 60,
            '衰退期': 30
        }
        
        base_score = base_scores.get(stage, 0)
        
        # 调整因素
        growth_rate = lifecycle_analysis.get('growth_rate', 0)
        stability = lifecycle_analysis.get('sales_stability', '不稳定')
        market_share = lifecycle_analysis.get('market_share', 0)
        
        # 计算稳定性加分
        stability_bonus = {
            '非常稳定': 15,
            '稳定': 10,
            '一般': 5,
            '不稳定': 0,
            '数据不足': 0
        }
        
        # 计算调整后的成熟度指数
        maturity_index = base_score
        
        # 增长率调整
        if stage == '成长期' and growth_rate > 50:
            maturity_index += 10
        elif stage == '成熟期' and growth_rate > 10:
            maturity_index += 5
        elif stage == '衰退期' and growth_rate < -20:
            maturity_index -= 10
            
        # 稳定性调整
        maturity_index += stability_bonus.get(stability, 0)
        
        # 市场份额调整
        if market_share > 30:
            maturity_index += 10
        elif market_share > 20:
            maturity_index += 5
        elif market_share > 10:
            maturity_index += 2
            
        # 确保指数在0-100范围内
        maturity_index = min(100, max(0, maturity_index))
        
        return {
            'maturity_index': round(maturity_index, 1),
            'stage': stage,
            'interpretation': self._interpret_maturity_index(maturity_index)
        }
    
    def _interpret_maturity_index(self, index):
        """解释成熟度指数的含义"""
        if index >= 85:
            return "产品高度成熟，在市场中有稳固地位"
        elif index >= 70:
            return "产品较为成熟，有良好的市场表现"
        elif index >= 50:
            return "产品处于发展阶段，有一定市场认可"
        elif index >= 30:
            return "产品尚处于市场开拓期，需要更多培育"
        else:
            return "产品处于初步探索阶段，市场认知度低"
    
    def forecast_sales_trend(self, product_name, days=30):
        """预测产品未来销售趋势"""
        sales_data = self.data_provider.daily_sales_by_product.get(product_name, [])
        
        if not sales_data or len(sales_data) < 7:
            return {
                'forecast': 'insufficient_data',
                'message': '数据不足以进行可靠预测',
                'estimated_growth': 0,
                'confidence': '低'
            }
        
        # 分析近期趋势 (最近7天与前7天比较)
        recent_days = min(7, len(sales_data))
        recent_sales = sales_data[-recent_days:]
        previous_sales = sales_data[-2*recent_days:-recent_days] if len(sales_data) >= 2*recent_days else []
        
        # 计算最近一段时间的平均日销量
        avg_daily_sales = sum(recent_sales) / len(recent_sales)
        
        # 计算增长率
        if previous_sales and sum(previous_sales) > 0:
            growth_rate = ((sum(recent_sales) - sum(previous_sales)) / sum(previous_sales)) * 100
        else:
            growth_rate = 0
        
        # 确定趋势类型
        if growth_rate > 20:
            trend = 'sharp_increase'
            message = f'预计{days}天内销量将大幅增长，增幅约{round(growth_rate, 1)}%'
            confidence = '中高' if len(sales_data) > 14 else '中'
        elif growth_rate > 5:
            trend = 'moderate_increase'
            message = f'预计{days}天内销量将稳步增长，增幅约{round(growth_rate, 1)}%'
            confidence = '高' if len(sales_data) > 14 else '中高'
        elif growth_rate > -5:
            trend = 'stable'
            message = f'预计{days}天内销量将保持稳定，波动约±5%'
            confidence = '高' if len(sales_data) > 14 else '中高'
        elif growth_rate > -20:
            trend = 'moderate_decrease'
            message = f'预计{days}天内销量将缓慢下降，降幅约{abs(round(growth_rate, 1))}%'
            confidence = '中高' if len(sales_data) > 14 else '中'
        else:
            trend = 'sharp_decrease'
            message = f'预计{days}天内销量将明显下降，降幅约{abs(round(growth_rate, 1))}%'
            confidence = '中' if len(sales_data) > 14 else '低'
        
        # 预估未来总销量
        lifecycle_stage = self.analyze_product_lifecycle(product_name).get('stage', '引入期')
        stage_adjustment = {
            '引入期': 1.2,  # 引入期可能有更快增长
            '成长期': 1.1,  # 成长期继续增长但增速放缓
            '成熟期': 1.0,  # 成熟期保持稳定
            '饱和期': 0.9,  # 饱和期小幅下降
            '衰退期': 0.7   # 衰退期明显下降
        }
        
        # 应用生命周期阶段调整系数
        adjusted_growth_rate = growth_rate * stage_adjustment.get(lifecycle_stage, 1.0)
        estimated_future_sales = avg_daily_sales * days * (1 + adjusted_growth_rate / 100)
        
        return {
            'forecast': trend,
            'message': message,
            'estimated_growth': round(adjusted_growth_rate, 1),
            'confidence': confidence,
            'estimated_sales_next_period': max(0, round(estimated_future_sales)),
            'avg_daily_sales': round(avg_daily_sales, 1),
            'based_on_days': len(sales_data)
        } 