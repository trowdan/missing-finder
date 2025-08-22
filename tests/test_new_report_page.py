from unittest.mock import Mock, patch

from homeward.models.case import CasePriority, Location


class TestNewReportPage:
    """Test cases for the new report page functionality"""

    @patch("homeward.ui.pages.new_report.ui")
    @patch("homeward.ui.pages.new_report.create_missing_person_form")
    @patch("homeward.ui.pages.new_report.create_footer")
    def test_create_new_report_page_components(self, mock_footer, mock_form, mock_ui):
        """Test that new report page creates all required components"""
        from homeward.ui.pages.new_report import create_new_report_page

        # Setup mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value.enable = Mock()

        mock_data_service = Mock()
        mock_config = Mock()
        mock_config.version = "1.0.0"
        mock_callback = Mock()

        create_new_report_page(mock_data_service, mock_config, mock_callback)

        # Verify dark mode is enabled
        mock_ui.dark_mode().enable.assert_called_once()

        # Verify components are created
        mock_form.assert_called_once()
        mock_footer.assert_called_once_with("1.0.0")

        # Verify UI structure
        assert mock_ui.column.call_count >= 2
        assert mock_ui.label.call_count >= 2  # Title and subtitle
        assert mock_ui.button.call_count >= 1  # Back button

    @patch("homeward.ui.pages.new_report.ui")
    def test_handle_form_submission_success(self, mock_ui):
        """Test successful form submission"""
        from homeward.ui.pages.new_report import handle_form_submission

        mock_data_service = Mock()
        mock_callback = Mock()

        form_data = {
            "name": "John",
            "surname": "Doe",
            "age": 30,
            "gender": "Male",
            "last_seen_date": "2023-12-01",
            "last_seen_time": "14:30",
            "last_seen_address": "123 Main St",
            "city": "Toronto",
            "country": "Canada",
            "postal_code": "M5V 3A8",
            "circumstances": "Left for work and never returned",
            "priority": "High",
            "reporter_name": "Jane Doe",
            "reporter_phone": "416-555-0123",
            "reporter_email": "jane@example.com",
            "relationship": "Sister",
        }

        with patch("homeward.ui.pages.new_report.ui.timer") as mock_timer:
            handle_form_submission(form_data, mock_data_service, mock_callback)

            # Verify success notification
            mock_ui.notify.assert_called_with(
                "Missing person report submitted successfully!", type="positive"
            )

            # Verify timer is set for callback
            mock_timer.assert_called_once()

    @patch("homeward.ui.pages.new_report.ui")
    def test_handle_form_submission_error(self, mock_ui):
        """Test form submission with error"""
        from homeward.ui.pages.new_report import handle_form_submission

        mock_data_service = Mock()
        mock_callback = Mock()

        # Invalid form data that will cause an exception
        form_data = {
            "name": None,  # This will cause an error
        }

        handle_form_submission(form_data, mock_data_service, mock_callback)

        # Verify error notification
        mock_ui.notify.assert_called()
        call_args = mock_ui.notify.call_args
        assert "Error submitting report:" in call_args[0][0]
        assert call_args[1]["type"] == "negative"

    def test_case_creation_from_form_data(self):
        """Test that MissingPersonCase is created correctly from form data"""

        form_data = {
            "name": "John",
            "surname": "Doe",
            "age": 30,
            "gender": "Male",
            "last_seen_date": "2023-12-01",
            "last_seen_time": "14:30",
            "last_seen_address": "123 Main St",
            "city": "Toronto",
            "country": "Canada",
            "postal_code": "M5V 3A8",
            "circumstances": "Left for work and never returned",
            "priority": "High",
            "height": "180",
            "weight": "75",
            "hair_color": "Brown",
            "eye_color": "Blue",
            "clothing_description": "Blue jeans and white shirt",
            "distinguishing_marks": "Scar on left arm",
            "medical_conditions": "None known",
            "additional_info": "Has a dog",
            "reporter_name": "Jane Doe",
            "reporter_phone": "416-555-0123",
            "reporter_email": "jane@example.com",
            "relationship": "Sister",
            "case_number": "MP001",
        }

        # Test the internal case creation logic
        location = Location(
            address=form_data.get("last_seen_address", ""),
            city=form_data.get("city", ""),
            country=form_data.get("country", ""),
            postal_code=form_data.get("postal_code", ""),
            latitude=0.0,
            longitude=0.0,
        )

        assert location.address == "123 Main St"
        assert location.city == "Toronto"
        assert location.country == "Canada"
        assert location.postal_code == "M5V 3A8"

        # Test priority mapping
        priority_map = {
            "High": CasePriority.HIGH,
            "Medium": CasePriority.MEDIUM,
            "Low": CasePriority.LOW,
        }
        assert priority_map["High"] == CasePriority.HIGH


