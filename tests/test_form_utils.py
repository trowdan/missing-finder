"""Tests for form utilities"""

import pytest
from homeward.utils.form_utils import (
    sanitize_form_value,
    sanitize_form_data,
    get_sanitized_form_value,
)


class TestSanitizeFormValue:
    """Test the sanitize_form_value function"""

    def test_empty_string_returns_none(self):
        """Empty string should return None"""
        assert sanitize_form_value("") is None

    def test_whitespace_string_returns_none(self):
        """Whitespace-only string should return None"""
        assert sanitize_form_value("   ") is None
        assert sanitize_form_value("\t\n  ") is None

    def test_valid_string_returns_unchanged(self):
        """Valid string should return unchanged"""
        assert sanitize_form_value("John Doe") == "John Doe"
        assert sanitize_form_value("123 Main St") == "123 Main St"

    def test_none_returns_none(self):
        """None should return None"""
        assert sanitize_form_value(None) is None

    def test_non_string_returns_unchanged(self):
        """Non-string values should return unchanged"""
        assert sanitize_form_value(123) == 123
        assert sanitize_form_value(45.67) == 45.67
        assert sanitize_form_value(True) is True
        assert sanitize_form_value([1, 2, 3]) == [1, 2, 3]


class TestSanitizeFormData:
    """Test the sanitize_form_data function"""

    def test_empty_dict_returns_empty_dict(self):
        """Empty dictionary should return empty dictionary"""
        assert sanitize_form_data({}) == {}

    def test_sanitizes_all_values(self):
        """All values in dictionary should be sanitized"""
        input_data = {
            "name": "John Doe",
            "email": "",
            "phone": "   ",
            "height": "",
            "weight": "70",
            "age": 25,
        }
        expected = {
            "name": "John Doe",
            "email": None,
            "phone": None,
            "height": None,
            "weight": "70",
            "age": 25,
        }
        assert sanitize_form_data(input_data) == expected

    def test_preserves_valid_values(self):
        """Valid values should be preserved"""
        input_data = {
            "name": "Jane Smith",
            "address": "123 Oak Street",
            "postal_code": "K1A 0A6",
        }
        assert sanitize_form_data(input_data) == input_data


class TestGetSanitizedFormValue:
    """Test the get_sanitized_form_value function"""

    def test_existing_key_with_valid_value(self):
        """Should return sanitized value for existing key"""
        form_data = {"name": "John Doe", "email": ""}
        assert get_sanitized_form_value(form_data, "name") == "John Doe"
        assert get_sanitized_form_value(form_data, "email") is None

    def test_missing_key_returns_default(self):
        """Should return default for missing key"""
        form_data = {"name": "John Doe"}
        assert get_sanitized_form_value(form_data, "missing_key") is None
        assert get_sanitized_form_value(form_data, "missing_key", "default") == "default"

    def test_empty_string_with_default(self):
        """Empty string should return None, not default"""
        form_data = {"email": ""}
        assert get_sanitized_form_value(form_data, "email", "default@example.com") is None


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""

    def test_missing_person_form_data(self):
        """Test with realistic missing person form data"""
        form_data = {
            "name": "John",
            "surname": "Doe",
            "height": "",  # Optional field left empty
            "weight": "70",  # Optional field filled
            "hair_color": "   ",  # Optional field with whitespace
            "eye_color": "Brown",  # Optional field filled
            "postal_code": "",  # Optional field empty
            "medical_conditions": "",  # Optional field empty
        }

        sanitized = sanitize_form_data(form_data)

        # Required fields should be preserved
        assert sanitized["name"] == "John"
        assert sanitized["surname"] == "Doe"

        # Empty optional fields should become None
        assert sanitized["height"] is None
        assert sanitized["hair_color"] is None
        assert sanitized["postal_code"] is None
        assert sanitized["medical_conditions"] is None

        # Filled optional fields should be preserved
        assert sanitized["weight"] == "70"
        assert sanitized["eye_color"] == "Brown"

    def test_sighting_form_data(self):
        """Test with realistic sighting form data"""
        form_data = {
            "reporter_name": "Jane Smith",
            "reporter_email": "",  # Optional field empty
            "individual_height": "5'8\"",  # Optional field filled
            "individual_features": "",  # Optional field empty
            "clothing_accessories": "   ",  # Optional field with whitespace
            "additional_details": "",  # Optional field empty
        }

        sanitized = sanitize_form_data(form_data)

        # Required fields should be preserved
        assert sanitized["reporter_name"] == "Jane Smith"

        # Empty optional fields should become None
        assert sanitized["reporter_email"] is None
        assert sanitized["individual_features"] is None
        assert sanitized["clothing_accessories"] is None
        assert sanitized["additional_details"] is None

        # Filled optional fields should be preserved
        assert sanitized["individual_height"] == "5'8\""