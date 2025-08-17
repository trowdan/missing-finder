import pytest
from unittest.mock import Mock, patch
from homeward.models.case import MissingPersonCase, CaseStatus, CasePriority, Location
from datetime import datetime


class TestCaseDetailPage:
    """Test cases for the case detail page"""
    
    @patch('homeward.ui.pages.case_detail.ui')
    @patch('homeward.ui.pages.case_detail.create_footer')
    def test_create_case_detail_page_with_mock_case(self, mock_footer, mock_ui):
        """Test case detail page creation with mock case data"""
        from homeward.ui.pages.case_detail import create_case_detail_page
        
        # Setup mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.grid.return_value.__enter__ = Mock()
        mock_ui.grid.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value.enable = Mock()
        
        mock_data_service = Mock()
        mock_data_service.get_case_by_id.return_value = None  # Force mock case creation
        
        mock_config = Mock()
        mock_config.version = "1.0.0"
        mock_callback = Mock()
        
        mock_video_analysis_service = Mock()
        
        create_case_detail_page("MP001", mock_data_service, mock_video_analysis_service, mock_config, mock_callback)
        
        # Verify dark mode is enabled
        mock_ui.dark_mode().enable.assert_called_once()
        
        # Verify footer is created
        mock_footer.assert_called_once_with("1.0.0")
        
        # Verify UI structure
        assert mock_ui.column.call_count >= 5  # Multiple columns for layout
        assert mock_ui.card.call_count >= 5    # Multiple cards for sections
        assert mock_ui.label.call_count >= 10  # Multiple labels for content
        assert mock_ui.button.call_count >= 5  # Action buttons
    
    @patch('homeward.ui.pages.case_detail.ui')
    @patch('homeward.ui.pages.case_detail.create_footer')
    def test_create_case_detail_page_with_real_case(self, mock_footer, mock_ui):
        """Test case detail page creation with real case data"""
        from homeward.ui.pages.case_detail import create_case_detail_page
        
        # Setup mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.grid.return_value.__enter__ = Mock()
        mock_ui.grid.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value.enable = Mock()
        
        # Create real case data
        case = MissingPersonCase(
            id="MP123",
            name="Jane",
            surname="Smith",
            age=25,
            gender="Female",
            last_seen_date=datetime(2023, 12, 5, 16, 30),
            last_seen_location=Location(
                address="456 Oak Avenue",
                city="Vancouver",
                country="Canada",
                postal_code="V6B 1A1",
                latitude=49.2827,
                longitude=-123.1207
            ),
            status=CaseStatus.ACTIVE,
            description="Missing after work shift ended.",
            photo_url=None,
            created_date=datetime(2023, 12, 5, 20, 0),
            priority=CasePriority.HIGH
        )
        
        mock_data_service = Mock()
        mock_data_service.get_case_by_id.return_value = case
        
        mock_config = Mock()
        mock_config.version = "2.0.0"
        mock_callback = Mock()
        
        mock_video_analysis_service = Mock()
        
        create_case_detail_page("MP123", mock_data_service, mock_video_analysis_service, mock_config, mock_callback)
        
        # Verify data service was called
        mock_data_service.get_case_by_id.assert_called_once_with("MP123")
        
        # Verify footer is created with correct version
        mock_footer.assert_called_once_with("2.0.0")
        
        # Verify UI structure
        assert mock_ui.column.called
        assert mock_ui.card.called
        assert mock_ui.label.called


