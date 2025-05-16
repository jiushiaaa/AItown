#coding=utf-8
"""
销售分析模块 - 用于跟踪和分析销售数据
"""

# 从新的包结构中导入
from .sales_analytics.sales_tracker import SalesTracker
from .sales_analytics.product_metrics import ProductMetricsAnalyzer
from .sales_analytics.product_lifecycle import ProductLifecycleAnalyzer
from .sales_analytics.consumer_analysis import ConsumerAnalyzer
from .sales_analytics.price_analysis import PriceAnalyzer
from .sales_analytics.product_association import ProductAssociationAnalyzer
from .sales_analytics.seasonal_analysis import SeasonalAnalyzer
from .sales_analytics.loyalty_program import LoyaltyProgramAnalyzer
from .sales_analytics.report_generator import ReportGenerator

# 向后兼容，保留原始类名称
__all__ = ['SalesTracker'] 