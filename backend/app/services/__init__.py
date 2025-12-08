# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Service layer"""

from .task_manager import task_manager
from .crawler_service import CrawlerService
from .result_service import ResultService
from .statistics_service import StatisticsService

__all__ = [
    "task_manager",
    "CrawlerService",
    "ResultService",
    "StatisticsService",
]
