# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/bilibili/bilibilli_store_media.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# -*- coding: utf-8 -*-
# @Author  : helloteemo
# @Time    : 2024/7/12 20:01
# @Desc    : bilibili 媒体保存
import pathlib
from typing import Dict

import aiofiles

from base.base_crawler import AbstractStoreImage, AbstractStoreVideo
from tools import utils


class BilibiliVideo(AbstractStoreVideo):
    video_store_path: str = "data/bili/videos"

    async def store_video(self, video_content_item: Dict):
        """
        store content

        Args:
            video_content_item:

        Returns:

        """
        # Prefer using bvid if available, otherwise fallback to aid
        folder_name = video_content_item.get("bvid") or video_content_item.get("aid")
        
        await self.save_video(
            folder_name, 
            video_content_item.get("video_content"), 
            video_content_item.get("extension_file_name"),
            video_content_item.get("title")
        )

    def make_save_file_name(self, folder_name: str, extension_file_name: str, title: str = None) -> str:
        """
        make save file name by store type

        Args:
            folder_name: folder name (bvid or aid)
            extension_file_name: video filename with extension
            title: video title

        Returns:

        """
        if title:
            sanitized_title = utils.sanitize_filename(title)
            # Limit title length to avoid filesystem issues
            if len(sanitized_title) > 50:
                sanitized_title = sanitized_title[:50]
            return f"{self.video_store_path}/{folder_name}/{sanitized_title}_{extension_file_name}"
        return f"{self.video_store_path}/{folder_name}/{extension_file_name}"

    async def save_video(self, folder_name: str, video_content: str, extension_file_name="mp4", title: str = None):
        """
        save video to local

        Args:
            folder_name: folder name (bvid or aid)
            video_content: video content
            extension_file_name: video filename with extension
            title: video title

        Returns:

        """
        pathlib.Path(self.video_store_path + "/" + str(folder_name)).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(str(folder_name), extension_file_name, title)
        async with aiofiles.open(save_file_name, 'wb') as f:
            await f.write(video_content)
            utils.logger.info(f"[BilibiliVideoImplement.save_video] save save_video {save_file_name} success ...")
