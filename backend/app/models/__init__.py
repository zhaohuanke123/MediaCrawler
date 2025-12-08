# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""Database models"""

from .task import Task
from .result import Result
from .statistics import Statistics

__all__ = ["Task", "Result", "Statistics"]
