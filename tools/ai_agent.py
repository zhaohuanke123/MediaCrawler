import os
import time
from pathlib import Path
from typing import Optional, List

from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import utils
from tools.video_splitter import VideoSplitter
from tools.ai_prompt import VideoSummaryPrompts

load_dotenv()

class VideoSummarizer:
    def __init__(self, api_key: Optional[str] = None, proxy_url: Optional[str] = None, max_chunk_duration: int = 45, prompts: Optional[VideoSummaryPrompts] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            utils.logger.warning("GEMINI_API_KEY not found. AI Agent functionality might not work.")
            # 即使缺少密钥，我们也不在此处返回，以允许实例化，
            # 但方法应检查它。

        self.proxy_url = proxy_url or os.getenv("HTTP_PROXY") or "http://127.0.0.1:7897"
        
        # 如果提供 or 找到代理环境变量，则设置它们
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
        
        # 初始化视频分割器
        self.video_splitter = VideoSplitter(max_duration_minutes=max_chunk_duration)
        
        # 初始化提示词
        self.prompts = prompts or VideoSummaryPrompts()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _upload_file_with_retry(self, file_path: Path):
        return self.client.files.upload(file=file_path)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _generate_content_with_retry(self, model, contents, config):
        return self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_file_with_retry(self, name):
        return self.client.files.get(name=name)

    def wait_for_files_active(self, file_upload):
        """
        等待文件处理完成
        """
        utils.logger.info("⏳ Waiting for video file processing...")
        
        while file_upload.state.name == "PROCESSING":
            time.sleep(5)
            file_upload = self._get_file_with_retry(name=file_upload.name)
            
        if file_upload.state.name != "ACTIVE":
            raise Exception(f"File processing failed: {file_upload.state.name}")
        utils.logger.info("✅ Video processing completed!")

    def _summarize_single_chunk(self, video_path: str, chunk_index: int, total_chunks: int, 
                               previous_summary: Optional[str] = None) -> Optional[str]:
        """
        结合之前的总结上下文，总结单个视频分片
        
        参数:
            video_path: 视频分片路径
            chunk_index: 当前分片索引（从1开始）
            total_chunks: 分片总数
            previous_summary: 来自前一个分片的总结，用于上下文
            
        返回:
            总结文本，如果失败则返回 None
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
            video_file = self._upload_file_with_retry(file_path=video_path_obj)
            self.wait_for_files_active(video_file)

            utils.logger.info(f"🤖 AI is watching and summarizing chunk {chunk_index}/{total_chunks}...")
            
            # 根据是第一个分片还是后续分片构建提示词
            if chunk_index == 1:
                prompt = self.prompts.chunk_first.format(
                    chunk_index=chunk_index,
                    total_chunks=total_chunks
                )
            else:
                prompt = self.prompts.chunk_continuation.format(
                    chunk_index=chunk_index,
                    total_chunks=total_chunks,
                    previous_summary=previous_summary
                )

            response = self._generate_content_with_retry(
                model="gemini-2.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            # 清理上传的文件
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
        从所有分片总结中生成最终的综合总结
        
        参数:
            chunk_summaries: 每个分片的总结列表
            original_video_name: 原始视频文件名
            
        返回:
            最终合并的总结文本
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
            prompt = self.prompts.final_summary.format(
                original_video_name=original_video_name,
                combined_text=combined_text
            )
            
            response = self._generate_content_with_retry(
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
    
    def summarize_video(self, video_path: str, auto_split: bool = True, output_dir: Optional[str] = None) -> Optional[str]:
        """
        总结视频，如果超过最大时长则自动分割
        
        参数:
            video_path: 视频文件路径
            auto_split: 是否自动分割长视频（默认: True）
            output_dir: 保存总结文件的目录。如果为 None，则保存在与视频相同的目录中。
            
        返回:
            总结 Markdown 文件的路径，如果失败则返回 None
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        # 检查视频是否需要分割
        if auto_split and self.video_splitter.needs_splitting(video_path):
            utils.logger.info("📹 Video is longer than limit, splitting into chunks...")
            return self.summarize_video_in_chunks(video_path, output_dir=output_dir)
        
        # 视频足够短，正常处理
        utils.logger.info(f"🚀 Uploading video: {video_path_obj.name}")
        
        try:
            video_file = self._upload_file_with_retry(file_path=video_path_obj)
            self.wait_for_files_active(video_file)

            utils.logger.info("🤖 AI is watching and summarizing the video...")
            
            prompt = self.prompts.single_video

            response = self._generate_content_with_retry(
                model="gemini-2.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7
                )
            )
            
            if output_dir:
                output_path = Path(output_dir) / f"{video_path_obj.stem}_summary.md"
            else:
                output_path = video_path_obj.with_name(f"{video_path_obj.stem}_summary.md")
            
            if response.text:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                utils.logger.info(f"✨ Summary saved to: {output_path}")
            else:
                utils.logger.error("❌ AI returned no text. Possible safety block or empty response.")
                # 即使总结失败也清理视频文件
                try:
                    self.client.files.delete(name=video_file.name)
                    utils.logger.info("🧹 Uploaded video file deleted.")
                except Exception as e:
                    utils.logger.error(f"❌ Error deleting file: {e}")
                return None
            
            # 清理
            try:
                self.client.files.delete(name=video_file.name)
                utils.logger.info("🧹 Uploaded video file deleted.")
            except Exception as e:
                utils.logger.error(f"❌ Error deleting file: {e}")

            return str(output_path)

        except Exception as e:
            utils.logger.error(f"❌ Error during summarization: {e}")
            return None
    
    def summarize_video_in_chunks(self, video_path: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        将视频分割成块，并结合上下文总结每个块
        
        参数:
            video_path: 视频文件路径
            output_dir: 保存总结文件的目录。如果为 None，则保存在与视频相同的目录中。
            
        返回:
            最终总结 Markdown 文件的路径，如果失败则返回 None
        """
        if not self.client:
            utils.logger.warning("VideoSummarizer not initialized with API key.")
            return None

        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: File not found {video_path}")
            return None

        # 将视频分割成块
        chunk_paths = self.video_splitter.split_video(video_path)
        if not chunk_paths:
            utils.logger.error("❌ Failed to split video")
            return None
        
        utils.logger.info(f"📝 Processing {len(chunk_paths)} video chunks...")
        
        # 处理每个块
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
                # 继续处理其他块
        
        if not chunk_summaries:
            utils.logger.error("❌ No chunks were successfully summarized")
            return None
        
        # 生成最终的综合总结
        final_summary = self._generate_final_summary(chunk_summaries, video_path_obj.name)
        
        # 保存最终总结
        if output_dir:
            output_path = Path(output_dir) / f"{video_path_obj.stem}_summary.md"
        else:
            output_path = video_path_obj.with_name(f"{video_path_obj.stem}_summary.md")
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_summary)
        
        utils.logger.info(f"✨ Final summary saved to: {output_path}")
        
        return str(output_path)
