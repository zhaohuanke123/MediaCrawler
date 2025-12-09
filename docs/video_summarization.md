# Video Summarization with Automatic Splitting

This feature enables AI-powered video summarization using Google's Gemini API, with automatic splitting for videos longer than 30 minutes.

## Overview

The Gemini API has a limit of 1 hour for video processing. To handle longer videos, this implementation:

1. **Automatically detects** videos longer than 30 minutes
2. **Splits them** into manageable chunks using ffmpeg
3. **Processes each chunk** with context from previous chunks
4. **Generates a comprehensive summary** combining all chunks

## Features

### VideoSplitter (`tools/video_splitter.py`)

- Split videos into chunks of configurable duration (default: 30 minutes)
- Uses ffmpeg/ffprobe for efficient video processing
- No re-encoding (uses codec copying for speed)
- Automatic duration detection
- Custom output directory support

### VideoSummarizer (`tools/ai_agent.py`)

- Automatic video splitting for long videos
- Contextual summarization (each chunk includes summary of previous chunks)
- Final comprehensive summary generation
- Support for manual chunk processing
- Configurable chunk duration

## Requirements

### System Requirements

- **ffmpeg** and **ffprobe** installed and available in PATH
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from https://ffmpeg.org/download.html

### Python Requirements

```bash
pip install google-genai python-dotenv
```

### API Key

Set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
GEMINI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage (Automatic Mode)

The simplest way to use the video summarizer:

```python
from tools.ai_agent import VideoSummarizer

# Create summarizer (reads GEMINI_API_KEY from environment)
summarizer = VideoSummarizer()

# Summarize video (automatically splits if needed)
summary_path = summarizer.summarize_video("/path/to/video.mp4")

print(f"Summary saved to: {summary_path}")
```

### Custom Configuration

```python
from tools.ai_agent import VideoSummarizer

# Custom chunk duration and API configuration
summarizer = VideoSummarizer(
    api_key="your-api-key",
    proxy_url="http://proxy:8080",
    max_chunk_duration=20  # 20-minute chunks instead of 30
)

# Process video
summary_path = summarizer.summarize_video("/path/to/long_video.mp4")
```

### Manual Video Splitting

```python
from tools.video_splitter import VideoSplitter

# Create splitter with 30-minute chunks
splitter = VideoSplitter(max_duration_minutes=30)

# Check if video needs splitting
if splitter.needs_splitting("/path/to/video.mp4"):
    # Split the video
    chunk_paths = splitter.split_video(
        "/path/to/video.mp4",
        output_dir="/path/to/output"
    )
    print(f"Created {len(chunk_paths)} chunks")
```

### Manual Chunk Processing

For more control over the summarization process:

```python
from tools.ai_agent import VideoSummarizer
from tools.video_splitter import VideoSplitter

# Split video
splitter = VideoSplitter(max_duration_minutes=30)
chunks = splitter.split_video("/path/to/video.mp4")

# Process each chunk
summarizer = VideoSummarizer()
chunk_summaries = []
previous_summary = None

for i, chunk_path in enumerate(chunks):
    summary = summarizer._summarize_single_chunk(
        chunk_path,
        chunk_index=i+1,
        total_chunks=len(chunks),
        previous_summary=previous_summary
    )
    chunk_summaries.append(summary)
    previous_summary = summary

# Generate final summary
final_summary = summarizer._generate_final_summary(
    chunk_summaries,
    "video.mp4"
)
```

### Disable Auto-Splitting

If you want to process a long video without splitting (not recommended for videos over 1 hour):

```python
summarizer = VideoSummarizer()
summary_path = summarizer.summarize_video(
    "/path/to/video.mp4",
    auto_split=False  # Disable automatic splitting
)
```

## Output Format

The generated summary is a Markdown file with the following structure:

### For Short Videos (< 30 minutes)

```markdown
# 视频一句话摘要

Brief summary of the video

# 关键要点 (Key Takeaways)

- Key point 1
- Key point 2
- Key point 3

# 详细内容

Detailed content organized by time or topic...

# 后续思考

Follow-up thoughts and insights...
```

### For Long Videos (> 30 minutes)

```markdown
# 视频完整摘要

Complete summary of the entire video

# 关键要点 (Key Takeaways)

- Integrated key points from all chunks
- ...

# 详细内容

Coherent narrative combining all chunks...

# 总结与思考

Overall conclusions and insights...
```

