#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置模块
统一管理项目的日志输出
"""

import logging
import os
from datetime import datetime


class LoggerConfig:
    """日志配置类"""
    
    def __init__(self, name="deepseek_client"):
        self.name = name
        self.logs_dir = "logs"
        self.setup_logs_directory()
        self.logger = self.setup_logger()
    
    def setup_logs_directory(self):
        """创建logs目录"""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
    
    def setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger(self.name)
        
        # 避免重复添加handler
        if logger.handlers:
            return logger
            
        logger.setLevel(logging.INFO)
        
        # 创建格式化器（包含行号信息）
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s:%(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器（包含所有日志级别）
        log_filename = f"{self.logs_dir}/deepseek_client_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self):
        """获取日志记录器"""
        return self.logger
    
    def get_logs_dir(self):
        """获取日志目录路径"""
        return self.logs_dir


# 全局日志实例
_logger_config = LoggerConfig()
logger = _logger_config.get_logger()
logs_dir = _logger_config.get_logs_dir()


def get_screenshot_path(filename):
    """获取截图文件的完整路径"""
    if not filename.endswith('.png'):
        filename += '.png'
    return os.path.join(logs_dir, filename)