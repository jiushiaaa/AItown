#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据管理器使用示例

此文件演示了如何在项目中正确使用统一数据存储方案。
"""

import os
import json
import time
from datetime import datetime
from common.data_manager import (
    data_manager,
    get_path, 
    get_db_path, 
    get_db_connection,
    load_json, 
    save_json, 
    load_yaml, 
    save_yaml
)

def demo_path_operations():
    """演示路径操作"""
    print("\n=== 路径操作演示 ===")
    
    # 获取各类数据的标准路径
    db_path = get_path('db', 'app_data.db')
    config_path = get_path('config', 'server_settings.yaml')
    log_path = get_path('logs', f"{datetime.now().strftime('%Y-%m-%d')}.log")
    product_img_path = get_path('products', 'images', 'green_tea.jpg')
    
    print(f"数据库路径: {db_path}")
    print(f"配置文件路径: {config_path}")
    print(f"日志文件路径: {log_path}")
    print(f"产品图片路径: {product_img_path}")
    
    # 检查目录是否存在
    product_dir_exists = data_manager.dir_exists('products', 'images')
    print(f"产品图片目录是否存在: {product_dir_exists}")
    
    # 创建目录
    if not product_dir_exists:
        data_manager.create_directory('products', 'images')
        print("已创建产品图片目录")

def demo_json_operations():
    """演示JSON数据操作"""
    print("\n=== JSON操作演示 ===")
    
    # 示例产品数据
    product_data = {
        "productId": "tea-001",
        "name": "西湖龙井",
        "price": 188.00,
        "description": "产自杭州西湖龙井村的明前龙井茶",
        "categories": ["绿茶", "明前茶"],
        "created_at": datetime.now().isoformat()
    }
    
    # 保存JSON数据
    product_path = 'products/tea/green_tea.json'
    success = save_json(product_data, 'products', 'tea/green_tea.json')
    print(f"保存产品数据: {'成功' if success else '失败'}")
    
    # 加载JSON数据
    loaded_data = load_json('products', 'tea/green_tea.json')
    print(f"加载的产品名称: {loaded_data.get('name')}")
    print(f"加载的产品价格: {loaded_data.get('price')}")
    
    # 修改并保存(带备份)
    loaded_data['price'] = 198.00
    loaded_data['updated_at'] = datetime.now().isoformat()
    success = save_json(loaded_data, 'products', 'tea/green_tea.json', backup=True)
    print(f"更新产品数据(带备份): {'成功' if success else '失败'}")
    
    # 检查文件是否存在
    file_exists = data_manager.file_exists('products', 'tea/green_tea.json')
    print(f"产品文件是否存在: {file_exists}")

def demo_yaml_operations():
    """演示YAML数据操作"""
    print("\n=== YAML操作演示 ===")
    
    # 示例配置数据
    server_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8765,
            "workers": 4,
            "timeout": 30
        },
        "websocket": {
            "ping_interval": 30,
            "ping_timeout": 10,
            "max_message_size": 1048576
        },
        "logging": {
            "level": "info",
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "file": "server.log"
        }
    }
    
    # 保存YAML配置
    success = save_yaml(server_config, 'config', 'server_settings.yaml')
    print(f"保存服务器配置: {'成功' if success else '失败'}")
    
    # 加载YAML配置
    loaded_config = load_yaml('config', 'server_settings.yaml')
    print(f"加载的服务器端口: {loaded_config.get('server', {}).get('port')}")
    print(f"加载的日志级别: {loaded_config.get('logging', {}).get('level')}")
    
    # 修改并保存配置(带备份)
    loaded_config['server']['port'] = 8766
    loaded_config['logging']['level'] = 'debug'
    success = save_yaml(loaded_config, 'config', 'server_settings.yaml', backup=True)
    print(f"更新服务器配置(带备份): {'成功' if success else '失败'}")

def demo_database_operations():
    """演示数据库操作"""
    print("\n=== 数据库操作演示 ===")
    
    # 获取数据库连接
    db_name = 'demo.db'
    conn = get_db_connection(db_name)
    print(f"获取数据库连接: {db_name}")
    
    # 创建表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    print("创建products表")
    
    # 插入数据
    conn.execute(
        "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?)",
        ('tea-001', '西湖龙井', 188.0, '明前龙井茶', datetime.now().isoformat())
    )
    conn.execute(
        "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?)",
        ('tea-002', '碧螺春', 168.0, '产自江苏苏州', datetime.now().isoformat())
    )
    conn.commit()
    print("插入示例数据")
    
    # 查询数据
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    print(f"查询到 {len(products)} 个产品:")
    for product in products:
        print(f"  - {product['id']}: {product['name']} (¥{product['price']})")

def demo_backup_operations():
    """演示备份和临时文件操作"""
    print("\n=== 备份操作演示 ===")
    
    # 创建一些临时文件
    for i in range(3):
        with open(data_manager.get_path('temp', f'temp_file_{i}.txt'), 'w') as f:
            f.write(f"这是临时文件 {i}，创建于 {datetime.now().isoformat()}")
        print(f"创建临时文件: temp_file_{i}.txt")
    
    # 列出临时文件
    temp_files = data_manager.list_files('temp', pattern='*.txt')
    print(f"临时目录中的文件: {temp_files}")
    
    # 清理临时文件(这里设置为0天以便演示)
    time.sleep(1)  # 确保文件有修改时间差异
    deleted_count = data_manager.cleanup_temp_files(days_old=0)
    print(f"清理了 {deleted_count} 个临时文件")
    
    # 验证清理结果
    temp_files = data_manager.list_files('temp', pattern='*.txt')
    print(f"清理后临时目录中的文件: {temp_files}")
    
    # 删除文件(带备份)
    product_path = 'tea/green_tea.json'
    if data_manager.file_exists('products', product_path):
        success = data_manager.delete_file('products', product_path, backup=True)
        print(f"删除产品文件(带备份): {'成功' if success else '失败'}")
        
        # 检查备份目录
        backup_files = data_manager.list_files('temp', 'backups/products', pattern='*.bak', recursive=True)
        print(f"备份目录中的文件: {backup_files}")

def main():
    """主函数，运行所有演示"""
    print("=== 统一数据存储方案演示 ===")
    print(f"数据根目录: {data_manager.data_dir}")
    
    # 运行各种演示
    demo_path_operations()
    demo_json_operations()
    demo_yaml_operations()
    demo_database_operations()
    demo_backup_operations()
    
    # 关闭数据库连接
    data_manager.close_db_connections()
    print("\n演示完成!")

if __name__ == "__main__":
    main()