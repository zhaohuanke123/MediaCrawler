import sys
import asyncio
import argparse
import os
import glob
from main import CrawlerFactory
import config
from tools.ai_agent import VideoSummarizer

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("platform", help="Platform (bili, dy, xhs)")
    parser.add_argument("video_id", help="Video ID or Note ID")
    args = parser.parse_args()
    
    platform = args.platform
    video_id = args.video_id
    print(f"Task received platform: {platform}, video_id: {video_id}")

    # Config setup
    config.PLATFORM = platform
    config.CRAWLER_TYPE = "detail"
    config.SAVE_DATA_OPTION = "json"
    config.HEADLESS = True
    config.ENABLE_CDP_MODE = True
    # 禁用爬虫内部的 AI Agent，防止重复运行
    config.ENABLE_AI_AGENT = False

    # Platform specific config
    if platform == "bili":
        config.BILI_SPECIFIED_ID_LIST = [video_id]
        data_dir = os.path.join("data", "bili", "videos", video_id)
    elif platform == "dy":
        config.DY_SPECIFIED_ID_LIST = [video_id]
        data_dir = os.path.join("data", "douyin", "videos", video_id)
    elif platform == "xhs":
        # config.XHS_SPECIFIED_ID_LIST = [video_id]
        # XHS might save images or videos. For now assume videos or check both?
        # XHS crawler structure might be different. Let's assume data/xhs/notes/{id} or similar.
        # Checking MediaCrawler structure, usually it is data/xhs/...
        # Let's check where XHS saves files.
        # data_dir = os.path.join("data", "xhs", "videos", video_id) # Guessing
        pass
    else:
        print(f"❌ Unsupported platform: {platform}")
        sys.exit(1)
    
    print(f"Configured crawler for {platform}.")

    try:
        crawler = CrawlerFactory.create_crawler(platform=config.PLATFORM)
        await crawler.start()
        print("Crawler finished successfully.")
        
        # --- AI Summarization Logic ---
        print("🔍 Checking for video files to summarize...")
        
        # Search for video files
        # Note: XHS might not have videos if it's an image note.
        video_files = []
        if os.path.exists(data_dir):
             video_files = glob.glob(os.path.join(data_dir, "*.mp4"))
        
        # If no specific video dir, try searching in platform root (some crawlers might behave differently)
        if not video_files:
             # Fallback or different structure check
             pass

        if video_files:
            video_path = video_files[0]
            print(f"📹 Found video: {video_path}")
            
            # Define output directory for summaries
            output_dir = os.path.join(os.getcwd(), "summary_output")
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🤖 Starting AI summarization... (Output dir: {output_dir})")
            summarizer = VideoSummarizer()
            
            # Check if API key is available
            if not summarizer.client:
                print("⚠️ GEMINI_API_KEY not found. Skipping summarization.")
            else:
                summary_path = summarizer.summarize_video(video_path, output_dir=output_dir)
                
                if summary_path:
                    print(f"✅ Summary generated at: {summary_path}")
                    try:
                        with open(summary_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Print with delimiters for server.py to parse
                            print(f"__SUMMARY_START__\n{content}\n__SUMMARY_END__")
                    except Exception as e:
                        print(f"❌ Failed to read summary file: {e}")
                else:
                    print("❌ Summarization failed.")
        else:
            print(f"⚠️ No video file found in {video_dir}")
            
    except Exception as e:
        print(f"Crawler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 爬虫进程仍然需要 ProactorEventLoopPolicy 来支持 Playwright
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
