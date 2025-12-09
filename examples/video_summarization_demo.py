#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script for video summarization with automatic splitting for long videos.

This example demonstrates:
1. How to use VideoSplitter to split long videos
2. How to use VideoSummarizer to summarize videos (with automatic splitting)
3. How to manually control the summarization process

Prerequisites:
- GEMINI_API_KEY environment variable set (or pass api_key parameter)
- ffmpeg and ffprobe installed on the system
- Video file(s) to process

Usage:
    python examples/video_summarization_demo.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.ai_agent import VideoSummarizer
from tools.video_splitter import VideoSplitter


def demo_video_splitter():
    """Demonstrate video splitting functionality"""
    print("=" * 80)
    print("DEMO 1: Video Splitting")
    print("=" * 80)
    
    # Create a video splitter with 30-minute chunks (default)
    splitter = VideoSplitter(max_duration_minutes=30)
    
    # Example video path (replace with your actual video)
    video_path = "/path/to/your/long_video.mp4"
    
    # Check if video needs splitting
    if not Path(video_path).exists():
        print(f"⚠️ Video not found: {video_path}")
        print("   Please update the video_path variable with an actual video file")
        return
    
    print(f"\n📹 Checking video: {video_path}")
    
    # Get video duration
    duration = splitter.get_video_duration(video_path)
    if duration:
        print(f"   Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    
    # Check if splitting is needed
    needs_split = splitter.needs_splitting(video_path)
    print(f"   Needs splitting: {needs_split}")
    
    if needs_split:
        print("\n✂️ Splitting video into chunks...")
        chunk_paths = splitter.split_video(video_path)
        print(f"\n✅ Created {len(chunk_paths)} chunks:")
        for i, chunk_path in enumerate(chunk_paths, 1):
            print(f"   {i}. {chunk_path}")
    else:
        print("\nℹ️ Video is short enough, no splitting needed")


def demo_basic_summarization():
    """Demonstrate basic video summarization"""
    print("\n" + "=" * 80)
    print("DEMO 2: Basic Video Summarization (Short Video)")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Please set it to use video summarization features")
        return
    
    # Create summarizer
    summarizer = VideoSummarizer(api_key=api_key)
    
    # Example short video path
    video_path = "/path/to/your/short_video.mp4"
    
    if not Path(video_path).exists():
        print(f"⚠️ Video not found: {video_path}")
        print("   Please update the video_path variable with an actual video file")
        return
    
    print(f"\n📹 Processing video: {video_path}")
    print("   This will upload the video to Gemini API and generate a summary")
    
    # Summarize video (auto-split disabled for short videos)
    summary_path = summarizer.summarize_video(video_path, auto_split=False)
    
    if summary_path:
        print(f"\n✅ Summary generated: {summary_path}")
        print("\nPreview of summary:")
        print("-" * 80)
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 80)
    else:
        print("\n❌ Failed to generate summary")


def demo_auto_split_summarization():
    """Demonstrate automatic splitting and summarization for long videos"""
    print("\n" + "=" * 80)
    print("DEMO 3: Auto-Split Video Summarization (Long Video)")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Please set it to use video summarization features")
        return
    
    # Create summarizer with custom chunk duration (e.g., 20 minutes for faster processing)
    summarizer = VideoSummarizer(api_key=api_key, max_chunk_duration=20)
    
    # Example long video path
    video_path = "/path/to/your/long_video.mp4"
    
    if not Path(video_path).exists():
        print(f"⚠️ Video not found: {video_path}")
        print("   Please update the video_path variable with an actual video file")
        return
    
    print(f"\n📹 Processing long video: {video_path}")
    print("   This will:")
    print("   1. Check if video exceeds 30 minutes")
    print("   2. Split into chunks if needed")
    print("   3. Process each chunk with context from previous chunks")
    print("   4. Generate final comprehensive summary")
    
    # Summarize video (auto-split enabled by default)
    summary_path = summarizer.summarize_video(video_path, auto_split=True)
    
    if summary_path:
        print(f"\n✅ Final summary generated: {summary_path}")
        print("\nPreview of summary:")
        print("-" * 80)
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 80)
    else:
        print("\n❌ Failed to generate summary")


def demo_manual_chunk_processing():
    """Demonstrate manual control over chunk processing"""
    print("\n" + "=" * 80)
    print("DEMO 4: Manual Chunk Processing")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        return
    
    # Create summarizer
    summarizer = VideoSummarizer(api_key=api_key)
    
    # Example long video path
    video_path = "/path/to/your/long_video.mp4"
    
    if not Path(video_path).exists():
        print(f"⚠️ Video not found: {video_path}")
        return
    
    print(f"\n📹 Manual processing of: {video_path}")
    
    # Step 1: Split video manually
    print("\nStep 1: Splitting video...")
    splitter = VideoSplitter(max_duration_minutes=30)
    chunk_paths = splitter.split_video(video_path)
    
    if not chunk_paths:
        print("❌ Failed to split video")
        return
    
    print(f"✅ Created {len(chunk_paths)} chunks")
    
    # Step 2: Process chunks manually
    print("\nStep 2: Processing chunks...")
    chunk_summaries = []
    previous_summary = None
    
    for i, chunk_path in enumerate(chunk_paths):
        print(f"\n   Processing chunk {i+1}/{len(chunk_paths)}...")
        
        summary = summarizer._summarize_single_chunk(
            chunk_path,
            chunk_index=i+1,
            total_chunks=len(chunk_paths),
            previous_summary=previous_summary
        )
        
        if summary:
            chunk_summaries.append(summary)
            previous_summary = summary
            print(f"   ✅ Chunk {i+1} completed")
        else:
            print(f"   ❌ Chunk {i+1} failed")
    
    # Step 3: Generate final summary
    print("\nStep 3: Generating final summary...")
    if chunk_summaries:
        final_summary = summarizer._generate_final_summary(
            chunk_summaries,
            Path(video_path).name
        )
        
        # Save final summary
        output_path = Path(video_path).with_name(f"{Path(video_path).stem}_summary.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_summary)
        
        print(f"✅ Final summary saved: {output_path}")
    else:
        print("❌ No chunks were successfully processed")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "     Video Summarization Demo - Automatic Splitting for Long Videos      ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run demos (comment out any you don't want to run)
    demo_video_splitter()
    # demo_basic_summarization()
    # demo_auto_split_summarization()
    # demo_manual_chunk_processing()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Update video paths in the demo functions")
    print("2. Set GEMINI_API_KEY environment variable")
    print("3. Install ffmpeg/ffprobe if not already installed")
    print("4. Uncomment the demos you want to run")
    print("\nFor more information, see:")
    print("  - tools/video_splitter.py")
    print("  - tools/ai_agent.py")
    print("  - tests/test_video_splitter.py")
    print("  - tests/test_ai_agent.py")
    print()


if __name__ == "__main__":
    main()