class TestCaseDetailHelpers:
    """Test helper functions for case detail page"""
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_handle_link_sighting(self, mock_ui):
        """Test link sighting handler"""
        from homeward.ui.pages.case_detail import handle_link_sighting
        
        handle_link_sighting("MP001")
        mock_ui.notify.assert_called_once_with('Link sighting to case MP001', type='info')
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_handle_analyze_video(self, mock_ui):
        """Test analyze video handler"""
        from homeward.ui.pages.case_detail import handle_analyze_video
        from homeward.models.case import MissingPersonCase, CaseStatus, CasePriority, Location
        from datetime import datetime
        
        # Create a mock case
        case = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            age=30,
            gender="Male",
            last_seen_date=datetime(2023, 12, 1, 14, 30),
            last_seen_location=Location(
                address="123 Main St",
                city="Toronto",
                country="Canada",
                postal_code="M5V 3A8",
                latitude=43.6532,
                longitude=-79.3832
            ),
            status=CaseStatus.ACTIVE,
            description="Missing person",
            photo_url=None,
            created_date=datetime(2023, 12, 1, 18, 0),
            priority=CasePriority.HIGH
        )
        
        mock_video_analysis_service = Mock()
        mock_video_analysis_service.analyze_videos.return_value = []  # Empty results
        
        mock_results_container = Mock()
        mock_results_container.clear = Mock()
        mock_results_container.__enter__ = Mock(return_value=mock_results_container)
        mock_results_container.__exit__ = Mock(return_value=None)
        
        handle_analyze_video("MP001", mock_video_analysis_service, case, mock_results_container)
        
        # Verify notifications - should have initial info and final warning
        assert mock_ui.notify.call_count == 2
        
        # Check first call (initial notification)
        first_call = mock_ui.notify.call_args_list[0]
        assert first_call == (('🤖 Starting AI-powered video analysis for case MP001...',), {'type': 'info'})
        
        # Check second call (no results warning)
        second_call = mock_ui.notify.call_args_list[1]
        assert second_call == (('No matches found in the specified criteria',), {'type': 'warning'})
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_handle_edit_case(self, mock_ui):
        """Test edit case handler"""
        from homeward.ui.pages.case_detail import handle_edit_case
        
        handle_edit_case("MP001")
        mock_ui.notify.assert_called_once_with('Edit case MP001', type='info')
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_handle_resolve_case(self, mock_ui):
        """Test resolve case handler"""
        from homeward.ui.pages.case_detail import handle_resolve_case
        
        handle_resolve_case("MP001")
        mock_ui.notify.assert_called_once_with('Mark case MP001 as resolved', type='positive')
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_handle_view_sighting(self, mock_ui):
        """Test view sighting handler"""
        from homeward.ui.pages.case_detail import handle_view_sighting
        
        sighting = {'location': 'Union Station', 'date': '2023-12-02 10:30'}
        handle_view_sighting(sighting)
        mock_ui.notify.assert_called_once_with('View sighting at Union Station', type='info')


class TestCaseDetailComponents:
    """Test case detail page components"""
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_create_info_field(self, mock_ui):
        """Test info field creation"""
        from homeward.ui.pages.case_detail import create_info_field
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        
        create_info_field("Test Label", "Test Value")
        
        # Verify column is created
        mock_ui.column.assert_called_once()
        
        # Verify labels are created with correct styling
        assert mock_ui.label.call_count == 2
        
        # Check first label call (field label)
        first_call = mock_ui.label.call_args_list[0]
        assert first_call[0][0] == "Test Label"
        
        # Check second label call (field value)
        second_call = mock_ui.label.call_args_list[1]
        assert second_call[0][0] == "Test Value"
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_create_sightings_table_with_data(self, mock_ui):
        """Test sightings table creation with data"""
        from homeward.ui.pages.case_detail import create_sightings_table
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.element.return_value.__enter__ = Mock()
        mock_ui.element.return_value.__exit__ = Mock()
        
        create_sightings_table()
        
        # Verify table structure is created
        assert mock_ui.element.called  # div elements for grid layout
        assert mock_ui.label.called     # table headers and content
        assert mock_ui.button.called    # action buttons
    
    @patch('homeward.ui.pages.case_detail.ui')
    def test_create_video_analysis_section(self, mock_ui):
        """Test video analysis section creation"""
        from homeward.ui.pages.case_detail import create_video_analysis_section
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.input.return_value = Mock()
        mock_ui.number.return_value = Mock()
        mock_ui.select.return_value = Mock()
        
        create_video_analysis_section()
        
        # Verify form elements are created
        assert mock_ui.column.called
        assert mock_ui.row.called
        assert mock_ui.input.called  # Date inputs
        assert mock_ui.number.called  # Radius input
        assert mock_ui.select.called  # Dropdown selections
        assert mock_ui.label.called   # Labels