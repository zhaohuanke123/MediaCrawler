# -*- coding: utf-8 -*-
"""
Video splitter tool for splitting long videos into chunks.
This is needed because Gemini API doesn't support videos longer than 1 hour.
"""
import os
from pathlib import Path
from typing import List, Optional
import subprocess

from tools import utils


class VideoSplitter:
    """
    Split video files into smaller chunks based on duration.
    Uses ffmpeg for accurate and efficient video splitting.
    """
    
    def __init__(self, max_duration_minutes: int = 30):
        """
        Initialize VideoSplitter
        
        Args:
            max_duration_minutes: Maximum duration of each chunk in minutes (default: 30)
        """
        self.max_duration_seconds = max_duration_minutes * 60
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            utils.logger.warning(
                "⚠️ ffmpeg not found. Video splitting requires ffmpeg. "
                "Please install it: https://ffmpeg.org/download.html"
            )
    
    def get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get video duration in seconds using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds, or None if unable to determine
        """
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    video_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            duration = float(result.stdout.strip())
            utils.logger.info(f"📊 Video duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return duration
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            utils.logger.error(f"❌ Error getting video duration: {e}")
            return None
    
    def needs_splitting(self, video_path: str) -> bool:
        """
        Check if video needs to be split
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if video duration exceeds max_duration_seconds
        """
        duration = self.get_video_duration(video_path)
        if duration is None:
            return False
        return duration > self.max_duration_seconds
    
    def split_video(self, video_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Split video into chunks of max_duration_seconds
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save chunks (default: same as video)
            
        Returns:
            List of paths to video chunks
        """
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            utils.logger.error(f"❌ Error: Video file not found {video_path}")
            return []
        
        duration = self.get_video_duration(video_path)
        if duration is None:
            utils.logger.error(f"❌ Cannot determine video duration")
            return []
        
        # Calculate number of chunks needed
        num_chunks = int((duration + self.max_duration_seconds - 1) / self.max_duration_seconds)
        
        if num_chunks <= 1:
            utils.logger.info("ℹ️ Video is short enough, no splitting needed")
            return [str(video_path)]
        
        utils.logger.info(f"✂️ Splitting video into {num_chunks} chunks...")
        
        # Setup output directory
        if output_dir is None:
            output_dir = video_path_obj.parent / f"{video_path_obj.stem}_chunks"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Split video using ffmpeg
        chunk_paths = []
        for i in range(num_chunks):
            start_time = i * self.max_duration_seconds
            chunk_name = f"{video_path_obj.stem}_chunk_{i+1:03d}{video_path_obj.suffix}"
            chunk_path = output_dir / chunk_name
            
            utils.logger.info(f"📹 Creating chunk {i+1}/{num_chunks}: {chunk_name}")
            
            try:
                # Use ffmpeg to extract chunk
                # -ss: start time, -t: duration, -c copy: copy codec (fast, no re-encoding)
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",  # Overwrite output file
                        "-i", str(video_path),
                        "-ss", str(start_time),
                        "-t", str(self.max_duration_seconds),
                        "-c", "copy",  # Copy codec without re-encoding
                        "-avoid_negative_ts", "1",  # Avoid negative timestamps
                        str(chunk_path)
                    ],
                    capture_output=True,
                    check=True
                )
                chunk_paths.append(str(chunk_path))
                utils.logger.info(f"✅ Chunk {i+1} created: {chunk_path}")
            except subprocess.CalledProcessError as e:
                utils.logger.error(f"❌ Error creating chunk {i+1}: {e}")
                utils.logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
                # Continue with other chunks even if one fails
        
        if chunk_paths:
            utils.logger.info(f"✨ Successfully created {len(chunk_paths)} video chunks")
        else:
            utils.logger.error(f"❌ Failed to create any video chunks")
        
        return chunk_paths
