# -*- coding: utf-8 -*-
"""
Tests for video_splitter module
"""
import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tools.video_splitter import VideoSplitter


class TestVideoSplitter:
    """Test cases for VideoSplitter class"""
    
    @pytest.fixture
    def video_splitter(self):
        """Create a VideoSplitter instance with 1-minute chunks for testing"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=True):
            return VideoSplitter(max_duration_minutes=1)
    
    @pytest.fixture
    def video_splitter_30min(self):
        """Create a VideoSplitter instance with default 30-minute chunks"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=True):
            return VideoSplitter(max_duration_minutes=30)
    
    def test_init_default_duration(self):
        """Test initialization with default duration"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=True):
            splitter = VideoSplitter()
            assert splitter.max_duration_seconds == 30 * 60
            assert splitter.ffmpeg_available is True
    
    def test_init_custom_duration(self):
        """Test initialization with custom duration"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=True):
            splitter = VideoSplitter(max_duration_minutes=45)
            assert splitter.max_duration_seconds == 45 * 60
            assert splitter.ffmpeg_available is True
    
    def test_init_ffmpeg_not_available(self):
        """Test initialization when ffmpeg is not available"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=False):
            splitter = VideoSplitter()
            assert splitter.ffmpeg_available is False
    
    def test_get_video_duration_no_ffmpeg(self):
        """Test get_video_duration when ffmpeg is not available"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=False):
            splitter = VideoSplitter()
            duration = splitter.get_video_duration("/path/to/video.mp4")
            assert duration is None
    
    def test_split_video_no_ffmpeg(self):
        """Test split_video when ffmpeg is not available"""
        with patch.object(VideoSplitter, '_check_ffmpeg', return_value=False):
            splitter = VideoSplitter()
            result = splitter.split_video("/path/to/video.mp4")
            assert result == []
    
    @patch('subprocess.run')
    def test_get_video_duration_success(self, mock_run, video_splitter):
        """Test successful video duration retrieval"""
        # Mock ffprobe output
        mock_run.return_value = Mock(stdout="120.5\n", returncode=0)
        
        duration = video_splitter.get_video_duration("/path/to/video.mp4")
        
        assert duration == 120.5
        mock_run.assert_called_once()
        assert "ffprobe" in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_get_video_duration_failure(self, mock_run, video_splitter):
        """Test video duration retrieval failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffprobe')
        
        duration = video_splitter.get_video_duration("/path/to/video.mp4")
        
        assert duration is None
    
    @patch('subprocess.run')
    def test_get_video_duration_invalid_output(self, mock_run, video_splitter):
        """Test video duration retrieval with invalid output"""
        mock_run.return_value = Mock(stdout="invalid\n", returncode=0)
        
        duration = video_splitter.get_video_duration("/path/to/video.mp4")
        
        assert duration is None
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_needs_splitting_short_video(self, mock_get_duration, video_splitter):
        """Test needs_splitting returns False for short video"""
        mock_get_duration.return_value = 30.0  # 30 seconds
        
        result = video_splitter.needs_splitting("/path/to/video.mp4")
        
        assert result is False
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_needs_splitting_long_video(self, mock_get_duration, video_splitter):
        """Test needs_splitting returns True for long video"""
        mock_get_duration.return_value = 120.0  # 2 minutes
        
        result = video_splitter.needs_splitting("/path/to/video.mp4")
        
        assert result is True
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_needs_splitting_exact_duration(self, mock_get_duration, video_splitter):
        """Test needs_splitting with video exactly at limit"""
        mock_get_duration.return_value = 60.0  # Exactly 1 minute
        
        result = video_splitter.needs_splitting("/path/to/video.mp4")
        
        assert result is False
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_needs_splitting_no_duration(self, mock_get_duration, video_splitter):
        """Test needs_splitting when duration cannot be determined"""
        mock_get_duration.return_value = None
        
        result = video_splitter.needs_splitting("/path/to/video.mp4")
        
        assert result is False
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_split_video_short_video(self, mock_mkdir, mock_exists, mock_get_duration, 
                                     mock_run, video_splitter):
        """Test split_video with short video that doesn't need splitting"""
        mock_exists.return_value = True
        mock_get_duration.return_value = 30.0  # 30 seconds
        
        result = video_splitter.split_video("/path/to/video.mp4")
        
        assert result == ["/path/to/video.mp4"]
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_split_video_long_video(self, mock_mkdir, mock_exists, mock_get_duration, 
                                    mock_run, video_splitter):
        """Test split_video with long video that needs splitting"""
        mock_exists.return_value = True
        mock_get_duration.return_value = 150.0  # 2.5 minutes = 3 chunks needed
        mock_run.return_value = Mock(returncode=0)
        
        result = video_splitter.split_video("/path/to/video.mp4")
        
        # Should create 3 chunks
        assert len(result) == 3
        assert mock_run.call_count == 3
        
        # Check that ffmpeg was called with correct parameters
        for call in mock_run.call_args_list:
            args = call[0][0]
            assert "ffmpeg" in args
            assert "-y" in args
            assert "-c" in args
            assert "copy" in args
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    def test_split_video_file_not_found(self, mock_exists, mock_get_duration, 
                                        mock_run, video_splitter):
        """Test split_video with non-existent file"""
        mock_exists.return_value = False
        
        result = video_splitter.split_video("/path/to/nonexistent.mp4")
        
        assert result == []
        mock_get_duration.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    def test_split_video_duration_unknown(self, mock_exists, mock_get_duration, 
                                          mock_run, video_splitter):
        """Test split_video when duration cannot be determined"""
        mock_exists.return_value = True
        mock_get_duration.return_value = None
        
        result = video_splitter.split_video("/path/to/video.mp4")
        
        assert result == []
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_split_video_custom_output_dir(self, mock_mkdir, mock_exists, 
                                           mock_get_duration, mock_run, video_splitter):
        """Test split_video with custom output directory"""
        mock_exists.return_value = True
        mock_get_duration.return_value = 150.0
        mock_run.return_value = Mock(returncode=0)
        
        result = video_splitter.split_video("/path/to/video.mp4", 
                                           output_dir="/custom/output")
        
        assert len(result) == 3
        # Check that output paths use custom directory
        for path in result:
            assert path.startswith("/custom/output")
        
        mock_mkdir.assert_called_once()
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_split_video_ffmpeg_error(self, mock_mkdir, mock_exists, 
                                      mock_get_duration, mock_run, video_splitter):
        """Test split_video when ffmpeg fails"""
        mock_exists.return_value = True
        mock_get_duration.return_value = 150.0
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg')
        
        result = video_splitter.split_video("/path/to/video.mp4")
        
        # Should return empty list when all chunks fail
        assert result == []
    
    @patch('subprocess.run')
    @patch.object(VideoSplitter, 'get_video_duration')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_split_video_partial_success(self, mock_mkdir, mock_exists, 
                                         mock_get_duration, mock_run, video_splitter):
        """Test split_video when some chunks succeed and some fail"""
        mock_exists.return_value = True
        mock_get_duration.return_value = 150.0
        
        # First call succeeds, second fails, third succeeds
        mock_run.side_effect = [
            Mock(returncode=0),
            subprocess.CalledProcessError(1, 'ffmpeg'),
            Mock(returncode=0)
        ]
        
        result = video_splitter.split_video("/path/to/video.mp4")
        
        # Should return 2 successful chunks
        assert len(result) == 2
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_split_video_30min_chunks(self, mock_get_duration, video_splitter_30min):
        """Test splitting with 30-minute chunk size"""
        # 90 minutes = 3 chunks of 30 minutes
        mock_get_duration.return_value = 90 * 60
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('subprocess.run', return_value=Mock(returncode=0)):
            
            result = video_splitter_30min.split_video("/path/to/long_video.mp4")
            
            assert len(result) == 3
    
    @patch.object(VideoSplitter, 'get_video_duration')
    def test_split_video_70min_video(self, mock_get_duration, video_splitter_30min):
        """Test splitting 70-minute video (edge case - requires 3 chunks)"""
        # 70 minutes requires 3 chunks (30 + 30 + 10)
        mock_get_duration.return_value = 70 * 60
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('subprocess.run', return_value=Mock(returncode=0)):
            
            result = video_splitter_30min.split_video("/path/to/video.mp4")
            
            assert len(result) == 3
