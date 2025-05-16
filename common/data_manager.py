#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一数据管理模块 - 负责数据读取、存储和路径管理
"""

import os
import sys
import yaml
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

class DataManager:
    """统一数据管理器，提供一致的数据访问接口"""
    
    def __init__(self, data_dir=None):
        # 设置默认数据目录
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../data')
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 创建核心子目录
        self.subdirs = [
            'database',  # 数据库文件
            'config',    # 配置文件
            'logs',      # 日志文件
            'exports',   # 导出文件
            'cache',     # 缓存文件
            'analytics', # 分析结果
            'products',  # 产品数据
            'users',     # 用户数据
            'sessions',  # 会话数据
            'uploads',   # 上传文件
            'temp'       # 临时文件
        ]
        
        # 创建所有子目录
        for subdir in self.subdirs:
            subdir_path = os.path.join(self.data_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            print(f"创建子目录: {subdir_path}")
        
        print(f"数据管理器已初始化，数据目录: {self.data_dir}")
    
    def get_path(self, *parts):
        """获取数据目录中的路径
        
        Args:
            *parts: 路径组成部分，如 'logs', 'app.log'
            
        Returns:
            str: 完整的文件路径
        """
        return os.path.join(self.data_dir, *parts)
    
    def file_exists(self, *parts):
        """检查文件是否存在
        
        Args:
            *parts: 路径组成部分，如 'logs', 'app.log'
            
        Returns:
            bool: 文件是否存在
        """
        filepath = self.get_path(*parts)
        return os.path.isfile(filepath)
    
    def dir_exists(self, *parts):
        """检查目录是否存在
        
        Args:
            *parts: 路径组成部分，如 'logs', 'app_logs'
            
        Returns:
            bool: 目录是否存在
        """
        dirpath = self.get_path(*parts)
        return os.path.isdir(dirpath)
    
    def create_directory(self, *parts):
        """创建目录
        
        Args:
            *parts: 路径组成部分，如 'logs', 'app_logs'
            
        Returns:
            str: 创建的目录路径
        """
        dirpath = self.get_path(*parts)
        os.makedirs(dirpath, exist_ok=True)
        return dirpath
    
    def load_yaml(self, *parts):
        """加载YAML文件
        
        Args:
            *parts: 路径组成部分，如 'config', 'app_config.yaml'
            
        Returns:
            dict: YAML内容，如果文件不存在或加载出错则返回空字典
        """
        filepath = self.get_path(*parts)
        if not os.path.isfile(filepath):
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"加载YAML文件出错: {filepath}, {str(e)}")
            return {}
    
    def save_yaml(self, data, *parts):
        """保存YAML文件
        
        Args:
            data: 要保存的数据
            *parts: 路径组成部分，如 'config', 'app_config.yaml'
            
        Returns:
            bool: 是否成功保存
        """
        filepath = self.get_path(*parts)
        
        # 确保父目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"保存YAML文件出错: {filepath}, {str(e)}")
            return False
    
    def load_json(self, *parts):
        """加载JSON文件
        
        Args:
            *parts: 路径组成部分，如 'analytics', 'user_stats.json'
            
        Returns:
            dict: JSON内容，如果文件不存在或加载出错则返回空字典
        """
        filepath = self.get_path(*parts)
        if not os.path.isfile(filepath):
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f) or {}
        except Exception as e:
            print(f"加载JSON文件出错: {filepath}, {str(e)}")
            return {}
    
    def save_json(self, data, *parts):
        """保存JSON文件
        
        Args:
            data: 要保存的数据
            *parts: 路径组成部分，如 'analytics', 'user_stats.json'
            
        Returns:
            bool: 是否成功保存
        """
        filepath = self.get_path(*parts)
        
        # 确保父目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存JSON文件出错: {filepath}, {str(e)}")
            return False
    
    def list_files(self, *parts, pattern=None):
        """列出目录中的文件
        
        Args:
            *parts: 路径组成部分，如 'logs'
            pattern: 可选的文件名匹配模式，如 '*.log'
            
        Returns:
            list: 文件路径列表
        """
        import glob
        
        dirpath = self.get_path(*parts)
        if not os.path.isdir(dirpath):
            return []
        
        if pattern:
            return glob.glob(os.path.join(dirpath, pattern))
        else:
            return [os.path.join(dirpath, f) for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
    
    def delete_file(self, *parts):
        """删除文件
        
        Args:
            *parts: 路径组成部分，如 'temp', 'temp_file.txt'
            
        Returns:
            bool: 是否成功删除
        """
        filepath = self.get_path(*parts)
        if not os.path.isfile(filepath):
            return False
        
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"删除文件出错: {filepath}, {str(e)}")
            return False
    
    def clear_directory(self, *parts):
        """清空目录内容
        
        Args:
            *parts: 路径组成部分，如 'temp'
            
        Returns:
            bool: 是否成功清空
        """
        dirpath = self.get_path(*parts)
        if not os.path.isdir(dirpath):
            return False
        
        try:
            for item in os.listdir(dirpath):
                item_path = os.path.join(dirpath, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            return True
        except Exception as e:
            print(f"清空目录出错: {dirpath}, {str(e)}")
            return False

def setup_logger(name, level=logging.INFO, log_file=None, console=True):
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        console: 是否输出到控制台
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有的处理器
    logger.handlers = []
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # 添加控制台处理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建全局数据管理器实例
data_manager = DataManager()

# 导出便捷函数以方便直接调用
get_path = data_manager.get_path
list_files = data_manager.list_files
load_yaml = data_manager.load_yaml
save_yaml = data_manager.save_yaml
load_json = data_manager.load_json
save_json = data_manager.save_json 