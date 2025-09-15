"""
Test to verify the form validation bug fix.
"""

import pytest
from src.homeward.models.form_mappers import SightingFormValidator


class TestFormValidationFix:
    """Test to verify the validation bug is fixed"""

    def test_validation_with_realistic_user_data_should_pass(self):
        """Test that realistic user data now passes validation"""

        # Simulate exactly what a user would input on the form
        realistic_form_data = {
            # Date section
            "sighting_date": "2023-12-01",
            "sighting_time": "14:30",

            # Location section
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "sighting_postal": "M5V 1J3",

            # Reporter section
            "reporter_name": "John Doe",
            "reporter_email": "john@example.com",

            # Individual description
            "individual_age": "25",
            "individual_gender": "Male",
            "individual_height": "5'10\"",

            # Confidence level (user DID fill this) - using the correct form field name
            "confidence": "High - Clear view, good lighting, close distance",

            # Source type (user DID fill this)
            "source_type": "Witness - I personally saw this person",

            # Additional details (this should be recognized as description)
            "additional_details": "I saw the person walking near the park around 2:30 PM. They were wearing a blue jacket and seemed to match the description of the missing person."
        }

        # Run validation
        missing_fields = SightingFormValidator.validate_required_fields(realistic_form_data)

        print(f"\n=== VALIDATION FIX TEST ===")
        print(f"User filled {len(realistic_form_data)} fields")
        print(f"Missing fields reported: {missing_fields}")
        print(f"Required fields: {SightingFormValidator.get_required_fields()}")

        # This should now pass with no missing fields
        assert len(missing_fields) == 0, f"Expected no missing fields, but got: {missing_fields}"

    def test_validation_with_missing_confidence_shows_correct_error(self):
        """Test that when confidence is actually missing, we get the right error message"""

        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "additional_details": "I saw the person",
            "source_type": "Witness - I personally saw this person",
            # "confidence" is intentionally missing
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)

        print(f"\n=== MISSING CONFIDENCE TEST ===")
        print(f"Missing fields: {missing_fields}")

        assert "Confidence Level" in missing_fields
        assert len(missing_fields) == 1

    def test_validation_with_missing_description_shows_correct_error(self):
        """Test that when description is actually missing, we get the right error message"""

        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "confidence": "High - Clear view, good lighting, close distance",
            "source_type": "Witness - I personally saw this person",
            # "additional_details" is intentionally missing
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)

        print(f"\n=== MISSING DESCRIPTION TEST ===")
        print(f"Missing fields: {missing_fields}")

        assert "Sighting Description" in missing_fields
        assert len(missing_fields) == 1

    def test_required_fields_match_form_fields(self):
        """Test that required fields exactly match what the form provides"""

        required_fields = SightingFormValidator.get_required_fields()

        # These should be the form field names, not SQL column names
        expected_form_fields = [
            "sighting_date",
            "sighting_address",
            "sighting_city",
            "sighting_country",
            "additional_details",  # Form field for description
            "confidence",          # Form field for confidence_level
            "source_type"
        ]

        print(f"\n=== FIELD MAPPING CHECK ===")
        print(f"Required fields: {required_fields}")
        print(f"Expected fields: {expected_form_fields}")

        assert set(required_fields) == set(expected_form_fields), \
            f"Required fields don't match expected form fields. Missing: {set(expected_form_fields) - set(required_fields)}, Extra: {set(required_fields) - set(expected_form_fields)}"

    def test_edge_case_empty_strings_should_fail_validation(self):
        """Test that empty strings are treated as missing fields"""

        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "additional_details": "",  # Empty string should fail
            "confidence": "High - Clear view, good lighting, close distance",
            "source_type": "Witness - I personally saw this person"
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)

        print(f"\n=== EMPTY STRING TEST ===")
        print(f"Missing fields: {missing_fields}")

        assert "Sighting Description" in missing_fields

    def test_edge_case_none_values_should_fail_validation(self):
        """Test that None values are treated as missing fields"""

        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "additional_details": "I saw the person",
            "confidence": None,  # None should fail
            "source_type": "Witness - I personally saw this person"
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)

        print(f"\n=== NONE VALUE TEST ===")
        print(f"Missing fields: {missing_fields}")

        assert "Confidence Level" in missing_fields


if __name__ == "__main__":
    # Run the tests to verify the fix
    test = TestFormValidationFix()
    test.test_validation_with_realistic_user_data_should_pass()
    test.test_validation_with_missing_confidence_shows_correct_error()
    test.test_validation_with_missing_description_shows_correct_error()
    test.test_required_fields_match_form_fields()
    test.test_edge_case_empty_strings_should_fail_validation()
    test.test_edge_case_none_values_should_fail_validation()