import re
import requests
from typing import Dict, Optional

class SocialMediaLinkParser:
    """
    用于解析社交媒体分享文本的工具类，提取短链接，
    将其解析为真实URL，并执行特定平台的清洗操作。
    """

    def __init__(self):
        # 配置真实的浏览器 User-Agent 以避免反爬虫页面
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _extract_url(self, text: str) -> Optional[str]:
        """
        使用正则表达式从文本中提取第一个 http 或 https 链接。
        在空白字符或通常不出现在这些短链接中的字符处停止。
        """
        # 正则表达式解释:
        # https?://  : 匹配 http:// 或 https://
        # [a-zA-Z0-9\.\/\-\?\&\=\%_]+ : 匹配一个或多个 URL 安全字符
        # 此模式假设链接由空格或其他非 URL 字符（如中文）分隔
        pattern = r'(https?://[a-zA-Z0-9\.\/\-\?\&\=\%_]+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    def _resolve_redirect(self, short_url: str) -> str:
        """
        跟随重定向以获取最终 URL。
        """
        try:
            # allow_redirects=True 是默认值，但为了清晰起见我们显式设置它。
            # 我们必须使用 headers 模拟浏览器，否则某些平台会返回错误页面。
            response = requests.get(short_url, headers=self.headers, allow_redirects=True, timeout=10)
            return response.url
        except requests.RequestException as e:
            print(f"Error resolving URL {short_url}: {e}")
            return short_url

    def _clean_douyin_url(self, url: str) -> str:
        """
        清洗抖音 URL：提取视频 ID 并格式化为 PC 端链接。
        """
        # 目标示例: https://www.douyin.com/video/7315824650938617138
        # 正则表达式查找 /video/ 后跟数字
        match = re.search(r'/video/(\d+)', url)
        if match:
            video_id = match.group(1)
            return f"https://www.douyin.com/video/{video_id}"
        return url

    def _clean_bilibili_url(self, url: str) -> str:
        """
        清洗 Bilibili URL：提取 BV 号并格式化为 PC 端链接。
        """
        # 目标示例: https://www.bilibili.com/video/BV1RTqSBHEwt
        # 正则表达式查找 BV 号 (BV 开头，后跟字母数字)
        match = re.search(r'(BV[a-zA-Z0-9]+)', url)
        if match:
            bv_id = match.group(1)
            return f"https://www.bilibili.com/video/{bv_id}"
        return url

    def parse(self, text: str) -> Dict[str, Optional[str]]:
        """
        解析文本的主方法。
        返回一个包含平台、原始短链接和目标 URL 的字典。
        """
        result = {
            "platform": "unknown",
            "original_short_url": None,
            "target_url": None
        }

        # 1. 提取短链接
        short_url = self._extract_url(text)
        if not short_url:
            return result
        
        result["original_short_url"] = short_url
        
        # 从短链接识别平台（预解析检查）
        if "douyin.com" in short_url:
            result["platform"] = "douyin"
        elif "xhslink.com" in short_url or "xiaohongshu.com" in short_url:
            result["platform"] = "xiaohongshu"
        elif "b23.tv" in short_url or "bilibili.com" in short_url:
            result["platform"] = "bilibili"

        # 2. 解析重定向
        target_url = self._resolve_redirect(short_url)
        
        # 从目标 URL 识别平台（如果之前未找到）
        if result["platform"] == "unknown":
             if "douyin.com" in target_url:
                 result["platform"] = "douyin"
             elif "xiaohongshu.com" in target_url:
                 result["platform"] = "xiaohongshu"
             elif "bilibili.com" in target_url:
                 result["platform"] = "bilibili"

        # 3. 特定平台清洗
        if result["platform"] == "douyin":
            target_url = self._clean_douyin_url(target_url)
        elif result["platform"] == "bilibili":
            target_url = self._clean_bilibili_url(target_url)
        # 对于小红书和其他平台，我们保持解析后的 URL 不变。
        
        result["target_url"] = target_url
        
        return result

if __name__ == "__main__":
    parser = SocialMediaLinkParser()
    
    # Test Case 1: Douyin
    douyin_text = "1.79 复制打开抖音，看看【摄影讲师李小龙的作品】圣诞拍照人多脸黑？3个万能技巧包你出片！# 圣诞拍... https://v.douyin.com/t7IdmCX99yQ/ ZZz:/ G@i.pD 04/03"
    print("Testing Douyin:")
    print(f"Input: {douyin_text}")
    douyin_result = parser.parse(douyin_text)
    print(f"Result: {douyin_result}")
    print("-" * 50)

    print("-" * 50)

    # Test Case 3: Bilibili
    bili_text = "【高级傻X，是怎样炼成的？知识分子的四种幻觉！-哔哩哔哩】 https://b23.tv/pmE3AAv"
    print("Testing Bilibili:")
    print(f"Input: {bili_text}")
    bili_result = parser.parse(bili_text)
    print(f"Result: {bili_result}")
    # Test Case 2: Xiaohongshu
    xhs_text = "给应届生泼盆冷水：算算月薪1w在上海的真实 http://xhslink.com/o/944F67UcrQQ 复制后打开【小红书】查看笔记！"
    print("Testing Xiaohongshu:")
    print(f"Input: {xhs_text}")
    xhs_result = parser.parse(xhs_text)
    print(f"Result: {xhs_result}")
