import asyncio
import config
from main import CrawlerFactory

# 全局锁，防止并发修改 config 导致冲突
CRAWLER_LOCK = asyncio.Lock()

async def run_crawler(**kwargs):
    """
    运行爬虫的封装函数
    :param kwargs: 配置参数，将覆盖 config 中的设置
    """
    async with CRAWLER_LOCK:
        # 1. 动态更新 config 配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                print(f"⚙️ Config updated: {key} = {value}")
            else:
                # 对于一些不在 base_config 但在 platform config 中的变量，我们也尝试设置
                # 因为 config 导入了所有 platform config，所以 hasattr 应该能检测到
                # 如果检测不到，可能是因为 config 模块的特殊性，我们尝试强制设置
                try:
                    setattr(config, key, value)
                    print(f"⚙️ Config set (new): {key} = {value}")
                except Exception as e:
                    print(f"⚠️ Failed to set config {key}: {e}")

        # 2. 创建并启动爬虫
        try:
            crawler = CrawlerFactory.create_crawler(platform=config.PLATFORM)
            await crawler.start()
            return True
        except Exception as e:
            print(f"❌ Crawler execution failed: {e}")
            raise e
