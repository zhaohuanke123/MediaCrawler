# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.

"""
Event loop policy fix for Windows compatibility with Playwright.

This module provides a utility to fix asyncio event loop issues on Windows
when using Playwright, which requires subprocess support.
"""

import asyncio
import platform


def setup_event_loop_policy():
    """
    Setup the appropriate event loop policy for the current platform.
    
    On Windows, sets WindowsSelectorEventLoopPolicy to support subprocess
    operations required by Playwright. This must be called before any
    asyncio operations or event loop creation.
    
    This is required because Windows' default ProactorEventLoop doesn't
    support subprocess creation, which causes NotImplementedError when
    Playwright tries to launch browser processes.
    """
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Auto-apply fix when this module is imported
setup_event_loop_policy()
