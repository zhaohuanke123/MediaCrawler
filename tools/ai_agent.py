import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import utils

load_dotenv()

class VideoSummarizer:
    def __init__(self, api_key: Optional[str] = None, proxy_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            utils.logger.warning("GEMINI_API_KEY not found. AI Agent functionality might not work.")
            # We don't return here to allow instantiation even if key is missing, 
            # but methods should check for it.

        self.proxy_url = proxy_url or os.getenv("HTTP_PROXY") or "http://127.0.0.1:7897"
        
        # Set proxy environment variables if provided or found
        if self.proxy_url:
            os.environ["http_proxy"] = self.proxy_url
            os.environ["https_proxy"] = self.proxy_url

        if self.api_key:
            self.client = genai.Client(
                api_key=self.api_key,
                http_options={'api_version': 'v1beta'}
            )
        else:
            self.client = None

    def wait_for_files_active(self, file_upload):
        """
        Wait for file processing to complete
        """
        utils.logger.info("⏳ Waiting for video file processing...")
        
        while file_upload.state.name == "PROCESSING":
            time.sleep(5)
            file_upload = self.client.files.get(name=file_upload.name)
            
        if file_upload.state.name != "ACTIVE":
            raise Exception(f"File processing failed: {file_upload.state.name}")
        utils.logger.info("✅ Video processing completed!")

    def summarize_video(self, video_path: str) -> Optional[str]:
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        utils.logger.info(f"🚀 Uploading video: {video_path_obj.name}")
        
        try:
            video_file = self.client.files.upload(file=video_path_obj)
            self.wait_for_files_active(video_file)

            utils.logger.info("🤖 AI is watching and summarizing the video...")
            
            prompt = """
            请作为一名专业的笔记整理员，观看这段视频并进行详细总结。
            输出格式要求为 Markdown，包含以下部分：
            1. **视频一句话摘要**：简明扼要。
            2. **关键要点 (Key Takeaways)**：使用列表形式。
            3. **详细内容**：按时间逻辑或主题逻辑分段落描述，如果视频中有明确的章节，请列出。
            4. **后续思考**：基于视频内容延伸的一个启发。
            请用中文输出。
            """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            output_path = video_path_obj.with_name(f"{video_path_obj.stem}_summary.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            utils.logger.info(f"✨ Summary saved to: {output_path}")
            
            # Cleanup
            try:
                self.client.files.delete(name=video_file.name)
                utils.logger.info("🧹 Uploaded video file deleted.")
            except Exception as e:
                utils.logger.error(f"❌ Error deleting file: {e}")

            return str(output_path)

        except Exception as e:
            utils.logger.error(f"❌ Error during summarization: {e}")
            return None