## How It Works

### Video Splitting Process

1. **Duration Detection**: Uses `ffprobe` to get video duration
2. **Chunk Calculation**: Determines number of chunks needed
3. **Splitting**: Uses `ffmpeg` with codec copying (no re-encoding) for speed
4. **Output**: Creates numbered chunks (e.g., `video_chunk_001.mp4`, `video_chunk_002.mp4`)

### Summarization Process

For long videos:

1. **Detection**: Checks if video exceeds `max_chunk_duration`
2. **Splitting**: Automatically splits into chunks
3. **First Chunk**: Summarizes with initial prompt
4. **Subsequent Chunks**: Each summary includes context from previous chunks
5. **Final Summary**: Combines all chunk summaries into comprehensive summary
6. **Cleanup**: Uploads are deleted from Gemini API after processing

## Testing

Comprehensive test suites are provided:

```bash
# Test video splitter
pytest tests/test_video_splitter.py -v

# Test AI agent
pytest tests/test_ai_agent.py -v

# Run all tests
pytest tests/test_video_splitter.py tests/test_ai_agent.py -v
```

### Test Coverage

- **VideoSplitter**: 18 tests covering all functionality
- **VideoSummarizer**: 23 tests covering all scenarios
- Edge cases: exact duration limits, partial failures, missing files, etc.

## Examples

See `examples/video_summarization_demo.py` for complete working examples:

```bash
python examples/video_summarization_demo.py
```

The demo includes:
1. Video splitting demonstration
2. Basic video summarization
3. Automatic split summarization
4. Manual chunk processing

## Troubleshooting

### ffmpeg not found

**Error**: `⚠️ ffmpeg not found`

**Solution**: Install ffmpeg:
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download and add to PATH

### API Key Issues

**Error**: `GEMINI_API_KEY not found`

**Solution**: Set the environment variable or pass it directly:
```python
summarizer = VideoSummarizer(api_key="your-key")
```

### Video Processing Timeout

**Issue**: Video processing takes too long

**Solution**: The system waits for Gemini to process the video. For very large videos, this may take several minutes. Consider:
- Using smaller chunk sizes (`max_chunk_duration=20`)
- Compressing the video before processing
- Checking Gemini API quotas

### Chunk Upload Failures

**Issue**: Some chunks fail to process

**Solution**: The system continues with remaining chunks and generates summary from successful ones. Check:
- Internet connection stability
- API quota limits
- Chunk file sizes

## Performance Considerations

### Processing Time

- **Short videos** (< 30 min): ~2-5 minutes per video
- **Long videos**: ~2-5 minutes per chunk + 1-2 minutes for final summary
- **Example**: 90-minute video = 3 chunks × 3 minutes + 2 minutes = ~11 minutes

### API Costs

Each video upload and summarization counts toward Gemini API usage:
- Short video: 1 API call
- Long video: N chunks + 1 final summary = N+1 API calls

### Storage

- Chunk files are created in a subdirectory (e.g., `video_chunks/`)
- Original video is not modified
- Chunk files can be deleted after summarization

## Best Practices

1. **Use appropriate chunk size**: 30 minutes is safe for Gemini's 1-hour limit
2. **Pre-process videos**: Compress or reduce resolution if needed
3. **Monitor API usage**: Track costs for long video processing
4. **Keep chunks**: Don't delete chunks until summary is verified
5. **Handle failures gracefully**: Check return values and implement retries

## API Reference

### VideoSplitter

```python
VideoSplitter(max_duration_minutes: int = 30)
```

**Methods:**
- `get_video_duration(video_path: str) -> Optional[float]`
- `needs_splitting(video_path: str) -> bool`
- `split_video(video_path: str, output_dir: Optional[str] = None) -> List[str]`

### VideoSummarizer

```python
VideoSummarizer(
    api_key: Optional[str] = None,
    proxy_url: Optional[str] = None,
    max_chunk_duration: int = 30
)
```

**Methods:**
- `summarize_video(video_path: str, auto_split: bool = True) -> Optional[str]`
- `summarize_video_in_chunks(video_path: str) -> Optional[str]`

## License

This feature is part of the MediaCrawler project. See the main LICENSE file for details.
