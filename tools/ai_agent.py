import os
import time
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import utils
from tools.video_splitter import VideoSplitter

load_dotenv()

class VideoSummarizer:
    def __init__(self, api_key: Optional[str] = None, proxy_url: Optional[str] = None, max_chunk_duration: int = 30):
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
        
        # Initialize video splitter
        self.video_splitter = VideoSplitter(max_duration_minutes=max_chunk_duration)

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

    def _summarize_single_chunk(self, video_path: str, chunk_index: int, total_chunks: int, 
                               previous_summary: Optional[str] = None) -> Optional[str]:
        """
        Summarize a single video chunk with context from previous summaries
        
        Args:
            video_path: Path to video chunk
            chunk_index: Index of current chunk (1-based)
            total_chunks: Total number of chunks
            previous_summary: Summary from previous chunk(s) for context
            
        Returns:
            Summary text or None if failed
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        utils.logger.info(f"🚀 Uploading video chunk {chunk_index}/{total_chunks}: {video_path_obj.name}")
        
        try:
            video_file = self.client.files.upload(file=video_path_obj)
            self.wait_for_files_active(video_file)

            utils.logger.info(f"🤖 AI is watching and summarizing chunk {chunk_index}/{total_chunks}...")
            
            # Build prompt based on whether this is first chunk or continuation
            if chunk_index == 1:
                prompt = f"""
                请作为一名专业的笔记整理员，观看这段视频并进行详细总结。
                注意：这是一个长视频的第 {chunk_index} 部分（共 {total_chunks} 部分）。
                
                输出格式要求为 Markdown，包含以下部分：
                1. **本段摘要**：简明扼要地总结本段内容。
                2. **关键要点**：使用列表形式列出本段的关键信息。
                3. **详细内容**：按时间逻辑或主题逻辑分段落描述本段内容。
                
                请用中文输出。
                """
            else:
                prompt = f"""
                请作为一名专业的笔记整理员，继续观看这段视频并进行详细总结。
                这是一个长视频的第 {chunk_index} 部分（共 {total_chunks} 部分）。
                
                **前面部分的总结：**
                {previous_summary}
                
                请在理解前面内容的基础上，总结本段新内容。输出格式要求为 Markdown，包含：
                1. **本段摘要**：简明扼要地总结本段内容，与前面内容的衔接。
                2. **关键要点**：使用列表形式列出本段的关键信息。
                3. **详细内容**：按时间逻辑或主题逻辑分段落描述本段内容。
                
                请用中文输出。
                """

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            # Cleanup uploaded file
            try:
                self.client.files.delete(name=video_file.name)
                utils.logger.info(f"🧹 Chunk {chunk_index} file deleted from server.")
            except Exception as e:
                utils.logger.error(f"❌ Error deleting file: {e}")

            return response.text

        except Exception as e:
            utils.logger.error(f"❌ Error during chunk {chunk_index} summarization: {e}")
            return None
    
    def _generate_final_summary(self, chunk_summaries: List[str], original_video_name: str) -> str:
        """
        Generate final comprehensive summary from all chunk summaries
        
        Args:
            chunk_summaries: List of summaries from each chunk
            original_video_name: Name of original video file
            
        Returns:
            Final combined summary text
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return "\n\n---\n\n".join(chunk_summaries)

        utils.logger.info("🤖 Generating final comprehensive summary...")
        
        combined_text = "\n\n---\n\n".join([
            f"## 第 {i+1} 部分总结\n\n{summary}" 
            for i, summary in enumerate(chunk_summaries)
        ])
        
        try:
            prompt = f"""
            请作为一名专业的笔记整理员，基于以下各部分的总结，生成一个完整、连贯的视频总结。
            
            视频文件名：{original_video_name}
            
            各部分总结：
            {combined_text}
            
            请整合所有内容，输出格式要求为 Markdown，包含以下部分：
            1. **视频完整摘要**：简明扼要地概括整个视频的核心内容。
            2. **关键要点 (Key Takeaways)**：整合所有部分的关键信息，使用列表形式。
            3. **详细内容**：按逻辑顺序整合所有部分的内容，形成连贯的叙述。
            4. **总结与思考**：基于完整视频内容的总结性思考和启发。
            
            请用中文输出。
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            return response.text
            
        except Exception as e:
            utils.logger.error(f"❌ Error generating final summary: {e}")
            utils.logger.info("ℹ️ Falling back to concatenated summaries")
            return combined_text
    
    def summarize_video(self, video_path: str, auto_split: bool = True) -> Optional[str]:
        """
        Summarize video, automatically splitting if longer than max duration
        
        Args:
            video_path: Path to video file
            auto_split: Whether to automatically split long videos (default: True)
            
        Returns:
            Path to summary markdown file, or None if failed
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        # Check if video needs splitting
        if auto_split and self.video_splitter.needs_splitting(video_path):
            utils.logger.info("📹 Video is longer than limit, splitting into chunks...")
            return self.summarize_video_in_chunks(video_path)
        
        # Video is short enough, process normally
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
    
    def summarize_video_in_chunks(self, video_path: str) -> Optional[str]:
        """
        Split video into chunks and summarize each chunk with context
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to final summary markdown file, or None if failed
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        # Split video into chunks
        chunk_paths = self.video_splitter.split_video(video_path)
        if not chunk_paths:
            utils.logger.error("❌ Failed to split video")
            return None
        
        utils.logger.info(f"📝 Processing {len(chunk_paths)} video chunks...")
        
        # Process each chunk
        chunk_summaries = []
        previous_summary = None
        
        for i, chunk_path in enumerate(chunk_paths):
            summary = self._summarize_single_chunk(
                chunk_path, 
                chunk_index=i + 1,
                total_chunks=len(chunk_paths),
                previous_summary=previous_summary
            )
            
            if summary:
                chunk_summaries.append(summary)
                previous_summary = summary
                utils.logger.info(f"✅ Chunk {i+1}/{len(chunk_paths)} summarized")
            else:
                utils.logger.error(f"❌ Failed to summarize chunk {i+1}")
                # Continue with other chunks
        
        if not chunk_summaries:
            utils.logger.error("❌ No chunks were successfully summarized")
            return None
        
        # Generate final comprehensive summary
        final_summary = self._generate_final_summary(chunk_summaries, video_path_obj.name)
        
        # Save final summary
        output_path = video_path_obj.with_name(f"{video_path_obj.stem}_summary.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_summary)
        
        utils.logger.info(f"✨ Final summary saved to: {output_path}")
        
        return str(output_path)
