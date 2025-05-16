#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一配置加载模块 - 适用于erniebot和data_api项目
"""

import os
import yaml
import json
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 初始化配置字典
        self.config = {}
        self._initialized = True
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件和环境变量"""
        # 确定配置文件路径
        # base_dir = Path(__file__).parent.absolute() # Original line
        # config_file = base_dir / "config.yaml" # Original line
        # Corrected path: Go up one level from common, then into config
        config_file = Path(__file__).parent.parent / "config" / "config.yaml"

        # 加载YAML配置
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"配置文件加载成功: {config_file}")
        except Exception as e:
            print(f"无法加载配置文件: {e}")
            # 使用默认配置
            self.config = self._get_default_config()

        # 加载环境变量
        self._load_env_vars()
    
    def _load_env_vars(self):
        """从环境变量加载配置，覆盖默认值"""
        # 加载.env文件中的环境变量(如果存在)
        env_file = Path(__file__).parent.absolute() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # 映射环境变量到配置
        env_mapping = {
            # erniebot配置
            "ERNIEBOT_HOST": ["services", "erniebot", "host"],
            "ERNIEBOT_PORT": ["services", "erniebot", "port"],
            "AI_API_KEY": ["services", "erniebot", "model", "api_key"],
            "AI_MODEL_NAME": ["services", "erniebot", "model", "model_name"],
            "DB_PATH": ["services", "erniebot", "database", "path"],
            
            # data_api配置
            "DATA_API_HOST": ["services", "data_api", "host"],
            "DATA_API_PORT": ["services", "data_api", "port"],
            
            # 通用配置
            "LOG_LEVEL": ["common", "log_level"],
            "DEBUG": ["services", "erniebot", "debug"],
            
            # dashboard配置
            "DASHBOARD_API_URL": ["services", "dashboard", "api_base_url"],
        }
        
        # 用环境变量更新配置
        for env_var, config_path in env_mapping.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # 转换环境变量值到适当的类型
                if env_value.lower() in ["true", "false"]:
                    # 布尔值处理
                    env_value = env_value.lower() == "true"
                elif env_value.isdigit():
                    # 整数处理
                    env_value = int(env_value)
                elif env_value.replace(".", "", 1).isdigit() and env_value.count(".") == 1:
                    # 浮点数处理
                    env_value = float(env_value)
                
                # 更新配置
                self._set_config_value(config_path, env_value)
    
    def _set_config_value(self, path_list, value):
        """递归设置配置字典中的值"""
        config = self.config
        for i, key in enumerate(path_list):
            if i == len(path_list) - 1:
                config[key] = value
            else:
                if key not in config:
                    config[key] = {}
                config = config[key]
    
    def _get_default_config(self):
        """返回默认配置"""
        return {
            "services": {
                "erniebot": {
                    "host": "127.0.0.1",
                    "port": 12339,
                    "debug": False,
                    "model": {
                        "api_key": "",
                        "model_name": "ernie-4.0-turbo-128k",
                        "temperature": 0.7
                    },
                    "database": {
                        "path": "simulation_data.db"
                    }
                },
                "data_api": {
                    "host": "127.0.0.1",
                    "port": 5000,
                    "debug": False,
                    "cors": {
                        "origins": ["*"]
                    }
                },
                "dashboard": {
                    "api_base_url": "http://127.0.0.1:5000",
                    "auto_refresh": True,
                    "refresh_interval": 30000
                },
                "unity": {
                    "socket_server": {
                        "host": "127.0.0.1",
                        "port": 12339
                    },
                    "settings": {
                        "animation_speed": 1.0,
                        "debug_mode": False
                    }
                }
            },
            "common": {
                "log_level": "info",
                "data_dir": "../data"
            }
        }
    
    def get(self, *args, default=None):
        """获取配置值，支持深层次访问，例如:
        config.get('services', 'erniebot', 'host')
        """
        value = self.config
        for arg in args:
            if isinstance(value, dict) and arg in value:
                value = value[arg]
            else:
                return default
        return value
    
    def to_dict(self):
        """返回完整配置字典"""
        return self.config
    
    def get_service_config(self, service_name):
        """获取特定服务的配置"""
        return self.get('services', service_name, default={})
    
    def __str__(self):
        """打印友好的配置信息"""
        return json.dumps(self.config, indent=2, ensure_ascii=False)


# 导出配置管理器单例
config = ConfigManager()

if __name__ == "__main__":
    # 测试配置加载
    print("配置加载测试:")
    print("erniebot host:", config.get('services', 'erniebot', 'host'))
    print("erniebot port:", config.get('services', 'erniebot', 'port'))
    print("data_api host:", config.get('services', 'data_api', 'host'))
    print("log level:", config.get('common', 'log_level'))
    print("\n完整配置:")
    print(config)