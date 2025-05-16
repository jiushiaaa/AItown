#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库清理脚本
用于清空数据库内容并重置表结构
"""

import os
import sys
import sqlite3

# 添加上级目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """主函数，清空数据库并重置表结构"""
    print("=== 开始清理数据库 ===")
    
    # 获取数据库路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'simulation_data.db')
    
    print(f"数据库路径: {db_path}")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 列出所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 清空表
        for table in tables:
            if table[0] != 'sqlite_sequence':  # 不清空sqlite内部表
                cursor.execute(f"DELETE FROM {table[0]}")
                print(f"已清空表 {table[0]}")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence")
        print("已重置自增ID")
        
        # 提交更改
        conn.commit()
        print("数据库清理完成")
        
        # 验证清理结果
        for table in tables:
            if table[0] != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"表 {table[0]} 现有记录数: {count}")
        
    except Exception as e:
        print(f"清理数据库时出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    
    print("=== 数据库清理完成 ===")
    print("现在可以运行 test_data_save.py 重新导入数据")

if __name__ == "__main__":
    main() 