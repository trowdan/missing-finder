from unittest.mock import Mock, patch

from homeward.config import AppConfig, DataSource


class TestNewSightingPage:
    """Test cases for the new sighting page"""

    @patch("homeward.ui.pages.new_sighting.ui")
    @patch("homeward.ui.pages.new_sighting.create_footer")
    def test_create_new_sighting_page(self, mock_footer, mock_ui):
        """Test new sighting page creation"""
        from homeward.ui.pages.new_sighting import create_new_sighting_page

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
        mock_config = Mock()
        mock_config.version = "1.0.0"
        mock_callback = Mock()

        create_new_sighting_page(mock_data_service, mock_config, mock_callback)

        # Verify dark mode is enabled
        mock_ui.dark_mode().enable.assert_called_once()

        # Verify footer is created
        mock_footer.assert_called_once_with("1.0.0")

        # Verify UI structure
        assert mock_ui.column.call_count >= 8  # Multiple columns for layout
        assert mock_ui.card.call_count >= 5  # Multiple cards for sections
        assert mock_ui.label.call_count >= 10  # Multiple labels for content
        assert mock_ui.button.call_count >= 3  # Action buttons

    @patch("homeward.ui.pages.new_sighting.GeocodingService")
    @patch("homeward.ui.pages.new_sighting.ui")
    def test_handle_form_submission_valid_data(self, mock_ui, mock_geocoding_service):
        """Test form submission handler with valid data"""
        from homeward.ui.pages.new_sighting import handle_form_submission

        # Create mock form data with all required fields
        mock_field = Mock()
        mock_field.value = "Test Value"

        # Mock date field
        mock_date_field = Mock()
        mock_date_field.value = "2024-01-15"

        form_data = {
            "reporter_name": mock_field,
            "sighting_date": mock_date_field,
            "sighting_address": mock_field,
            "sighting_city": mock_field,
            "sighting_country": mock_field,
            "additional_details": mock_field,
            "confidence": mock_field,
            "source_type": mock_field,
        }

        mock_data_service = Mock()
        mock_data_service.create_sighting.return_value = "test-sighting-id"

        mock_config = Mock()

        # Mock geocoding service
        mock_geocoding_instance = Mock()
        mock_geocoding_instance.geocode_address.return_value = None  # No coordinates found
        mock_geocoding_service.return_value = mock_geocoding_instance

        handle_form_submission(form_data, mock_data_service, mock_config)

        # Verify data service is called
        mock_data_service.create_sighting.assert_called_once()

        # Verify success notification
        mock_ui.notify.assert_called_with(
            "✅ Sighting report submitted successfully!", type="positive"
        )

        # Verify timer is set for redirect
        mock_ui.timer.assert_called_once()

    @patch("homeward.ui.pages.new_sighting.ui")
    def test_handle_form_submission_missing_required(self, mock_ui):
        """Test form submission handler with missing required fields"""
        from homeward.ui.pages.new_sighting import handle_form_submission

        # Create mock form data missing required fields
        mock_field = Mock()
        mock_field.value = ""

        form_data = {
            "reporter_name": mock_field,  # Empty value
            "sighting_date": mock_field,
            "additional_details": mock_field,
        }

        mock_data_service = Mock()
        mock_config = Mock()

        handle_form_submission(form_data, mock_data_service, mock_config)

        # Verify error notification for missing fields
        mock_ui.notify.assert_called_with(
            "Please fill in the required fields: Sighting Date, Sighting Address, Sighting City, Country, Sighting Description, Confidence Level, Source Type", type="negative"
        )


class TestNewSightingPageIntegration:
    """Integration tests for new sighting page"""

    @patch("homeward.ui.pages.new_sighting.ui")
    @patch("homeward.ui.pages.new_sighting.create_footer")
    def test_complete_sighting_page_workflow(self, mock_footer, mock_ui):
        """Test complete workflow of new sighting page"""
        from homeward.ui.pages.new_sighting import create_new_sighting_page

        # Setup all necessary mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.grid.return_value.__enter__ = Mock()
        mock_ui.grid.return_value.__exit__ = Mock()
        mock_ui.element.return_value.__enter__ = Mock()
        mock_ui.element.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value.enable = Mock()

        # Create realistic config
        config = AppConfig(data_source=DataSource.MOCK, version="1.0.0")

        mock_data_service = Mock()
        mock_callback = Mock()

        # Test page creation
        create_new_sighting_page(mock_data_service, config, mock_callback)

        # Verify all major sections are created
        assert mock_ui.card.call_count >= 5  # All form sections
        assert mock_ui.icon.call_count >= 5  # Section icons

        # Verify form elements are created
        assert mock_ui.input.call_count >= 8  # Text inputs (including date/time)
        assert mock_ui.textarea.call_count >= 3  # Textareas
        assert mock_ui.select.call_count >= 2  # Dropdowns
        assert mock_ui.number.call_count >= 1  # Number inputs
        assert mock_ui.date.call_count >= 1  # Date pickers
        assert mock_ui.time.call_count >= 1  # Time pickers

        # Verify action buttons
        button_calls = list(mock_ui.button.call_args_list)
        assert len(button_calls) >= 3  # Back button, Cancel, Submit
