#coding=utf-8
"""
正山堂茶业定价辅助工具 - 用于管理产品定价与成本计算
"""

import os
import yaml
import argparse

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")

def load_yaml_config(filename):
    """加载YAML配置文件"""
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        print(f"警告: 配置文件 {filepath} 不存在!")
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml_config(data, filename):
    """保存YAML配置文件"""
    filepath = os.path.join(CONFIG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, indent=2, default_flow_style=False)
    print(f"配置已保存到: {filepath}")

def calculate_cost_from_price(min_price, max_price, cost_ratio=0.4, method="min"):
    """
    根据价格范围计算成本
    
    参数:
    - min_price: 最低销售价格
    - max_price: 最高销售价格
    - cost_ratio: 成本比例，默认为0.4（即成本为价格的40%）
    - method: 计算方法，可选值：
      - "min": 使用最低价格计算 (默认)
      - "avg": 使用平均价格计算
      - "max": 使用最高价格计算
    
    返回:
    - 计算得出的成本
    """
    if method == "min":
        return int(min_price * cost_ratio)
    elif method == "avg":
        avg_price = (min_price + max_price) / 2
        return int(avg_price * cost_ratio)
    elif method == "max":
        return int(max_price * cost_ratio)
    else:
        raise ValueError(f"不支持的计算方法: {method}")

def generate_costs_from_pricing(cost_ratio=0.4, method="min", initial_stock=200):
    """
    从产品定价配置生成产品成本配置
    
    参数:
    - cost_ratio: 成本比例，默认为0.4
    - method: 成本计算方法，默认为"min"
    - initial_stock: 默认初始库存量
    
    返回:
    - 生成的产品成本配置
    """
    pricing_config = load_yaml_config("product_pricing.yaml")
    cost_config = {}
    
    # 加载现有成本配置（如果存在）
    existing_costs = load_yaml_config("product_costs.yaml")
    
    for product_name, product_data in pricing_config.items():
        if 'price_range' in product_data:
            min_price, max_price = product_data['price_range']
            
            # 计算成本
            cost = calculate_cost_from_price(min_price, max_price, cost_ratio, method)
            
            # 获取现有库存数据，如果没有则使用默认值
            if product_name in existing_costs:
                stock = existing_costs[product_name].get('initial_stock', initial_stock)
            else:
                # 根据产品类别调整默认库存
                category = product_data.get('category', '').lower()
                if '高端' in category or '收藏' in category:
                    stock = 50  # 高端产品库存较少
                elif '礼盒' in category:
                    stock = 150  # 礼盒类中等库存
                elif '入门' in category or '促销' in category:
                    stock = 400  # 入门级和促销产品库存较多
                else:
                    stock = initial_stock
            
            # 创建产品成本配置
            cost_config[product_name] = {
                'cost': cost,
                'initial_stock': stock
            }
    
    return cost_config

def update_costs_file(cost_ratio=0.4, method="min"):
    """更新产品成本配置文件"""
    cost_config = generate_costs_from_pricing(cost_ratio, method)
    
    # 保存到成本配置文件
    save_yaml_config(cost_config, "product_costs.yaml")
    print(f"已使用 {method} 方法和 {cost_ratio*100}% 成本比例更新产品成本")

def add_new_product(name, min_price, max_price, category, description="", cost_ratio=0.4, stock=200):
    """
    添加新产品到定价和成本配置
    
    参数:
    - name: 产品名称
    - min_price: 最低价格
    - max_price: 最高价格
    - category: 产品类别
    - description: 产品描述
    - cost_ratio: 成本比例
    - stock: 初始库存
    """
    # 加载当前配置
    pricing_config = load_yaml_config("product_pricing.yaml")
    cost_config = load_yaml_config("product_costs.yaml")
    
    # 添加到定价配置
    pricing_config[name] = {
        'price_range': [min_price, max_price],
        'category': category,
        'description': description
    }
    
    # 计算成本并添加到成本配置
    cost = calculate_cost_from_price(min_price, max_price, cost_ratio)
    cost_config[name] = {
        'cost': cost,
        'initial_stock': stock
    }
    
    # 保存配置
    save_yaml_config(pricing_config, "product_pricing.yaml")
    save_yaml_config(cost_config, "product_costs.yaml")
    
    print(f"已添加新产品: {name}")
    print(f"价格范围: {min_price}-{max_price}元, 成本: {cost}元, 初始库存: {stock}")

def main():
    parser = argparse.ArgumentParser(description="正山堂茶业定价与成本管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 更新成本命令
    update_parser = subparsers.add_parser("update", help="从定价配置更新成本配置")
    update_parser.add_argument("--ratio", type=float, default=0.4, help="成本比例(默认: 0.4)")
    update_parser.add_argument("--method", choices=["min", "avg", "max"], default="min", 
                              help="成本计算方法 (min/avg/max, 默认: min)")
    
    # 添加产品命令
    add_parser = subparsers.add_parser("add", help="添加新产品")
    add_parser.add_argument("name", help="产品名称")
    add_parser.add_argument("min_price", type=int, help="最低价格")
    add_parser.add_argument("max_price", type=int, help="最高价格")
    add_parser.add_argument("category", help="产品类别")
    add_parser.add_argument("--description", default="", help="产品描述")
    add_parser.add_argument("--ratio", type=float, default=0.4, help="成本比例(默认: 0.4)")
    add_parser.add_argument("--stock", type=int, default=200, help="初始库存(默认: 200)")
    
    args = parser.parse_args()
    
    if args.command == "update":
        update_costs_file(args.ratio, args.method)
    elif args.command == "add":
        add_new_product(
            args.name, 
            args.min_price, 
            args.max_price, 
            args.category, 
            args.description, 
            args.ratio, 
            args.stock
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 