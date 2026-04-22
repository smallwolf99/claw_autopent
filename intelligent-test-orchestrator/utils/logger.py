#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志模块

提供统一的日志配置和格式化管理，避免各模块重复配置。

使用方式:
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（终端友好）"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    设置并返回 logger
    
    Args:
        name: logger 名称（通常使用 __name__）
        level: 日志级别（默认 INFO）
        log_file: 日志文件路径（可选，如果提供则同时写入文件）
        use_colors: 是否使用颜色输出（默认 True）
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，直接返回（避免重复配置）
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 创建格式化器
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    if use_colors:
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取已存在的 logger（不创建新的）
    
    Args:
        name: logger 名称
    
    Returns:
        Logger 对象（如果不存在则返回 None）
    """
    return logging.getLogger(name)


def set_global_level(level: int):
    """
    设置全局日志级别
    
    Args:
        level: 日志级别（logging.DEBUG/INFO/WARNING/ERROR/CRITICAL）
    """
    logging.getLogger().setLevel(level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)


# 便捷的日志级别常量
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
