# Video Summarization Workflow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     VideoSummarizer                              │
│                    (tools/ai_agent.py)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Check Duration │
                    └─────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        ┌───────────────┐          ┌────────────────┐
        │  Short Video  │          │  Long Video    │
        │   (< 30 min)  │          │   (> 30 min)   │
        └───────────────┘          └────────────────┘
                │                           │
                │                           ▼
                │                  ┌────────────────┐
                │                  │ VideoSplitter  │
                │                  │ Split into     │
                │                  │ chunks         │
                │                  └────────────────┘
                │                           │
                │                           ▼
                │              ┌────────────────────────┐
                │              │  Chunk 1  │  Chunk 2   │
                │              │  Chunk 3  │  ...       │
                │              └────────────────────────┘
                │                           │
                ▼                           ▼
        ┌────────────────────────────────────────────┐
        │        Upload to Gemini API                │
        └────────────────────────────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────────┐
        │        AI Summarization Process            │
        └────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        ┌───────────────┐          ┌────────────────────┐
        │  Direct       │          │  Contextual        │
        │  Summary      │          │  Summarization     │
        └───────────────┘          └────────────────────┘
                │                           │
                │                           ▼
                │              ┌────────────────────────┐
                │              │  Summary 1 + Context   │
                │              │  Summary 2 + Context   │
                │              │  Summary 3 + Context   │
                │              └────────────────────────┘
                │                           │
                │                           ▼
                │              ┌────────────────────────┐
                │              │  Final Integration     │
                │              │  Combine all summaries │
                │              └────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Markdown Summary   │
                    │  ({video}_summary.md)│
                    └─────────────────────┘
```

## Process Flow Details

### 1. Short Video Processing (< 30 minutes)

```
Input Video → Check Duration → Upload to Gemini
                                    ↓
                            Generate Summary
                                    ↓
                              Save as .md
```

**Example**:
- Input: `tutorial.mp4` (15 minutes)
- Output: `tutorial_summary.md`
- Time: ~3 minutes
- API Calls: 1

### 2. Long Video Processing (> 30 minutes)

```
Input Video (90 min)
    ↓
Check Duration → Needs Split? YES
    ↓
Split into Chunks
    ├─ video_chunk_001.mp4 (0-30 min)
    ├─ video_chunk_002.mp4 (30-60 min)
    └─ video_chunk_003.mp4 (60-90 min)
    ↓
Process Chunk 1
    ↓ (upload + summarize)
    Summary 1: "This chunk covers introduction..."
    ↓
Process Chunk 2 (with context from Chunk 1)
    ↓ (upload + summarize with previous context)
    Summary 2: "Building on previous section..."
    ↓
Process Chunk 3 (with context from Chunk 1+2)
    ↓ (upload + summarize with previous context)
    Summary 3: "Concluding the topics from..."
    ↓
Generate Final Summary
    ↓ (integrate all summaries)
    Final: Complete coherent narrative
    ↓
Save as video_summary.md
```

**Example**:
- Input: `conference.mp4` (90 minutes)
- Chunks: 3 × 30 minutes
- Output: `conference_summary.md`
- Time: ~14 minutes
- API Calls: 4 (3 chunks + 1 final)

## Component Interactions

### VideoSplitter

```python
┌──────────────────────────────────────┐
│         VideoSplitter                │
├──────────────────────────────────────┤
│ + get_video_duration()               │
│   └─> Uses ffprobe                   │
│                                      │
│ + needs_splitting()                  │
│   └─> duration > max_duration        │
│                                      │
│ + split_video()                      │
│   └─> Uses ffmpeg -c copy            │
└──────────────────────────────────────┘
         │
         ▼
    ┌────────┐
    │ ffmpeg │ ← Fast codec copying, no re-encoding
    └────────┘
```

### VideoSummarizer

```python
┌────────────────────────────────────────────┐
│         VideoSummarizer                    │
├────────────────────────────────────────────┤
│ + summarize_video()                        │
│   ├─> Check if needs splitting            │
│   ├─> Call summarize_video_in_chunks()    │
│   └─> Or direct summarization             │
│                                            │
│ + summarize_video_in_chunks()             │
│   ├─> Split video using VideoSplitter     │
│   ├─> Process each chunk with context     │
│   └─> Generate final summary              │
│                                            │
│ + _summarize_single_chunk()               │
│   ├─> Upload chunk to Gemini             │
│   ├─> Include previous summary context    │
│   └─> Return chunk summary                │
│                                            │
│ + _generate_final_summary()               │
│   ├─> Combine all chunk summaries         │
│   └─> Generate coherent final summary     │
└────────────────────────────────────────────┘
         │
         ▼
    ┌──────────┐
    │ Gemini   │ ← AI summarization
    │   API    │
    └──────────┘
