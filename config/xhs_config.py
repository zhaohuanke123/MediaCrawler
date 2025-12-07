# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/config/xhs_config.py
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


# 小红书平台配置

# 排序方式，具体的枚举值在media_platform/xhs/field.py中
SORT_TYPE = "popularity_descending"

# 指定笔记URL列表, 必须要携带xsec_token参数
# ⚠️ 重要：不支持短链接！请使用完整的小红书URL
# 获取方法：
#   1. 在浏览器中打开短链接 http://xhslink.com/o/8sw3jfATYB5
#   2. 等待跳转后，复制浏览器地址栏的完整URL（类似下面的格式）
#   3. 粘贴到这里
XHS_SPECIFIED_NOTE_URL_LIST = [
    # 示例格式（请替换为你的真实URL）：
    # "https://www.xiaohongshu.com/explore/64b95d01000000000c034587?xsec_token=AB0EFqJvINCkj6xOCKCQgfNNh8GdnBC_6XecG4QOddo3Q=&xsec_source=pc_cfeed"
    # ........................
    "https://www.xiaohongshu.com/explore/6932a08c000000001e011b88?app_platform=android&ignoreEngage=true&app_version=9.2.0&share_from_user_hidden=true&xsec_source=app_share&type=normal&xsec_token=CBBWATMT2U8GTHIW6xTOaHgYRBxJ-ol-lbETGC_qnmWf8=&author_share=1&shareRedId=ODpEMTU9ND82NzUyOTgwNjZFOTg5SzpK&apptime=1765103056&share_id=cc2df5077dcd4ee19241655b894d8cd5&share_channel=copy_link&appuid=64b12806000000000b015f4a&xhsshare=CopyLink",
]
# 指定创作者URL列表，需要携带xsec_token和xsec_source参数

XHS_CREATOR_ID_LIST = [
    # "https://www.xiaohongshu.com/user/profile/5f58bd990000000001003753?xsec_token=ABYVg1evluJZZzpMX-VWzchxQ1qSNVW3r-jOEnKqMcgZw=&xsec_source=pc_search"
    # ........................
]