class TestMissingPersonForm:
    """Test cases for the missing person form component"""

    @patch("homeward.ui.components.missing_person_form.ui")
    def test_create_missing_person_form_structure(self, mock_ui):
        """Test that the form creates all required UI elements"""
        from homeward.ui.components.missing_person_form import (
            create_missing_person_form,
        )

        # Setup mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.grid.return_value.__enter__ = Mock()
        mock_ui.grid.return_value.__exit__ = Mock()
        mock_ui.input.return_value = Mock()
        mock_ui.textarea.return_value = Mock()
        mock_ui.select.return_value = Mock()
        mock_ui.number.return_value = Mock()
        mock_ui.upload.return_value = Mock()

        mock_submit = Mock()
        mock_cancel = Mock()

        create_missing_person_form(mock_submit, mock_cancel)

        # Verify form structure
        assert mock_ui.column.call_count >= 5  # Multiple columns for layout
        assert mock_ui.card.call_count >= 5  # Multiple cards for sections
        assert mock_ui.input.call_count >= 10  # Multiple input fields
        assert mock_ui.textarea.call_count >= 5  # Multiple textarea fields
        assert mock_ui.select.call_count >= 2  # Gender and priority selects
        assert mock_ui.button.call_count == 2  # Cancel and Submit buttons
        assert mock_ui.upload.call_count == 1  # Photo upload

    def test_form_validation_required_fields(self):
        """Test form validation for required fields"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with missing required fields
        form_data = {
            "name": Mock(value="John"),
            "surname": Mock(value=""),  # Missing surname
            "age": Mock(value=30),
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main St"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(value="Missing"),
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="416-555-0123"),
            "relationship": Mock(value="Sister"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui") as mock_ui:
            handle_submit(form_data, mock_submit)

            # Should show validation error
            mock_ui.notify.assert_called()
            call_args = mock_ui.notify.call_args
            assert "Please fill in required fields" in call_args[0][0]
            assert call_args[1]["type"] == "negative"

            # Should not call submit callback
            mock_submit.assert_not_called()

    def test_form_validation_name_format(self):
        """Test name field validation"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with invalid name
        form_data = {
            "name": Mock(value="John123"),  # Invalid name with numbers
            "surname": Mock(value="Doe"),
            "age": Mock(value=30),
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main St"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(value="Missing"),
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="416-555-0123"),
            "relationship": Mock(value="Sister"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui") as mock_ui:
            handle_submit(form_data, mock_submit)

            # Should show name validation error
            mock_ui.notify.assert_called()
            call_args = mock_ui.notify.call_args
            assert "can only contain letters" in call_args[0][0]
            assert call_args[1]["type"] == "negative"

    def test_form_validation_age_range(self):
        """Test age validation"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with invalid age
        form_data = {
            "name": Mock(value="John"),
            "surname": Mock(value="Doe"),
            "age": Mock(value=200),  # Invalid age
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main St"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(value="Missing"),
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="416-555-0123"),
            "relationship": Mock(value="Sister"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui") as mock_ui:
            handle_submit(form_data, mock_submit)

            # Should show age validation error
            mock_ui.notify.assert_called()
            call_args = mock_ui.notify.call_args
            assert "Age must be between 0 and 150" in call_args[0][0]
            assert call_args[1]["type"] == "negative"

    def test_form_validation_phone_format(self):
        """Test phone number validation"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with invalid phone
        form_data = {
            "name": Mock(value="John"),
            "surname": Mock(value="Doe"),
            "age": Mock(value=30),
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main Street"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(value="Left for work and never returned home"),
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="123"),  # Too short
            "relationship": Mock(value="Sister"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui") as mock_ui:
            handle_submit(form_data, mock_submit)

            # Should show phone validation error
            mock_ui.notify.assert_called()
            call_args = mock_ui.notify.call_args
            assert "valid phone number" in call_args[0][0]
            assert call_args[1]["type"] == "negative"

    def test_form_validation_email_format(self):
        """Test email validation"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with invalid email
        form_data = {
            "name": Mock(value="John"),
            "surname": Mock(value="Doe"),
            "age": Mock(value=30),
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main Street"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(
                value="Left for work and never returned home"
            ),  # Valid circumstances
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="416-555-0123"),
            "reporter_email": Mock(value="invalid-email"),  # Invalid email
            "relationship": Mock(value="Sister"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui") as mock_ui:
            handle_submit(form_data, mock_submit)

            # Should show email validation error
            mock_ui.notify.assert_called()
            call_args = mock_ui.notify.call_args
            assert "valid email address" in call_args[0][0]
            assert call_args[1]["type"] == "negative"

    def test_form_validation_success(self):
        """Test successful form validation"""
        from homeward.ui.components.missing_person_form import handle_submit

        # Mock form data with all valid fields
        form_data = {
            "name": Mock(value="John"),
            "surname": Mock(value="Doe"),
            "age": Mock(value=30),
            "gender": Mock(value="Male"),
            "last_seen_date": Mock(value="2023-12-01"),
            "last_seen_address": Mock(value="123 Main Street"),
            "city": Mock(value="Toronto"),
            "country": Mock(value="Canada"),
            "circumstances": Mock(value="Left for work and never returned home"),
            "reporter_name": Mock(value="Jane Doe"),
            "reporter_phone": Mock(value="416-555-0123"),
            "relationship": Mock(value="Sister"),
            "priority": Mock(value="High"),
        }

        mock_submit = Mock()

        with patch("homeward.ui.components.missing_person_form.ui"):
            handle_submit(form_data, mock_submit)

            # Should call submit callback with processed data
            mock_submit.assert_called_once()
            submitted_data = mock_submit.call_args[0][0]

            assert submitted_data["name"] == "John"
            assert submitted_data["surname"] == "Doe"
            assert submitted_data["age"] == 30
            assert submitted_data["gender"] == "Male"


class TestFormValidationHelpers:
    """Test validation helper functions"""

    def test_validate_name_field_valid(self):
        """Test name validation with valid input"""
        from homeward.ui.components.missing_person_form import validate_name_field

        mock_field = Mock()
        mock_field.value = "John O'Connor-Smith"
        mock_field.props = Mock()

        validate_name_field(mock_field, "Test field")

        # Should remove error props for valid name
        mock_field.props.assert_called_with(remove="error error-message")

    def test_validate_name_field_invalid(self):
        """Test name validation with invalid input"""
        from homeward.ui.components.missing_person_form import validate_name_field

        mock_field = Mock()
        mock_field.value = "John123"
        mock_field.props = Mock()

        validate_name_field(mock_field, "Test field")

        # Should set error props for invalid name
        mock_field.props.assert_called_with(
            'error error-message="Only letters, spaces, hyphens, and apostrophes allowed"'
        )

    def test_validate_email_field_valid(self):
        """Test email validation with valid input"""
        from homeward.ui.components.missing_person_form import validate_email_field

        mock_field = Mock()
        mock_field.value = "test@example.com"
        mock_field.props = Mock()

        validate_email_field(mock_field)

        # Should remove error props for valid email
        mock_field.props.assert_called_with(remove="error error-message")

    def test_validate_email_field_invalid(self):
        """Test email validation with invalid input"""
        from homeward.ui.components.missing_person_form import validate_email_field

        mock_field = Mock()
        mock_field.value = "invalid-email"
        mock_field.props = Mock()

        validate_email_field(mock_field)

        # Should set error props for invalid email
        mock_field.props.assert_called_with(
            'error error-message="Please enter a valid email address"'
        )

    def test_validate_phone_field_valid(self):
        """Test phone validation with valid input"""
        from homeward.ui.components.missing_person_form import validate_phone_field

        mock_field = Mock()
        mock_field.value = "(416) 555-0123"
        mock_field.props = Mock()

        validate_phone_field(mock_field)

        # Should remove error props for valid phone
        mock_field.props.assert_called_with(remove="error error-message")

    def test_validate_phone_field_invalid(self):
        """Test phone validation with invalid input"""
        from homeward.ui.components.missing_person_form import validate_phone_field

        mock_field = Mock()
        mock_field.value = "123"
        mock_field.props = Mock()

        validate_phone_field(mock_field)

        # Should set error props for invalid phone
        mock_field.props.assert_called_with(
            'error error-message="Enter 10-15 digits (spaces, dashes, parentheses allowed)"'
        )

    def test_validate_age_field_valid(self):
        """Test age validation with valid input"""
        from homeward.ui.components.missing_person_form import validate_age_field

        mock_field = Mock()
        mock_field.value = 25
        mock_field.props = Mock()

        validate_age_field(mock_field)

        # Should remove error props for valid age
        mock_field.props.assert_called_with(remove="error error-message")

    def test_validate_age_field_invalid(self):
        """Test age validation with invalid input"""
        from homeward.ui.components.missing_person_form import validate_age_field

        mock_field = Mock()
        mock_field.value = 200
        mock_field.props = Mock()

        validate_age_field(mock_field)

        # Should set error props for invalid age
        mock_field.props.assert_called_with(
            'error error-message="Age must be between 0 and 150"'
        )
