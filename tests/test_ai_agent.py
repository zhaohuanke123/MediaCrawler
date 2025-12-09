# -*- coding: utf-8 -*-
"""
Tests for ai_agent module
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from tools.ai_agent import VideoSummarizer


class TestVideoSummarizer:
    """Test cases for VideoSummarizer class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock genai client"""
        client = Mock()
        client.files = Mock()
        client.models = Mock()
        return client
    
    @pytest.fixture
    def summarizer_with_key(self, mock_client):
        """Create VideoSummarizer with mocked API key"""
        with patch('tools.ai_agent.genai.Client', return_value=mock_client), \
             patch('tools.ai_agent.VideoSplitter'):
            summarizer = VideoSummarizer(api_key="test_key")
            summarizer.client = mock_client
            return summarizer
    
    @pytest.fixture
    def summarizer_no_key(self):
        """Create VideoSummarizer without API key"""
        with patch('tools.ai_agent.VideoSplitter'):
            summarizer = VideoSummarizer(api_key=None)
            return summarizer
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch('tools.ai_agent.genai.Client') as mock_client_class, \
             patch('tools.ai_agent.VideoSplitter'):
            summarizer = VideoSummarizer(api_key="test_key")
            
            assert summarizer.api_key == "test_key"
            assert summarizer.client is not None
            mock_client_class.assert_called_once()
    
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        with patch('os.getenv', return_value=None), \
             patch('tools.ai_agent.VideoSplitter'):
            summarizer = VideoSummarizer()
            
            assert summarizer.client is None
    
    def test_init_with_proxy(self):
        """Test initialization with proxy URL"""
        with patch('tools.ai_agent.genai.Client'), \
             patch('tools.ai_agent.VideoSplitter'), \
             patch('os.environ', {}) as mock_env:
            summarizer = VideoSummarizer(api_key="test_key", proxy_url="http://proxy:8080")
            
            assert summarizer.proxy_url == "http://proxy:8080"
    
    def test_init_custom_chunk_duration(self):
        """Test initialization with custom chunk duration"""
        with patch('tools.ai_agent.genai.Client'), \
             patch('tools.ai_agent.VideoSplitter') as mock_splitter:
            summarizer = VideoSummarizer(api_key="test_key", max_chunk_duration=45)
            
            mock_splitter.assert_called_once_with(max_duration_minutes=45)
    
    def test_wait_for_files_active_success(self, summarizer_with_key):
        """Test successful file processing wait"""
        mock_file = Mock()
        mock_file.state.name = "ACTIVE"
        
        # Should not raise exception
        summarizer_with_key.wait_for_files_active(mock_file)
    
    def test_wait_for_files_active_processing(self, summarizer_with_key):
        """Test file processing wait with transition"""
        mock_file = Mock()
        mock_file.state.name = "PROCESSING"
        mock_file.name = "test_file"
        
        # Mock client to return active file after first call
        active_file = Mock()
        active_file.state.name = "ACTIVE"
        summarizer_with_key.client.files.get.return_value = active_file
        
        with patch('time.sleep'):
            summarizer_with_key.wait_for_files_active(mock_file)
        
        summarizer_with_key.client.files.get.assert_called_with(name="test_file")
    
    def test_wait_for_files_active_failure(self, summarizer_with_key):
        """Test file processing failure"""
        mock_file = Mock()
        mock_file.state.name = "FAILED"
        
        with pytest.raises(Exception) as exc_info:
            summarizer_with_key.wait_for_files_active(mock_file)
        
        assert "File processing failed" in str(exc_info.value)
    
    def test_summarize_video_no_client(self, summarizer_no_key):
        """Test summarize_video without API client"""
        result = summarizer_no_key.summarize_video("/path/to/video.mp4")
        assert result is None
    
    @patch('pathlib.Path.exists')
    def test_summarize_video_file_not_found(self, mock_exists, summarizer_with_key):
        """Test summarize_video with non-existent file"""
        mock_exists.return_value = False
        
        result = summarizer_with_key.summarize_video("/path/to/nonexistent.mp4")
        assert result is None
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=MagicMock)
    @patch.object(VideoSummarizer, 'wait_for_files_active')
    def test_summarize_video_short_video_success(self, mock_wait, mock_open, 
                                                 mock_exists, summarizer_with_key):
        """Test successful summarization of short video"""
        mock_exists.return_value = True
        
        # Mock video splitter to indicate no splitting needed
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.needs_splitting.return_value = False
        
        # Mock file upload and response
        mock_video_file = Mock(name="test_video_file")
        summarizer_with_key.client.files.upload.return_value = mock_video_file
        
        mock_response = Mock()
        mock_response.text = "# Video Summary\n\nTest summary content"
        summarizer_with_key.client.models.generate_content.return_value = mock_response
        
        result = summarizer_with_key.summarize_video("/path/to/video.mp4")
        
        assert result is not None
        assert result.endswith("_summary.md")
        summarizer_with_key.client.files.upload.assert_called_once()
        mock_wait.assert_called_once()
        summarizer_with_key.client.models.generate_content.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch.object(VideoSummarizer, 'summarize_video_in_chunks')
    def test_summarize_video_long_video_auto_split(self, mock_summarize_chunks, 
                                                   mock_exists, summarizer_with_key):
        """Test automatic splitting for long video"""
        mock_exists.return_value = True
        
        # Mock video splitter to indicate splitting needed
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.needs_splitting.return_value = True
        
        mock_summarize_chunks.return_value = "/path/to/video_summary.md"
        
        result = summarizer_with_key.summarize_video("/path/to/long_video.mp4")
        
        assert result == "/path/to/video_summary.md"
        mock_summarize_chunks.assert_called_once_with("/path/to/long_video.mp4")
    
    @patch('pathlib.Path.exists')
    def test_summarize_video_auto_split_disabled(self, mock_exists, summarizer_with_key):
        """Test summarization with auto_split disabled"""
        mock_exists.return_value = True
        
        # Mock video splitter
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.needs_splitting.return_value = True
        
        # Mock upload and response
        mock_video_file = Mock(name="test_file")
        summarizer_with_key.client.files.upload.return_value = mock_video_file
        
        mock_response = Mock()
        mock_response.text = "Summary"
        summarizer_with_key.client.models.generate_content.return_value = mock_response
        
        with patch.object(summarizer_with_key, 'wait_for_files_active'), \
             patch('builtins.open', MagicMock()):
            result = summarizer_with_key.summarize_video("/path/to/video.mp4", auto_split=False)
        
        # Should proceed with normal summarization despite video being long
        assert result is not None
        summarizer_with_key.client.files.upload.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_summarize_video_in_chunks_no_client(self, mock_exists, summarizer_no_key):
        """Test summarize_video_in_chunks without API client"""
        mock_exists.return_value = True
        
        result = summarizer_no_key.summarize_video_in_chunks("/path/to/video.mp4")
        assert result is None
    
    @patch('pathlib.Path.exists')
    def test_summarize_video_in_chunks_file_not_found(self, mock_exists, summarizer_with_key):
        """Test summarize_video_in_chunks with non-existent file"""
        mock_exists.return_value = False
        
        result = summarizer_with_key.summarize_video_in_chunks("/path/to/nonexistent.mp4")
        assert result is None
    
    @patch('pathlib.Path.exists')
    def test_summarize_video_in_chunks_split_failure(self, mock_exists, summarizer_with_key):
        """Test summarize_video_in_chunks when splitting fails"""
        mock_exists.return_value = True
        
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.split_video.return_value = []
        
        result = summarizer_with_key.summarize_video_in_chunks("/path/to/video.mp4")
        assert result is None
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=MagicMock)
    @patch.object(VideoSummarizer, '_summarize_single_chunk')
    @patch.object(VideoSummarizer, '_generate_final_summary')
    def test_summarize_video_in_chunks_success(self, mock_final_summary, mock_single_chunk,
                                               mock_open, mock_exists, summarizer_with_key):
        """Test successful multi-chunk summarization"""
        mock_exists.return_value = True
        
        # Mock video splitting
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.split_video.return_value = [
            "/path/chunk1.mp4",
            "/path/chunk2.mp4",
            "/path/chunk3.mp4"
        ]
        
        # Mock chunk summarizations
        mock_single_chunk.side_effect = [
            "Summary of chunk 1",
            "Summary of chunk 2",
            "Summary of chunk 3"
        ]
        
        # Mock final summary generation
        mock_final_summary.return_value = "Complete video summary"
        
        result = summarizer_with_key.summarize_video_in_chunks("/path/to/video.mp4")
        
        assert result is not None
        assert result.endswith("_summary.md")
        assert mock_single_chunk.call_count == 3
        mock_final_summary.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=MagicMock)
    @patch.object(VideoSummarizer, '_summarize_single_chunk')
    @patch.object(VideoSummarizer, '_generate_final_summary')
    def test_summarize_video_in_chunks_partial_failure(self, mock_final_summary, 
                                                       mock_single_chunk, mock_open,
                                                       mock_exists, summarizer_with_key):
        """Test multi-chunk summarization with some chunk failures"""
        mock_exists.return_value = True
        
        # Mock video splitting
        summarizer_with_key.video_splitter = Mock()
        summarizer_with_key.video_splitter.split_video.return_value = [
            "/path/chunk1.mp4",
            "/path/chunk2.mp4",
            "/path/chunk3.mp4"
        ]
        
        # Mock chunk summarizations (second chunk fails)
        mock_single_chunk.side_effect = [
            "Summary of chunk 1",
            None,  # Failure
            "Summary of chunk 3"
        ]
        
        # Mock final summary generation
        mock_final_summary.return_value = "Partial video summary"
        
        result = summarizer_with_key.summarize_video_in_chunks("/path/to/video.mp4")
        
        assert result is not None
        # Should still generate summary from successful chunks
        mock_final_summary.assert_called_once_with(
            ["Summary of chunk 1", "Summary of chunk 3"],
            "video.mp4"
        )
    
    @patch('pathlib.Path.exists')
    @patch.object(VideoSummarizer, 'wait_for_files_active')
    def test_summarize_single_chunk_first_chunk(self, mock_wait, mock_exists, 
                                                summarizer_with_key):
        """Test summarizing first chunk (no previous context)"""
        mock_exists.return_value = True
        
        # Mock file upload and response
        mock_video_file = Mock(name="chunk_file")
        summarizer_with_key.client.files.upload.return_value = mock_video_file
        
        mock_response = Mock()
        mock_response.text = "Chunk 1 summary"
        summarizer_with_key.client.models.generate_content.return_value = mock_response
        
        result = summarizer_with_key._summarize_single_chunk(
            "/path/chunk1.mp4",
            chunk_index=1,
            total_chunks=3,
            previous_summary=None
        )
        
        assert result == "Chunk 1 summary"
        # Check that prompt is for first chunk
        call_args = summarizer_with_key.client.models.generate_content.call_args
        prompt = call_args[1]['contents'][1]
        assert "第 1 部分" in prompt
        assert "前面部分的总结" not in prompt
    
    @patch('pathlib.Path.exists')
    @patch.object(VideoSummarizer, 'wait_for_files_active')
    def test_summarize_single_chunk_continuation(self, mock_wait, mock_exists,
                                                 summarizer_with_key):
        """Test summarizing subsequent chunk with previous context"""
        mock_exists.return_value = True
        
        # Mock file upload and response
        mock_video_file = Mock(name="chunk_file")
        summarizer_with_key.client.files.upload.return_value = mock_video_file
        
        mock_response = Mock()
        mock_response.text = "Chunk 2 summary"
        summarizer_with_key.client.models.generate_content.return_value = mock_response
        
        result = summarizer_with_key._summarize_single_chunk(
            "/path/chunk2.mp4",
            chunk_index=2,
            total_chunks=3,
            previous_summary="Previous chunk summary"
        )
        
        assert result == "Chunk 2 summary"
        # Check that prompt includes previous summary
        call_args = summarizer_with_key.client.models.generate_content.call_args
        prompt = call_args[1]['contents'][1]
        assert "第 2 部分" in prompt
        assert "前面部分的总结" in prompt
        assert "Previous chunk summary" in prompt
    
    @patch('pathlib.Path.exists')
    def test_summarize_single_chunk_no_client(self, mock_exists, summarizer_no_key):
        """Test _summarize_single_chunk without API client"""
        mock_exists.return_value = True
        
        result = summarizer_no_key._summarize_single_chunk(
            "/path/chunk.mp4",
            chunk_index=1,
            total_chunks=1
        )
        assert result is None
    
    def test_generate_final_summary_success(self, summarizer_with_key):
        """Test generating final summary from chunks"""
        chunk_summaries = [
            "Summary of part 1",
            "Summary of part 2",
            "Summary of part 3"
        ]
        
        mock_response = Mock()
        mock_response.text = "Complete integrated summary"
        summarizer_with_key.client.models.generate_content.return_value = mock_response
        
        result = summarizer_with_key._generate_final_summary(chunk_summaries, "test_video.mp4")
        
        assert result == "Complete integrated summary"
        summarizer_with_key.client.models.generate_content.assert_called_once()
        
        # Check that all chunk summaries are in the prompt
        call_args = summarizer_with_key.client.models.generate_content.call_args
        prompt = call_args[1]['contents'][0]
        for summary in chunk_summaries:
            assert summary in prompt
    
    def test_generate_final_summary_no_client(self, summarizer_no_key):
        """Test _generate_final_summary without API client"""
        chunk_summaries = ["Summary 1", "Summary 2"]
        
        result = summarizer_no_key._generate_final_summary(chunk_summaries, "video.mp4")
        
        # Should return concatenated summaries as fallback
        assert "Summary 1" in result
        assert "Summary 2" in result
        assert "---" in result
    
    def test_generate_final_summary_api_error(self, summarizer_with_key):
        """Test _generate_final_summary when API call fails"""
        chunk_summaries = ["Summary 1", "Summary 2"]
        
        summarizer_with_key.client.models.generate_content.side_effect = Exception("API Error")
        
        result = summarizer_with_key._generate_final_summary(chunk_summaries, "video.mp4")
        
        # Should fall back to concatenated summaries
        assert "Summary 1" in result
        assert "Summary 2" in result
