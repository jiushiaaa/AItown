#coding=utf-8
"""
数据处理模块 - 用于处理、验证和修复JSON数据
已重构为模块化结构，实际实现请参考 data_processor/ 目录
"""

from .data_processor.utils import (
    string_to_dict,
    percentage_to_number,
    to_number,
    check_completed,
    clean_emoji_field
)

from .data_processor.customer import (
    generate_default_customer_interactions,
    add_consumer_details
)

from .data_processor.stats import (
    generate_default_daily_stats,
    generate_default_cumulative_stats,
    recalculate_daily_stats
)

from .data_processor.validator import (
    verify_and_fix_json,
    generate_default_data
)

__all__ = [
    'string_to_dict',
    'percentage_to_number',
    'to_number',
    'check_completed',
    'clean_emoji_field',
    'generate_default_customer_interactions',
    'add_consumer_details',
    'generate_default_daily_stats',
    'generate_default_cumulative_stats',
    'recalculate_daily_stats',
    'verify_and_fix_json',
    'generate_default_data'
] 