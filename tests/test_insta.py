import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from datetime import datetime

from instagrapi.types import User, Location, UserShort, Media
from src.insta import post_album, get_lat_lng


class TestPostAlbum:
    """Test suite for post_album function"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Instagram client"""
        return Mock()
    
    @pytest.fixture
    def image_paths(self, tmp_path):
        """Create temporary image files for testing"""
        img1 = tmp_path / "image1.jpg"
        img2 = tmp_path / "image2.jpg"
        img1.write_text("fake image 1")
        img2.write_text("fake image 2")
        return [img1, img2]
    
    @pytest.fixture
    def mock_location(self):
        """Create a mock Instagram Location object"""
        loc = Mock(spec=Location)
        loc.pk = 123456789
        loc.name = "Paris, France"
        return loc
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock Instagram User object"""
        user = Mock(spec=User)
        user.pk = 987654321
        user.username = "leonardo"
        return user
    
    @pytest.fixture
    def mock_media(self):
        """Create a mock Instagram Media object"""
        media = Mock(spec=Media)
        media.pk = 111222333
        return media
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_with_tags_and_location(
        self, mock_get_lat_lng, mock_client, image_paths, 
        mock_user, mock_location, mock_media
    ):
        """Test posting an album with both tags and location"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)  # Paris coordinates
        mock_client.location_search.return_value = [mock_location]
        mock_client.user_info_by_username.return_value = mock_user
        mock_client.album_upload.return_value = mock_media
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert
        assert result is True
        assert mock_client.location_search.called
        assert mock_client.user_info_by_username.called
        assert mock_client.album_upload.called
        
        # Verify upload was called with correct parameters
        call_kwargs = mock_client.album_upload.call_args[1]
        assert call_kwargs["caption"] == "Test caption"
        assert len(call_kwargs["usertags"]) == 1
        assert call_kwargs["location"] == mock_location
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_without_location(
        self, mock_get_lat_lng, mock_client, image_paths, 
        mock_user, mock_media
    ):
        """Test posting an album when location search fails"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)
        mock_client.location_search.return_value = []  # No location found
        mock_client.user_info_by_username.return_value = mock_user
        mock_client.album_upload.return_value = mock_media
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert
        assert result is True
        assert mock_client.album_upload.called
        
        # Verify location was NOT passed
        call_kwargs = mock_client.album_upload.call_args[1]
        assert "location" not in call_kwargs or call_kwargs.get("location") is None
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_without_tags(
        self, mock_get_lat_lng, mock_client, image_paths, 
        mock_location, mock_media
    ):
        """Test posting an album when user tag lookup fails"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)
        mock_client.location_search.return_value = [mock_location]
        mock_client.user_info_by_username.side_effect = Exception("User not found")
        mock_client.album_upload.return_value = mock_media
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert
        assert result is True
        assert mock_client.album_upload.called
        
        # Verify tags were NOT passed
        call_kwargs = mock_client.album_upload.call_args[1]
        assert "usertags" not in call_kwargs or call_kwargs.get("usertags") == []
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_location_search_exception(
        self, mock_get_lat_lng, mock_client, image_paths, 
        mock_user, mock_media
    ):
        """Test posting when location search throws exception"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)
        mock_client.location_search.side_effect = Exception("API error")
        mock_client.user_info_by_username.return_value = mock_user
        mock_client.album_upload.return_value = mock_media
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert - should still succeed even if location fails
        assert result is True
        assert mock_client.album_upload.called
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_upload_fails(
        self, mock_get_lat_lng, mock_client, image_paths, 
        mock_location, mock_user
    ):
        """Test post failure when album_upload throws exception"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)
        mock_client.location_search.return_value = [mock_location]
        mock_client.user_info_by_username.return_value = mock_user
        mock_client.album_upload.side_effect = Exception("Upload failed")
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert
        assert result is False
        assert mock_client.album_upload.called
    
    @patch('src.insta.get_lat_lng')
    def test_post_album_calls_with_empty_tags_and_none_location(
        self, mock_get_lat_lng, mock_client, image_paths, mock_media
    ):
        """Test that album_upload is called only with caption and paths when location/tags fail"""
        # Setup
        mock_get_lat_lng.return_value = (48.8566, 2.3522)
        mock_client.location_search.return_value = []
        mock_client.user_info_by_username.side_effect = Exception("Not found")
        mock_client.album_upload.return_value = mock_media
        
        # Execute
        result = post_album(
            mock_client,
            image_paths,
            caption="Test caption",
            username="leonardo",
            location_str="Paris, France"
        )
        
        # Assert
        assert result is True
        call_kwargs = mock_client.album_upload.call_args[1]
        
        # Only these should be present
        assert "paths" in call_kwargs
        assert "caption" in call_kwargs
        assert call_kwargs.get("usertags") == [] or "usertags" not in call_kwargs
        assert "location" not in call_kwargs


class TestGetLatLng:
    """Test suite for get_lat_lng function"""
    
    @patch('src.insta.Nominatim')
    def test_get_lat_lng_valid_location(self, mock_nominatim_class):
        """Test getting coordinates for a valid location"""
        # Setup
        mock_geolocator = Mock()
        mock_nominatim_class.return_value = mock_geolocator
        mock_location = Mock()
        mock_location.latitude = 48.8566
        mock_location.longitude = 2.3522
        mock_geolocator.geocode.return_value = mock_location
        
        # Execute
        lat, lng = get_lat_lng("Paris, France")
        
        # Assert
        assert lat == 48.8566
        assert lng == 2.3522
    
    @patch('src.insta.Nominatim')
    def test_get_lat_lng_invalid_location(self, mock_nominatim_class):
        """Test that exception is raised for invalid location"""
        # Setup
        mock_geolocator = Mock()
        mock_nominatim_class.return_value = mock_geolocator
        mock_geolocator.geocode.return_value = None
        
        # Execute & Assert
        with pytest.raises(Exception, match="Could not geocode location"):
            get_lat_lng("Nonexistent Place XYZ")
