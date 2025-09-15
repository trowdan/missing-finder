from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from homeward.models.case import CasePriority, CaseStatus, Location, MissingPersonCase


class TestCaseDetailPage:
    """Test cases for the case detail page"""

    @patch("homeward.ui.pages.case_detail.ui")
    def test_create_case_detail_page_with_no_case_found(self, mock_ui):
        """Test case detail page creation when case is not found"""
        from homeward.ui.pages.case_detail import create_case_detail_page

        # Setup mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value.enable = Mock()

        mock_data_service = Mock()
        mock_data_service.get_case_by_id.return_value = None  # Case not found

        mock_config = Mock()
        mock_config.version = "1.0.0"
        mock_callback = Mock()

        mock_video_analysis_service = Mock()

        create_case_detail_page(
            "MP001",
            mock_data_service,
            mock_video_analysis_service,
            mock_config,
            mock_callback,
        )

        # Verify dark mode is enabled
        mock_ui.dark_mode().enable.assert_called_once()

        # Verify that we get a case not found page
        assert mock_ui.column.call_count >= 2  # Layout columns
        assert mock_ui.label.call_count >= 3  # Header, error message, and description
        assert mock_ui.button.call_count >= 1  # Back to dashboard button

    @patch("homeward.ui.pages.case_detail.ui")
    @patch("homeward.ui.pages.case_detail.create_footer")
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
            date_of_birth=datetime(1999, 3, 10),
            gender="Female",
            last_seen_date=datetime(2023, 12, 5, 16, 30),
            last_seen_location=Location(
                address="456 Oak Avenue",
                city="Vancouver",
                country="Canada",
                postal_code="V6B 1A1",
                latitude=49.2827,
                longitude=-123.1207,
            ),
            status=CaseStatus.ACTIVE,
            circumstances="Missing after work shift ended",
            reporter_name="John Smith",
            reporter_phone="+1 555 0123",
            relationship="Husband",
            description="Missing after work shift ended.",
            photo_url=None,
            created_date=datetime(2023, 12, 5, 20, 0),
            priority=CasePriority.HIGH,
        )

        mock_data_service = Mock()
        mock_data_service.get_case_by_id.return_value = case

        mock_config = Mock()
        mock_config.version = "2.0.0"
        mock_callback = Mock()

        mock_video_analysis_service = Mock()

        create_case_detail_page(
            "MP123",
            mock_data_service,
            mock_video_analysis_service,
            mock_config,
            mock_callback,
        )

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

    @patch("homeward.ui.pages.case_detail.ui")
    def test_open_link_sighting_modal(self, mock_ui):
        """Test link sighting modal opening"""
        from homeward.services.mock_data_service import MockDataService
        from homeward.ui.pages.case_detail import open_link_sighting_modal

        # Setup mocks - create comprehensive UI mock
        mock_data_service = MockDataService()

        # Mock all UI components used in the function
        mock_dialog = MagicMock()
        mock_dialog.__enter__ = MagicMock(return_value=mock_dialog)
        mock_dialog.__exit__ = MagicMock(return_value=None)

        mock_ui.dialog.return_value = mock_dialog
        mock_ui.card.return_value.__enter__ = MagicMock()
        mock_ui.card.return_value.__exit__ = MagicMock()
        mock_ui.row.return_value.__enter__ = MagicMock()
        mock_ui.row.return_value.__exit__ = MagicMock()
        mock_ui.column.return_value.__enter__ = MagicMock()
        mock_ui.column.return_value.__exit__ = MagicMock()

        # Call the function - should not raise an error
        try:
            open_link_sighting_modal("MP001", mock_data_service)
            # If we get here without exceptions, the basic functionality works
            assert True
        except Exception as e:
            # If there's an exception, fail the test
            raise AssertionError(
                f"open_link_sighting_modal raised exception: {e}"
            ) from e

        # Verify dialog was created
        mock_ui.dialog.assert_called_once()

    @patch("homeward.ui.pages.case_detail.ui")
    def test_handle_analyze_video(self, mock_ui):
        """Test analyze video handler"""
        from datetime import datetime

        from homeward.models.case import (
            CasePriority,
            CaseStatus,
            Location,
            MissingPersonCase,
        )
        from homeward.ui.pages.case_detail import handle_analyze_video

        # Create a mock case
        case = MissingPersonCase(
            id="MP001",
            name="John",
            surname="Doe",
            date_of_birth=datetime(1994, 1, 15),
            gender="Male",
            last_seen_date=datetime(2023, 12, 1, 14, 30),
            last_seen_location=Location(
                address="123 Main St",
                city="Toronto",
                country="Canada",
                postal_code="M5V 3A8",
                latitude=43.6532,
                longitude=-79.3832,
            ),
            status=CaseStatus.ACTIVE,
            circumstances="Test missing person",
            reporter_name="Jane Doe",
            reporter_phone="+1 416 555 0123",
            relationship="Wife",
            description="Missing person",
            photo_url=None,
            created_date=datetime(2023, 12, 1, 18, 0),
            priority=CasePriority.HIGH,
        )

        mock_video_analysis_service = Mock()
        mock_video_analysis_service.analyze_videos.return_value = []  # Empty results

        mock_results_container = Mock()
        mock_results_container.clear = Mock()
        mock_results_container.__enter__ = Mock(return_value=mock_results_container)
        mock_results_container.__exit__ = Mock(return_value=None)

        handle_analyze_video(
            "MP001", mock_video_analysis_service, case, mock_results_container
        )

        # Verify notifications - should have initial info and final warning
        assert mock_ui.notify.call_count == 2

        # Check first call (initial notification)
        first_call = mock_ui.notify.call_args_list[0]
        assert first_call == (
            ("🤖 Starting AI-powered video analysis for case MP001...",),
            {"type": "info"},
        )

        # Check second call (no results warning)
        second_call = mock_ui.notify.call_args_list[1]
        assert second_call == (
            ("No matches found in the specified criteria",),
            {"type": "warning"},
        )

    @patch("homeward.ui.pages.case_detail.ui")
    def test_handle_edit_case(self, mock_ui):
        """Test edit case handler"""
        from homeward.services.mock_data_service import MockDataService
        from homeward.ui.pages.case_detail import handle_edit_case

        mock_data_service = MockDataService()
        case = mock_data_service.get_case_by_id("MP001")

        # Mock dialog components
        mock_dialog = MagicMock()
        mock_dialog.__enter__ = MagicMock(return_value=mock_dialog)
        mock_dialog.__exit__ = MagicMock(return_value=None)
        mock_ui.dialog.return_value = mock_dialog

        # Mock form components
        mock_ui.column.return_value.__enter__ = MagicMock()
        mock_ui.column.return_value.__exit__ = MagicMock()

        handle_edit_case("MP001", case, mock_data_service)

        # Verify dialog was opened
        mock_ui.dialog.assert_called_once()

    @patch("homeward.ui.pages.case_detail.ui")
    def test_handle_resolve_case(self, mock_ui):
        """Test resolve case handler"""
        from homeward.ui.pages.case_detail import handle_resolve_case

        handle_resolve_case("MP001")
        mock_ui.notify.assert_called_once_with(
            "Mark case MP001 as resolved", type="positive"
        )

    @patch("homeward.ui.pages.case_detail.ui")
    def test_handle_view_sighting(self, mock_ui):
        """Test view sighting handler"""
        from homeward.ui.pages.case_detail import handle_view_sighting

        sighting = {"location": "Union Station", "date": "2023-12-02 10:30"}
        handle_view_sighting(sighting)
        mock_ui.notify.assert_called_once_with(
            "View sighting at Union Station", type="info"
        )


class TestCaseDetailComponents:
    """Test case detail page components"""

    @patch("homeward.ui.pages.case_detail.ui")
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

    @patch("homeward.ui.pages.case_detail.ui")
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
        assert mock_ui.label.called  # table headers and content
        assert mock_ui.button.called  # action buttons

    @patch("homeward.ui.pages.case_detail.ui")
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
        assert mock_ui.label.called  # Labels
