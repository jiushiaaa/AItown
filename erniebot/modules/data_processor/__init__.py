"""
数据处理模块 - 用于处理、验证和修复JSON数据
"""

from .utils import (
    string_to_dict,
    percentage_to_number,
    to_number,
    check_completed,
    clean_emoji_field
)

from .customer import (
    generate_default_customer_interactions,
    add_consumer_details
)

from .stats import (
    generate_default_daily_stats,
    generate_default_cumulative_stats,
    recalculate_daily_stats
)

from .validator import (
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