```

## Data Flow

### Single Chunk Processing

```
video_chunk_002.mp4
    │
    ├─ Upload to Gemini
    │      ↓
    │  File ID: files/abc123
    │      ↓
    ├─ Wait for Processing
    │      ↓
    │  Status: ACTIVE
    │      ↓
    └─ Generate Content with Prompt:
           "这是第 2 部分（共 3 部分）
            前面部分的总结：[Summary from Chunk 1]
            请总结本段内容..."
           ↓
       AI Response
           ↓
    Summary Text (Markdown)
           ↓
    Return to main process
```

### Context Propagation

```
Chunk 1: "Video introduces concept X..."
    ↓
    │ (passed as context)
    ↓
Chunk 2: "Building on X, demonstrates Y..."
    ↓
    │ (both summaries passed as context)
    ↓
Chunk 3: "Concludes with Z, relating to X and Y..."
    ↓
    │ (all summaries combined)
    ↓
Final: "Complete video covers X, Y, and Z in depth..."
```

## Error Handling

```
┌─────────────────┐
│  Start Process  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Check Dependencies  │
├─────────────────────┤
│ • ffmpeg available? │
│ • API key set?      │
│ • Video exists?     │
└────────┬────────────┘
         │
    ┌────┴────┐
    │  Error? │
    └────┬────┘
         │ No
         ▼
┌──────────────────┐
│  Split if Needed │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Success?│
    └────┬────┘
         │ Yes
         ▼
┌─────────────────────┐
│  Process Chunks     │
├─────────────────────┤
│ For each chunk:     │
│  • Try upload       │
│  • Try summarize    │
│  • On error: log    │
│    and continue     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Generate Final      │
│ (even if partial)   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Save Summary       │
└─────────────────────┘
```

## Performance Characteristics

### Time Complexity

```
Short Video (< 30 min):
    Upload Time + Processing Time + Download Time
    ≈ 2-5 minutes

Long Video (N chunks):
    (Upload + Process + Download) × N + Final Summary
    ≈ (3-5 minutes) × N + 2 minutes
    
Example (90 min video, 3 chunks):
    (4 min × 3) + 2 min = 14 minutes
```

### Space Complexity

```
Original Video: X MB
Chunks: ~X MB (no re-encoding)
Summary: ~5-50 KB (Markdown text)

Total Space: ~2X MB (during processing)
After Cleanup: X MB (original) + 5-50 KB (summary)
```

## API Usage Pattern

```
Short Video:
    1 API call: Upload + Summarize
    
Long Video (3 chunks):
    API Call 1: Upload Chunk 1 + Summarize
    API Call 2: Upload Chunk 2 + Summarize (with context)
    API Call 3: Upload Chunk 3 + Summarize (with context)
    API Call 4: Final Summary (text only, no upload)
    
    Total: 4 API calls
```

## Summary Output Structure

### Short Video

```markdown
# 视频一句话摘要
Brief summary

# 关键要点 (Key Takeaways)
- Point 1
- Point 2
- Point 3

# 详细内容
Detailed content...

# 后续思考
Follow-up thoughts...
```

### Long Video (Multi-Chunk)

```markdown
# 视频完整摘要
Complete integrated summary

# 关键要点 (Key Takeaways)
- Integrated point 1 (from all chunks)
- Integrated point 2
- Integrated point 3

# 详细内容
Coherent narrative combining all chunks...

# 总结与思考
Overall conclusions and insights...
```

## Integration Points

```
MediaCrawler Project
    │
    ├─ tools/
    │   ├─ ai_agent.py ← VideoSummarizer
    │   └─ video_splitter.py ← VideoSplitter
    │
    ├─ tests/
    │   ├─ test_ai_agent.py
    │   └─ test_video_splitter.py
    │
    ├─ examples/
    │   └─ video_summarization_demo.py
    │
    └─ docs/
        ├─ video_summarization.md
        └─ video_summarization_workflow.md (this file)
```

## Usage Patterns

### Pattern 1: Automatic (Recommended)

```python
from tools.ai_agent import VideoSummarizer

summarizer = VideoSummarizer()
summary_path = summarizer.summarize_video("video.mp4")
# Automatically handles splitting if needed
```

### Pattern 2: Manual Control

```python
from tools.video_splitter import VideoSplitter
from tools.ai_agent import VideoSummarizer

splitter = VideoSplitter(max_duration_minutes=30)
if splitter.needs_splitting("video.mp4"):
    chunks = splitter.split_video("video.mp4")
    summarizer = VideoSummarizer()
    summary = summarizer.summarize_video_in_chunks("video.mp4")
```

### Pattern 3: Custom Processing

```python
# Full control over each step
splitter = VideoSplitter()
chunks = splitter.split_video("video.mp4")

summarizer = VideoSummarizer()
summaries = []
prev = None

for i, chunk in enumerate(chunks):
    s = summarizer._summarize_single_chunk(
        chunk, i+1, len(chunks), prev
    )
    summaries.append(s)
    prev = s

final = summarizer._generate_final_summary(summaries, "video.mp4")
```
