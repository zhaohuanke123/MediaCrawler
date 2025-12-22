from dataclasses import dataclass

@dataclass
class VideoSummaryPrompts:
    """
    Configuration for video summarization prompts.
    """
    
    # Prompt for the first chunk of a split video
    chunk_first: str = """
    请作为一名专业的笔记整理员，观看这段视频并进行详细总结。
    注意：这是一个长视频的第 {chunk_index} 部分（共 {total_chunks} 部分）。
    
    输出格式要求为 Markdown，包含以下部分：
    1. **本段摘要**：简明扼要地总结本段内容。
    2. **关键要点**：使用列表形式列出本段的关键信息。
    3. **详细内容**：按时间逻辑或主题逻辑分段落描述本段内容。
    
    请用中文输出。
    """

    # Prompt for subsequent chunks of a split video
    chunk_continuation: str = """
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

    # Prompt for generating the final summary from chunk summaries
    final_summary: str = """
    请作为一名专业的笔记整理员，基于以下各部分的总结，生成一个完整、连贯的视频总结。
    
    视频文件名：{original_video_name}
    
    各部分总结：
    {combined_text}
    
    请整合所有内容，输出格式要求为 Markdown，包含以下部分：
    1. **视频完整摘要**：简明扼要地概括整个视频的核心内容。
    2. **关键要点 (Key Takeaways)**：整合所有部分的关键信息, 包含时间线，使用列表形式。
    3. **详细内容**：按逻辑顺序整合所有部分的内容，形成连贯的叙述。
    4. **总结与思考**：基于完整视频内容的总结性思考和启发。
    
    请用中文输出。
    由于系统限制，请不要使用 # 标题语法，改用 **加粗** 来表示小标题。不要使用表格。
    """

    # Prompt for a single (short) video
    single_video: str = """
    请作为一名专业的笔记整理员，观看这段视频并进行详细总结。
    输出格式要求为 Markdown，包含以下部分：
    1. **视频一句话摘要**：简明扼要。
    2. **关键要点 (Key Takeaways)**：使用列表形式。
    3. **详细内容**：按时间逻辑或主题逻辑分段落描述，如果视频中有明确的章节，请列出。
    4. **后续思考**：基于视频内容延伸的一个启发。
    
    请用中文输出。
    由于系统限制，请不要使用 # 标题语法，改用 **加粗** 来表示小标题。不要使用表格。
    """
