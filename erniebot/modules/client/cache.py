#coding=utf-8
"""
缓存模块 - 提供LRU缓存实现
"""

import time
from collections import OrderedDict

class LRUCache:
    """LRU缓存实现，用于缓存API请求结果"""
    
    def __init__(self, capacity=100):
        """初始化LRU缓存
        
        Args:
            capacity (int): 缓存容量
        """
        self.cache = OrderedDict()
        self.capacity = capacity
        self.expiry = {}  # 存储缓存项的过期时间
    
    def get(self, key):
        """获取缓存项
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        if key not in self.cache:
            return None
            
        # 检查是否过期
        if key in self.expiry and time.time() > self.expiry[key]:
            self.cache.pop(key)
            self.expiry.pop(key)
            return None
            
        # 将访问的项移到末尾（最近使用）
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value, ttl=3600):
        """添加缓存项
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        # 如果键已存在，更新值并移到末尾
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # 如果缓存已满，删除最早使用的项
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
                
            # 添加新项
            self.cache[key] = value
        
        # 设置过期时间
        if ttl > 0:
            self.expiry[key] = time.time() + ttl
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.expiry.clear() 