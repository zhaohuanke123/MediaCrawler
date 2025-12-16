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
    parser.add_argument("video_id", help="Bilibili Video ID")
    args = parser.parse_args()
    
    video_id = args.video_id
    print(f"Task received video_id: {video_id}")

    # Config setup
    config.PLATFORM = "bili"
    config.CRAWLER_TYPE = "detail"
    config.BILI_SPECIFIED_ID_LIST = [video_id]
    config.SAVE_DATA_OPTION = "json"
    config.HEADLESS = True
    config.ENABLE_CDP_MODE = True
    # 禁用爬虫内部的 AI Agent，防止重复运行
    config.ENABLE_AI_AGENT = False
    
    print("Configured crawler for Bilibili.")

    try:
        crawler = CrawlerFactory.create_crawler(platform=config.PLATFORM)
        await crawler.start()
        print("Crawler finished successfully.")
        
        # --- AI Summarization Logic ---
        print("🔍 Checking for video files to summarize...")
        # Video path pattern: data/bili/videos/{video_id}/*.mp4
        video_dir = os.path.join("data", "bili", "videos", video_id)
        video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
        
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
