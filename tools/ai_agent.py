import os
import time
from pathlib import Path
from typing import Optional, List

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
        
        # Initialize prompts
        self.prompts = prompts or VideoSummaryPrompts()

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
            prompt = self.prompts.final_summary.format(
                original_video_name=original_video_name,
                combined_text=combined_text
            )
            
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
    
    def summarize_video(self, video_path: str, auto_split: bool = True, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Summarize video, automatically splitting if longer than max duration
        
        Args:
            video_path: Path to video file
            auto_split: Whether to automatically split long videos (default: True)
            output_dir: Directory to save the summary file. If None, saves in the same directory as video.
            
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
            return self.summarize_video_in_chunks(video_path, output_dir=output_dir)
        
        # Video is short enough, process normally
        utils.logger.info(f"🚀 Uploading video: {video_path_obj.name}")
        
        try:
            video_file = self.client.files.upload(file=video_path_obj)
            self.wait_for_files_active(video_file)

            utils.logger.info("🤖 AI is watching and summarizing the video...")
            
            prompt = self.prompts.single_video

            response = self.client.models.generate_content(
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
                # Cleanup video file even if summarization failed
                try:
                    self.client.files.delete(name=video_file.name)
                    utils.logger.info("🧹 Uploaded video file deleted.")
                except Exception as e:
                    utils.logger.error(f"❌ Error deleting file: {e}")
                return None
            
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
    
    def summarize_video_in_chunks(self, video_path: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Split video into chunks and summarize each chunk with context
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save the summary file. If None, saves in the same directory as video.
            
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
        if output_dir:
            output_path = Path(output_dir) / f"{video_path_obj.stem}_summary.md"
        else:
            output_path = video_path_obj.with_name(f"{video_path_obj.stem}_summary.md")
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_summary)
        
        utils.logger.info(f"✨ Final summary saved to: {output_path}")
        
        return str(output_path)
