# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Real crawler service for integrating root directory crawler implementations"""

import sys
import asyncio
import logging
import platform
from pathlib import Path
from typing import Optional, Dict, Callable
from datetime import datetime
from contextvars import ContextVar

# Fix for Windows: Set WindowsSelectorEventLoopPolicy to support subprocess
# This is required for Playwright to work on Windows
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add project root to sys.path to allow imports from root crawler modules
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from base.base_crawler import AbstractCrawler
from media_platform.bilibili import BilibiliCrawler
from media_platform.douyin import DouYinCrawler
from media_platform.kuaishou import KuaishouCrawler
from media_platform.tieba import TieBaCrawler
from media_platform.weibo import WeiboCrawler
from media_platform.xhs import XiaoHongShuCrawler
from media_platform.zhihu import ZhihuCrawler
from var import crawler_type_var, source_keyword_var

logger = logging.getLogger(__name__)


class RealCrawlerService:
    """Service for running real crawler implementations from root directory"""
    
    # Platform mapping: frontend platform name -> crawler short name
    PLATFORM_MAP = {
        "xhs": "xhs",
        "douyin": "dy",
        "kuaishou": "ks",
        "bilibili": "bili",
        "weibo": "wb",
        "tieba": "tieba",
        "zhihu": "zhihu"
    }
    
    # Crawler class mapping
    CRAWLER_CLASSES = {
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        "bili": BilibiliCrawler,
        "wb": WeiboCrawler,
        "tieba": TieBaCrawler,
        "zhihu": ZhihuCrawler,
    }
    
    @staticmethod
    def prepare_config(platform: str, crawler_type: str, config_dict: dict) -> dict:
        """
        准备爬虫配置，将前端配置转换为爬虫所需格式
        
        Args:
            platform: 平台名称
            crawler_type: 爬虫类型 (search, detail, creator)
            config_dict: 前端传递的配置字典
            
        Returns:
            转换后的配置字典
        """
        # Import root config module (from project root)
        import config as root_config
        config = root_config
        
        # 设置基础配置
        crawler_short_name = RealCrawlerService.PLATFORM_MAP.get(platform, platform)
        config.PLATFORM = crawler_short_name
        config.CRAWLER_TYPE = crawler_type
        
        # 从前端配置中提取关键词
        keyword = config_dict.get('keyword', '')
        if keyword:
            config.KEYWORDS = keyword
            # 设置上下文变量
            source_keyword_var.set(keyword)
        
        # 设置页数
        pages = config_dict.get('pages', 10)
        if hasattr(config, 'CRAWLER_MAX_NOTES_COUNT'):
            config.CRAWLER_MAX_NOTES_COUNT = pages
        
        # 设置排序方式（如果支持）
        sort = config_dict.get('sort', 'latest')
        if hasattr(config, 'SEARCH_SORT_TYPE'):
            config.SEARCH_SORT_TYPE = sort
        
        # 设置爬虫类型上下文变量
        crawler_type_var.set(crawler_type)
        
        # 设置为无头模式（后台运行）
        config.HEADLESS = True
        
        # 禁用CDP模式以避免浏览器启动问题
        config.ENABLE_CDP_MODE = False
        
        # 设置数据保存选项为数据库模式
        config.SAVE_DATA_OPTION = "db"
        
        # 禁用IP代理（可根据需要启用）
        config.ENABLE_IP_PROXY = False
        
        # 设置登录类型
        config.LOGIN_TYPE = "cookie"  # 使用cookie登录避免二维码
        
        logger.info(f"[RealCrawlerService] 配置已准备: platform={crawler_short_name}, "
                   f"type={crawler_type}, keyword={keyword}, pages={pages}")
        
        return {
            'platform': crawler_short_name,
            'crawler_type': crawler_type,
            'keyword': keyword,
            'pages': pages,
            'sort': sort
        }
    
    @staticmethod
    async def run_crawler(
        platform: str,
        crawler_type: str,
        config_dict: dict,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> dict:
        """
        运行真实的爬虫
        
        Args:
            platform: 平台名称
            crawler_type: 爬虫类型
            config_dict: 配置字典
            progress_callback: 进度回调函数 callback(progress, items_collected)
            
        Returns:
            执行结果字典
        """
        logger.info(f"[RealCrawlerService] 开始运行爬虫: platform={platform}, type={crawler_type}")
        
        # 准备配置
        prepared_config = RealCrawlerService.prepare_config(platform, crawler_type, config_dict)
        
        # 获取爬虫类
        crawler_short_name = RealCrawlerService.PLATFORM_MAP.get(platform, platform)
        crawler_class = RealCrawlerService.CRAWLER_CLASSES.get(crawler_short_name)
        
        if not crawler_class:
            raise ValueError(f"不支持的平台: {platform}")
        
        items_collected = 0
        
        try:
            # 创建爬虫实例
            crawler: AbstractCrawler = crawler_class()
            
            logger.info(f"[RealCrawlerService] 爬虫实例已创建: {crawler_class.__name__}")
            
            # 报告开始进度
            if progress_callback:
                await progress_callback(5, 0)
            
            # 启动爬虫
            # 注意：crawler.start() 会执行整个爬取流程
            await crawler.start()
            
            logger.info(f"[RealCrawlerService] 爬虫执行完成")
            
            # 报告完成进度
            if progress_callback:
                await progress_callback(100, items_collected)
            
            return {
                'success': True,
                'items_collected': items_collected,
                'platform': platform,
                'crawler_type': crawler_type
            }
            
        except Exception as e:
            logger.error(f"[RealCrawlerService] 爬虫执行失败: {e}", exc_info=True)
            raise
    
    @staticmethod
    def is_available() -> bool:
        """
        检查真实爬虫是否可用
        
        Returns:
            True if available, False otherwise
        """
        try:
            # 尝试导入必要的模块
            from base.base_crawler import AbstractCrawler
            return True
        except ImportError as e:
            logger.warning(f"[RealCrawlerService] 真实爬虫不可用: {e}")
            return False


class CrawlerProgressTracker:
    """爬虫进度跟踪器"""
    
    def __init__(self, total_items: int = 100):
        self.total_items = total_items
        self.current_items = 0
        self.progress = 0
    
    def update(self, items: int):
        """更新收集的项目数"""
        self.current_items += items
        self.progress = min(int((self.current_items / self.total_items) * 100), 100)
    
    def get_progress(self) -> tuple:
        """获取当前进度"""
        return self.progress, self.current_items
