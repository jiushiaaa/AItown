#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_api配置模块 - 提供基本配置值
"""

import os
import sys
from pathlib import Path
from flask_cors import CORS
import dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

# 基本配置值
HOST = os.environ.get("DATA_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("DATA_API_PORT", "5000"))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

def get_db_path():
    """获取数据库文件路径"""
    db_filename = os.environ.get("DB_PATH", "simulation_data.db")
    
    # 数据库文件通常位于 erniebot 模块目录下
    project_root = Path(__file__).parent.parent
    erniebot_dir = project_root / "erniebot"
    db_path = erniebot_dir / db_filename
    
    # 如果 erniebot 目录下的路径不存在，尝试项目根目录 (作为后备)
    if not db_path.exists():
        db_path_root = project_root / db_filename
        if db_path_root.exists():
             print(f"警告: 数据库文件在erniebot目录未找到，使用根目录下的 {db_filename}")
             return str(db_path_root)
        else:
             # 如果根目录也没有，则返回erniebot目录下的预期路径，让后续代码处理不存在的情况
             print(f"警告: 数据库文件 {db_path} 不存在")
             return str(db_path)
    
    return str(db_path)

# 设置数据库路径
DB_PATH = get_db_path()

def configure_app(app):
    """配置Flask应用"""
    # 配置CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # 返回配置，以便设置Flask运行参数
    return {
        "host": HOST,
        "port": PORT,
        "debug": DEBUG
    }

# 打印配置信息
print(f"Data API 配置加载完成. 服务运行在 {HOST}:{PORT}")
print(f"数据库路径: {DB_PATH}")